import io
import os
import sys
import tkinter as tk
import customtkinter
from PIL import Image
import matplotlib.pyplot as plt

from Gui.MessageWindow import MessageWindow
from Gui.SettingsWindow import SettingsWindow
from simulator import AirSimCarSimulation

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.ip_address = ""
        self.output_directory = './run/'

        # configure window
        self.title("5GCARS1 Simulator")
        self.geometry(f"{1244}x{750}")
        self.resizable(False, False)
        # initialize secondary windows
        self.toplevel_window = None
        self.message_window = None

        # keep track of after callbacks
        self.after_callbacks = []

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # SIDEBAR FRAME
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="5GCARS1", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.run_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_1.configure(text="RUN")
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_settingsWindow)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(text="Settings")

        # INPUT FRAME
        self.input_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.input_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=3)
        self.input_frame.grid_rowconfigure(9, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)

        # CV PARAMETERS
        self.cvlabel = customtkinter.CTkLabel(self.input_frame, text="Cv model parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.cvlabel.grid(row=0, column=0, columnspan=1, pady=10)
        self.info_button_cv = customtkinter.CTkButton(self.input_frame, text="info", font=customtkinter.CTkFont(size=12, weight="bold"), command=self.open_cvInfoWindow)
        self.info_button_cv.grid(row=0, column=1, pady=10)

        # CV Model
        self.option1 = customtkinter.CTkLabel(self.input_frame, text="CV model:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.option1.grid(row=1, column=0, padx=20, pady=(10, 10))

        self.optionmenu_1 = customtkinter.CTkComboBox(self.input_frame, values=["Superlight", "Light", "Medium", "Heavy"], state="readonly")
        self.optionmenu_1.grid(row=1, column=1, padx=20, pady=(10, 10))
        self.optionmenu_1.set("Superlight")

        # Image Format
        self.option2 = customtkinter.CTkLabel(self.input_frame, text="Image Format:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.option2.grid(row=2, column=0, padx=20, pady=(10, 10))

        self.optionmenu_2 = customtkinter.CTkComboBox(self.input_frame, values=["JPEG", "PNG"], state="readonly")
        self.optionmenu_2.grid(row=2, column=1, padx=20, pady=(10, 10))
        self.optionmenu_2.set("PNG")

        # GPU Selection
        self.gpu_label = customtkinter.CTkLabel(self.input_frame, text="GPU Selection:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.gpu_label.grid(row=3, column=0, padx=20, pady=(20, 10))

        self.gpu_var = tk.StringVar(value='device')
        self.gpu_combobox = customtkinter.CTkComboBox(self.input_frame, values=["device", "virtual"], state="readonly", variable=self.gpu_var, command=self.update_gpu_info)
        self.gpu_combobox.grid(row=3, column=1, padx=20, pady=(10, 10))
        self.gpu_combobox.set("device")

        # Virtual GPU Entry
        self.virtual_label = customtkinter.CTkLabel(self.input_frame, text="Inference time:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.virtual_entry = customtkinter.CTkEntry(self.input_frame)
        self.virtual_entry.bind('<Return>', self.parse_virtual_entry)
        self.virtual_entry.configure(state="disabled")
        self.virtual_label.grid(row=4, column=0, padx=10, pady=10)
        self.virtual_entry.grid(row=4, column=1, padx=10, pady=10)

        # CHANNEL PARAMETERS
        self.label_fr = customtkinter.CTkLabel(self.input_frame, text="Channel parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_fr.grid(row=5, column=0, pady=10)
        self.info_button_channel = customtkinter.CTkButton(self.input_frame, text="info", font=customtkinter.CTkFont(size=12, weight="bold"), command=self.open_channelInfoWindow)
        self.info_button_channel.grid(row=5, column=1, pady=10)
        # Bandwidth
        self.bandwidth = customtkinter.CTkLabel(self.input_frame, text="Bandwidth [MHz]:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.bandwidth.grid(row=7, column=0, padx=10, pady=10)
        self.bandwidth_values = customtkinter.CTkComboBox(self.input_frame, values=["20", "40", "80", "160"], state="readonly")
        self.bandwidth_values.grid(row=7, column=1, padx=10, pady=10)
        self.bandwidth_values.set("20")

        # Central frequency
        self.central_frequency = customtkinter.CTkLabel(self.input_frame, text="Central frequency[GHz]:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.central_frequency.grid(row=6, column=0, padx=10, pady=10)
        self.frequency_values = customtkinter.CTkComboBox(self.input_frame, values=["2.4", "5"], state="readonly", command=self.update_bandwidth_values)
        self.frequency_values.grid(row=6, column=1, padx=10, pady=10)
        self.frequency_values.set("5")

        # Transmitted power
        self.ptx = customtkinter.CTkLabel(self.input_frame, text="Ptx [dBm]:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.ptx.grid(row=8, column=0, padx=10, pady=10)
        self.ptx_values = customtkinter.CTkComboBox(self.input_frame, values=["-15", "-20", "-25", "-30"], state="readonly")
        self.ptx_values.grid(row=8, column=1, padx=10, pady=10)
        self.ptx_values.set("-15")

        # LOGBOX
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=3, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.insert(index="0.0", text="Simulation output:")

        # SIDE IMAGES
        self.image_frame = customtkinter.CTkFrame(self, width=500, corner_radius=0)
        self.image_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=4)
        self.image_frame.grid_rowconfigure((0), weight=1)
        self.image_frame.grid_rowconfigure((1, 2), weight=2)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Gui/asset")
        self.img1 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "cv_placeholder.png")), size=(533, 300))
        self.image1 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img1)
        self.label_img = customtkinter.CTkLabel(self.image_frame, text="Last Segmented Image", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_img.grid(row=0, column=0, padx=20, pady=5)
        self.image1.grid(row=1, column=0, padx=20, pady=5)
        self.img2 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "latency_placeholder.png")), size=(533, 300))
        self.image2 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img2)
        self.image2.grid(row=2, column=0, padx=20, pady=5)
        tot = [12, 50, 20]
        self.set_plot(tot)

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
        self.image1.configure(image=self.img1)
        print(f"GUI>> Image loaded: {vis_path}")

    def set_plot(self, Total_lat):
        # Desired pixel dimensions
        pixel_width = 533
        pixel_height = 370

        # Convert pixels to inches (default DPI is 100)
        inch_width = pixel_width / 100
        inch_height = pixel_height / 100

        # Create the figure and axis with the specified size
        plt.close('all')
        fig, ax = plt.subplots(figsize=(inch_width, inch_height))

        # Create a lollipop plot
        ax.stem(range(len(Total_lat)), Total_lat)

        # Customize the plot
        ax.set_title('Overall service latency')
        ax.set_xlabel('Inference')
        ax.set_ylabel('Latency (ms)')
        ax.set_ylim(min(Total_lat) - 50, max(Total_lat) + 50)
        ax.grid(True)
        # Adjust layout to prevent labels from being cut off
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
        self.image2.configure(image=ctk_image)
        self.image2.image = ctk_image  # Keep a reference to avoid garbage collection

        # Close the buffer
        buf.close()

    def update_gui(self, times):
        self.set_image()
        overall_time = [sum(x)*1000 for x in zip(*times)]
        self.set_plot(overall_time)
        self.update()

    def set_ip_address(self, ip):
        self.ip_address = ip

    def set_output_directory(self, directory):
        self.output_directory = directory

    def update_gpu_info(self, event=None):
        selected_gpu = self.gpu_var.get()
        if selected_gpu == "device":
            self.virtual_entry.delete(0, tk.END)
            self.virtual_entry.configure(state="disabled")
        else:
            self.virtual_entry.configure(state="normal")

    def parse_virtual_entry(self, event=None):
        try:
            float(self.virtual_entry.get())
        except ValueError:
            self.virtual_entry.delete(0, tk.END)
            self.virtual_entry.insert(0, "")

    def run_button_event(self):
        simulation = AirSimCarSimulation(
            gui=self,
            client_ip='192.168.1.21',
            directory = './run/',
            cv_mode='light',
            inf_time=1,
            channel_params=[20e6, 5, -15],
            image_format='JPEG',
            image_quality=80,
            decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]}
        )
        simulation.run_simulation(obstacle="fence")
        simulation.run_simulation(obstacle="car")

    def open_cvInfoWindow(self):
        text = "CV INFO:\n\nAggiungi descrizione"
        self.open_message_window(text)

    def open_channelInfoWindow(self):
        cv_text = "CHANNEL INFO:\n\nAggiungi descrizione"
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
