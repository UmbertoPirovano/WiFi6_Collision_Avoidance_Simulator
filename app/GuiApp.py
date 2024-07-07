import io
import os
import tkinter as tk
import customtkinter
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import airsim

from Gui.MessageWindow import MessageWindow
from Gui.SettingsWindow import SettingsWindow
from Gui.ScenarioEditorWindow import ScenarioEditorWindow
from simulator import AirSimCarSimulation

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        self.ip_address = ""
        self.output_directory = './run/'
        self.scenarios = {}

        # configure window
        self.title("Wifi-6 Simulator")
        self.geometry(f"{1244}x{780}")
        self.resizable(False, False)
        # initialize secondary windows
        self.toplevel_window = None
        self.message_window = None
        self.scenario_editor_window = None

        # keep track of after callbacks
        self.after_callbacks = []

        # General styling
        self.radius = 10
        self.font = customtkinter.CTkFont(size=12, weight="bold")
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Gui/asset")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # SIDEBAR FRAME
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=self.radius)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        #self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="802.11ax\n\nCollision\navoidance\nsimulator", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon.png")), size=(130, 130)))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        self.settings_button = customtkinter.CTkButton(self.sidebar_frame, command=self.open_settingsWindow)
        self.settings_button.grid(row=1, column=0, padx=20, pady=10)
        self.settings_button.configure(text="Settings")
        self.scenario_label = customtkinter.CTkLabel(self.sidebar_frame, text="Select scenario:", font=self.font)
        self.scenario_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.add_scenario_button = customtkinter.CTkButton(self.sidebar_frame, text="Add scenario", command=self.open_add_scenario_window)
        self.add_scenario_button.grid(row=3, column=0, padx=20, pady=10)
        self.scenario_optionMenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["car", "fence"])
        self.scenario_optionMenu.grid(row=4, column=0, padx=20, pady=10)
        self.scenario_optionMenu.set("car")
        self.throttle_label = customtkinter.CTkLabel(self.sidebar_frame, text="Throttle:", font=self.font)
        self.throttle_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.throttle_entry = customtkinter.CTkEntry(self.sidebar_frame)
        self.throttle_entry.grid(row=6, column=0, padx=20, pady=10)
        self.throttle_entry.insert(0, "0.5")
        self.run_button = customtkinter.CTkButton(self.sidebar_frame, command=self.run_button_event, fg_color="green", hover_color="darkgreen")
        self.run_button.grid(row=7, column=0, padx=20, pady=10)
        self.run_button.configure(text="RUN")
        self.about_button = customtkinter.CTkButton(self.sidebar_frame, command=self.open_aboutWindow)
        self.about_button.grid(row=9, column=0, padx=20, pady=(10,20))
        self.about_button.configure(text="About")

        # INPUT FRAME
        self.input_frame = customtkinter.CTkFrame(self, corner_radius=self.radius)
        self.input_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 10), sticky="nsew", rowspan=3)
        self.input_frame.grid_rowconfigure(9, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)

        # CV PARAMETERS
        self.cvlabel = customtkinter.CTkLabel(self.input_frame, text="Cv model parameters:", font=self.font)
        self.cvlabel.grid(row=0, column=0, columnspan=1, pady=(20,10))
        self.info_button_cv = customtkinter.CTkButton(self.input_frame, text="info", font=self.font, command=self.open_cvInfoWindow)
        self.info_button_cv.grid(row=0, column=1, pady=(20,10))

        # CV Model
        self.option1 = customtkinter.CTkLabel(self.input_frame, text="CV model:", font=self.font)
        self.option1.grid(row=1, column=0, padx=20, pady=(10, 10))

        self.optionmenu_1 = customtkinter.CTkComboBox(self.input_frame, values=["Superlight", "Light", "Medium", "Heavy"], state="readonly")
        self.optionmenu_1.grid(row=1, column=1, padx=20, pady=(10, 10))
        self.optionmenu_1.set("Light")

        # Image Format
        self.option2 = customtkinter.CTkLabel(self.input_frame, text="Image Format:", font=self.font)
        self.option2.grid(row=2, column=0, padx=20, pady=(10, 10))

        self.optionmenu_2 = customtkinter.CTkComboBox(self.input_frame, values=["JPEG", "PNG"], state="readonly")
        self.optionmenu_2.grid(row=2, column=1, padx=20, pady=(10, 10))
        self.optionmenu_2.set("JPEG")

        # GPU Selection
        self.gpu_label = customtkinter.CTkLabel(self.input_frame, text="GPU Selection:", font=self.font)
        self.gpu_label.grid(row=3, column=0, padx=20, pady=(10, 10))

        self.gpu_var = tk.StringVar(value='device')
        self.gpu_combobox = customtkinter.CTkComboBox(self.input_frame, values=["device", "virtual"], state="readonly", variable=self.gpu_var, command=self.update_gpu_info)
        self.gpu_combobox.grid(row=3, column=1, padx=20, pady=(10, 10))
        self.gpu_combobox.set("device")

        # Virtual GPU Entry
        self.virtual_label = customtkinter.CTkLabel(self.input_frame, text="Inference interval [s]:", font=self.font)
        self.virtual_label.grid(row=4, column=0, padx=20, pady=(10, 10))
        self.virtual_entry = customtkinter.CTkEntry(self.input_frame)
        self.virtual_entry.bind('<Return>', self.parse_float_entry)
        self.virtual_entry.configure(state="disabled")
        self.virtual_entry.grid(row=4, column=1, padx=20, pady=(10, 10))

        # CHANNEL PARAMETERS
        self.label_fr = customtkinter.CTkLabel(self.input_frame, text="Channel parameters:", font=self.font)
        self.label_fr.grid(row=5, column=0, padx=20, pady=(10, 10))
        self.info_button_channel = customtkinter.CTkButton(self.input_frame, text="info", font=self.font, command=self.open_channelInfoWindow)
        self.info_button_channel.grid(row=5, column=1, padx=20, pady=(10, 10))
        # Bandwidth
        self.bandwidth = customtkinter.CTkLabel(self.input_frame, text="Bandwidth [MHz]:", font=self.font)
        self.bandwidth.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.bandwidth_values = customtkinter.CTkComboBox(self.input_frame, values=["20", "40", "80", "160"], state="readonly")
        self.bandwidth_values.grid(row=7, column=1, padx=20, pady=(10, 10))
        self.bandwidth_values.set("20")

        # Central frequency
        self.central_frequency = customtkinter.CTkLabel(self.input_frame, text="Central frequency [GHz]:", font=self.font)
        self.central_frequency.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.frequency_values = customtkinter.CTkComboBox(self.input_frame, values=["2.4", "5"], state="readonly", command=self.update_bandwidth_values)
        self.frequency_values.grid(row=6, column=1, padx=20, pady=(10, 10))
        self.frequency_values.set("5")

        # Transmitted power
        self.ptx = customtkinter.CTkLabel(self.input_frame, text="Ptx [dBm]:", font=self.font)
        self.ptx.grid(row=8, column=0, padx=20, pady=(10, 10))
        self.ptx_values = customtkinter.CTkComboBox(self.input_frame, values=["20", "25", "30"], state="readonly")
        self.ptx_values.grid(row=8, column=1, padx=20, pady=(10, 10))
        self.ptx_values.set("20")

        # LOGBOX
        self.textbox = customtkinter.CTkTextbox(self, width=200, height=250, font=self.font, corner_radius=self.radius)
        self.textbox.grid(row=3, column=1, padx=(20, 0), pady=(0, 20), sticky="nsew")
        self.textbox.insert(index="0.0", text="Welcome! If needed, remember to set AirSim's IP in Settings!\n\nSimulation output:\n")
        self.textbox.configure(state="disabled")

        # SIDE IMAGES
        # TABVIEW
        self.image_tabview = customtkinter.CTkTabview(self, corner_radius=self.radius, width=533)
        self.image_tabview.grid(row=0, column=3, padx=(20, 20), pady=(10, 20), sticky="nsew", rowspan=4)
        self.image_tabview.add("Overview")
        self.image_tabview.tab("Overview").grid_rowconfigure(0, weight=1)
        self.image_tabview.tab("Overview").grid_rowconfigure((1,2), weight=2)
        self.image_tabview.add("Latency")
        self.image_tabview.tab("Latency").grid_rowconfigure((0,1,2,3), weight=1)
        self.latency_tab_scrollable = customtkinter.CTkScrollableFrame(self.image_tabview.tab("Latency"), width=533)
        self.latency_tab_scrollable.grid(row=0, column=0, padx=20, pady=5, sticky="nsew", rowspan=4)
        self.latency_tab_scrollable.grid_rowconfigure((0,1,2,3), weight=1)
        self.latency_tab_scrollable.bind_all("<Button-4>", lambda e: self.latency_tab_scrollable._parent_canvas.yview("scroll", -1, "units"))
        self.latency_tab_scrollable.bind_all("<Button-5>", lambda e: self.latency_tab_scrollable._parent_canvas.yview("scroll", 1, "units"))
        # TAB OVERVIEW
        self.label_img = customtkinter.CTkLabel(self.image_tabview.tab("Overview"), text="Last Segmented Image", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_img.grid(row=0, column=0, padx=20, pady=5)
        self.segmented_image = customtkinter.CTkLabel(self.image_tabview.tab("Overview"), text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "cv_placeholder.png")), size=(533, 300)))
        self.segmented_image.grid(row=1, column=0, padx=20, pady=5)
        self.plot_speed = customtkinter.CTkLabel(self.image_tabview.tab("Overview"), text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300)))
        self.plot_speed.grid(row=2, column=0, padx=20, pady=5)
        self.set_plot(self.plot_speed, [0, 0, 0, 0, 0], 'Speed')
        # TAB LATENCY
        self.plot_capture = customtkinter.CTkLabel(self.latency_tab_scrollable, text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300)))
        self.plot_capture.grid(row=0, column=0, padx=0, pady=5)
        self.set_plot(self.plot_capture, [0, 0, 0, 0, 0], 'Capture Latency')
        self.plot_transmission = customtkinter.CTkLabel(self.latency_tab_scrollable, text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300)))
        self.plot_transmission.grid(row=1, column=0, padx=0, pady=5)
        self.set_plot(self.plot_transmission, [0, 0, 0, 0, 0], 'Transmission Latency')
        self.plot_inference = customtkinter.CTkLabel(self.latency_tab_scrollable, text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300)))
        self.plot_inference.grid(row=2, column=0, padx=0, pady=5)
        self.set_plot(self.plot_inference, [0, 0, 0, 0, 0], 'Inference Latency')
        self.plot_overall = customtkinter.CTkLabel(self.latency_tab_scrollable, text="", image=customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300)))
        self.plot_overall.grid(row=3, column=0, padx=0, pady=5)
        self.set_plot(self.plot_overall, [0, 0, 0, 0, 0], 'Overall Latency')

        # Close event bindings
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_bandwidth_values(self, event=None):
        selected_frequency = self.frequency_values.get()
        if selected_frequency == '2.4':
            self.bandwidth_values.configure(values=["20", "40"])
        elif selected_frequency == '5':
            self.bandwidth_values.configure(values=["20", "40", "80", "160"])
        self.bandwidth_values.set("20")  # Default to 20 MHz if previously selected bandwidth is not available

    def set_image(self):
        view_files = sorted(os.listdir(os.path.join(self.output_directory, 'processed/vis')))
        vis_path = os.path.join(self.output_directory, 'processed/vis', view_files[-1])
        self.img1 = customtkinter.CTkImage(Image.open(vis_path), size=(533, 300))
        self.segmented_image.configure(image=self.img1)
        print(f"GUI>> Image loaded: {vis_path}")

    def set_plot(self, plot, Total_lat, label=''):
        if label != "Speed":
            Total_lat = np.array(Total_lat) * 1000  # Convert to milliseconds

        # Desired pixel dimensions
        pixel_width = 533
        pixel_height = 370

        # Convert pixels to inches (default DPI is 100)
        inch_width = pixel_width / 100
        inch_height = pixel_height / 100

        # Create the figure and axis with the specified size
        plt.close('all')
        fig, ax = plt.subplots(figsize=(inch_width, inch_height))

        # Define custom colors
        line_color = '#00bcd4'  # Cyan color for the stems
        marker_color = '#ff4081'  # Magenta color for the markers
        base_color = '#ffeb3b'  # Yellow color for the base lines
        background_color = '#2b2b2b'  # Dark gray background color
        grid_color = '#d3d3d3'  # Light gray grid color
        text_color = '#ffffff'  # White text color

        # Set the background color
        ax.set_facecolor(background_color)
        fig.patch.set_facecolor(background_color)

        # Create a lollipop plot with custom colors
        markerline, stemlines, baseline = ax.stem(range(len(Total_lat)), Total_lat)

        # Set custom colors for the plot elements
        plt.setp(markerline, 'markerfacecolor', marker_color, 'markeredgecolor', marker_color)
        plt.setp(stemlines, 'color', line_color)
        #plt.setp(baseline, 'color', base_color)

        # Customize the plot
        if label != '':
            ax.set_title(label, fontsize=14, fontweight='bold', color=text_color)
        ax.set_xlabel('Inference', fontsize=12, color=text_color)
        ax.set_ylabel('Latency (ms)', fontsize=12, color=text_color)
        ax.set_ylim(max(min(Total_lat)-100, 0), max(Total_lat) + max(Total_lat) * 0.1)
        ax.grid(True, linestyle='--', linewidth=0.7, color=grid_color, alpha=0.7)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        # Set the color of ticks
        ax.tick_params(axis='both', which='both', colors=text_color)

        # Customize the plot layout to prevent labels from being cut off
        plt.tight_layout()

        # Save the plot to a BytesIO buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        # Open the image from the buffer using PIL
        img = Image.open(buf)

        # Convert PIL image to customtkinter CTkImage
        ctk_image = customtkinter.CTkImage(light_image=img, size=(pixel_width, pixel_height))

        # Update the label with the new image
        plot.configure(image=ctk_image)
        plot.image = ctk_image  # Keep a reference to avoid garbage collection

        # Close the buffer
        buf.close()

    def update_plots(self, times, speeds):
        # Update the plots with the new data
        # Update speed plot
        self.set_plot(self.plot_speed, speeds, 'Speed')
        # Update latency plots
        overall_time = [sum(x) for x in zip(*times.values())]
        times['Total_lat'] = overall_time
        self.set_plot(self.plot_overall,times.get('Total_lat'), 'Overall Latency')
        self.set_plot(self.plot_capture,times.get('capture'), 'Capture Latency')
        self.set_plot(self.plot_transmission,times.get('tx'), 'Transmission Latency')
        self.set_plot(self.plot_inference,times.get('inference'), 'Inference Latency')
    
    def update_gui(self, times, speeds):
        # times is a dictionary containing the times for each step
        self.set_image()
        self.update_plots(times, speeds)
        self.update()

    def add_scenario(self, name):
        tmp_airsim = airsim.CarClient(ip=self.ip_address)
        tmp_airsim.confirmConnection()
        car_state = tmp_airsim.getCarState()
        position = [
            car_state.kinematics_estimated.position.x_val,
            car_state.kinematics_estimated.position.y_val,
            car_state.kinematics_estimated.position.z_val
        ]
        orientation = [
            car_state.kinematics_estimated.orientation.w_val,
            car_state.kinematics_estimated.orientation.x_val,
            car_state.kinematics_estimated.orientation.y_val,
            car_state.kinematics_estimated.orientation.z_val
        ]
        self.scenarios[name] = {
            "position": position,
            "orientation": orientation
        }
        self.print_to_logbox(f"Added scenario: {name} at position {position} with orientation {orientation}")
        self.scenario_optionMenu.configure(values=["car", "fence"] + list(self.scenarios.keys()))


    def set_ip_address(self, ip):
        self.ip_address = ip
        self.print_to_logbox(f"IP address set to: {ip}")

    def set_output_directory(self, directory):
        self.output_directory = directory
        self.print_to_logbox(f"Output directory set to: {directory}")

    def update_gpu_info(self, event=None):
        selected_gpu = self.gpu_var.get()
        if selected_gpu == "device":
            self.virtual_entry.delete(0, tk.END)
            self.virtual_entry.configure(state="disabled")
        else:
            self.virtual_entry.configure(state="normal")

    def parse_float_entry(self, event=None):
        try:
            float(self.virtual_entry.get())
        except ValueError:
            self.virtual_entry.delete(0, tk.END)
            self.virtual_entry.insert(0, "")

    def validate_input(self):
        self.cv_mode = self.optionmenu_1.get()
        self.image_format = self.optionmenu_2.get()
        self.gpu = self.gpu_var.get()
        self.inference_time = self.virtual_entry.get() if self.gpu == "virtual" else None
        self.channel_params = [int(self.bandwidth_values.get()) * 1e6, float(self.frequency_values.get()), int(self.ptx_values.get())]
        self.target_throttle = float(self.throttle_entry.get())
        self.print_to_logbox(f"Selected CV model: {self.cv_mode}")
        self.print_to_logbox(f"Selected image format: {self.image_format}")
        self.print_to_logbox(f"Selected GPU: {self.gpu}")
        if self.gpu == "virtual":
            self.print_to_logbox(f"Selected inference time: {self.inference_time}")
        self.print_to_logbox(f"Selected channel parameters: {self.channel_params}")

    def run_button_event(self):
        self.print_to_logbox("Starting simulation...")
        try:
            self.validate_input()
            simulation = AirSimCarSimulation(
                gui=self,
                client_ip=self.ip_address,
                directory = self.output_directory,
                cv_mode=self.cv_mode,
                inf_time=int(self.inference_time) if self.inference_time is not None else None,
                channel_params=self.channel_params,
                image_format=self.image_format,
                image_quality=80,
                decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]},
                target_throttle=self.target_throttle
            )
            for scenario in self.scenarios:
                simulation.add_scenario(name=scenario, position=self.scenarios[scenario]["position"], orientation=self.scenarios[scenario]["orientation"])
            fail = simulation.run_simulation(obstacle=self.scenario_optionMenu.get())
            self.print_to_logbox("Scenario 1 completed:" + (" Collision detected." if fail else " No collision detected."))
            self.print_to_logbox("Simulation completed.\n")
        except Exception as e:
            self.print_to_logbox(f"Error during simulation: {e}\n")

    def print_to_logbox(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert(index="end", text=f"\n{text}")
        self.textbox.configure(state="disabled")

    def open_aboutWindow(self):
        text = "Wifi-6 Collision Avoidance Simulator\n\nVersion: 2.0 - July 2024\n\nAuthors:\n\n- Umberto Pirovano\n- Andrea Paternò\n- Andrea Conese\n- Hamze Ghorbani Koujani\n\n"
        self.open_message_window(text)

    def open_cvInfoWindow(self):
        text = "CV INFO:\n\n"\
              "-Cv model: \nit is possible to choose among different proposed models that have different performances\n\n"\
              "-Image format: \nthe format used to retrieve images from AirSim. It is possible to choose between JPEG (80% quality) or PNG (100% quality)\n\n"\
              "-GPU selection: \nDEVICE performs inference real-time and performances may vary depending on the hardware. \nVIRTUAL performs inference pausing the simulation every n seconds, where n is the value set in the 'Inference interval' entry\n\n"
        self.open_message_window(text)

    def open_channelInfoWindow(self):
        cv_text = "CHANNEL INFO:\n\n"\
          "- Central frequency: \nwi-fi 6 can work in two main carriers: 2.4 GHz or 5 GHz\n"\
          "!!! If 2.4 GHz is chosen as central frequency only 20,40 MHz bandwidths will be available, because the total available bandwidth is 60 MHz\n"\
          "!!! If 5 GHz is chosen as central frequency only 20,40,80,160 MHz bandwidths will be available, because the total available bandwidth is 500 MHz\n\n"\
          "- Bandwidth: \nspacing between the channel, higher is the value lower will be the transmission time of the image but with a trade off with the number of users possible\n\n"\
          "- Ptx: \nTransmitted power values assuming different types of transmitters"

        self.open_message_window(cv_text)

    def open_message_window(self, text):
        if self.message_window is None or not self.message_window.winfo_exists():
            self.message_window = MessageWindow(text=text)  # create window if its None or destroyed
            self.message_window.protocol("WM_DELETE_WINDOW", self.on_message_window_close)
        self.message_window.wait_visibility()
        self.message_window.focus()
        self.message_window.grab_set()

    def open_settingsWindow(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = SettingsWindow(self)  # create window if its None or destroyed
            self.toplevel_window.protocol("WM_DELETE_WINDOW", self.on_settings_window_close)
        self.toplevel_window.wait_visibility()
        self.toplevel_window.focus()
        self.toplevel_window.grab_set()

    def open_add_scenario_window(self):
        if self.scenario_editor_window is None or not self.scenario_editor_window.winfo_exists():
            self.scenario_editor_window = ScenarioEditorWindow(self)  # create window if its None or destroyed
            self.scenario_editor_window.protocol("WM_DELETE_WINDOW", self.on_scenario_editor_window_close)
        self.scenario_editor_window.wait_visibility()
        self.scenario_editor_window.focus()
        self.scenario_editor_window.grab_set()

    def on_message_window_close(self):
        if self.message_window:
            self.message_window.grab_release()
            self.message_window.destroy()
            self.message_window = None

    def on_settings_window_close(self):
        if self.toplevel_window:
            self.toplevel_window.grab_release()
            self.toplevel_window.destroy()
            self.toplevel_window = None

    def on_scenario_editor_window_close(self):
        if self.scenario_editor_window:
            self.scenario_editor_window.grab_release()
            self.scenario_editor_window.destroy()
            self.scenario_editor_window = None

    def on_closing(self):
        # Cancel all scheduled callbacks
        for callback_id in self.after_callbacks:
            self.after_cancel(callback_id)
        self.after_callbacks.clear()

        # Destroy the main window
        self.withdraw()
        self.quit()

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error during execution: {e}")
        raise e
