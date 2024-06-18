import io
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter
from PIL import Image,ImageTk
import random
import re
import matplotlib.pyplot as plt
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

import customtkinter

class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x500")
        self.title("Parameters' details")
        self.resizable(False,False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self, state="normal", font=customtkinter.CTkFont(family="TimesNewRoman", size=12, weight="bold"))
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")  # Disable after inserting text
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x300")
        self.title("Settings")
        self.resizable(False,False)
        self.parent=parent
        #Grid 
        self.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.grid_rowconfigure((0, 1, 2,3,4), weight=1)
        self.input_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), rowspan=3,columnspan=4)
        self.input_frame.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.input_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Client IP Entry
        self.ip_label = customtkinter.CTkLabel(self.input_frame, text="AirSim IP:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.ip_label.grid(row=0,column=0, padx=20, pady=10)
        self.ip_entry = customtkinter.CTkEntry(self.input_frame)
        self.ip_entry.grid(row=0, column=1, padx=20, pady=20,columnspan=2)
        self.ip_entry.insert(0,"127.0.0.1")

    
        # Directory
        self.directory_label = customtkinter.CTkLabel(self.input_frame, text="Out dir:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.directory_label.grid(row=1,column=0, padx=20, pady=10)
        self.directory_entry = customtkinter.CTkLabel(self.input_frame, text="./run/")
        self.directory_entry.grid(row=1, column=1, padx=20, pady=20, columnspan=2)        
        self.select_directory_button = customtkinter.CTkButton(self.input_frame, text="Select Directory", command=self.select_directory)
        self.select_directory_button.grid(row=1, column=4, padx=20, pady=20)
        #RNG
        self.rng_label = customtkinter.CTkLabel(self.input_frame, text="Random Number Generator", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.rng_label.grid(row=2,column=0, padx=20, pady=10)
        self.rng_entry = customtkinter.CTkEntry(self.input_frame)
        self.rng_entry.grid(row=2, column=1, padx=20, pady=20, columnspan=2)
        self.rng_entry.bind('<Return>',command=self.parse_rng_entry)
        # BUTTON FRAME
        self.buttonframe =customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.buttonframe.grid(row=4,column=0,columnspan=4, padx=(20, 20), pady=(20, 20))
        self.buttonframe.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.buttonframe.grid_columnconfigure((0,1,2,3,4), weight=1)

        # create a Save button
        self.save_button = customtkinter.CTkButton(self.buttonframe, text="Save & Exit", command=self.save_settings)
        self.save_button.grid(row=0, column=3, padx=20, pady=10)

        # create an Exit button
        self.exit_button = customtkinter.CTkButton(self.buttonframe, text="Exit", command=self.destroy)
        self.exit_button.grid(row=0, column=4, padx=20, pady=10)
        #Confirm connection
        self.label_connection = customtkinter.CTkLabel(self.input_frame,text="")
        self.label_connection.grid(row=2,column = 0 ,padx=20,pady=10)
    
        
    def parse_rng_entry(self,event):
        try:
            a = float(self.rng_entry.get())
            rng = random.seed(a)
        except ValueError:
            self.rng_entry.delete(0,tk.END)
            self.rng_entry.insert(0,"")

    def save_settings(self):
        client_ip = self.ip_entry.get()
        Directory = self.directory_entry.cget("text")
        if self.validate_ip():
            self.parent.set_ip_address(client_ip)
            self.destroy()
        else:
            self.label_connection.configure(text="IP format not valid")
            
       
        self.parent.set_output_directory(Directory)
    
    
    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.directory_entry.configure(text=self.directory)

    def validate_ip(self):
        ip = self.ip_entry.get()
        pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if pattern.match(ip):
            segments = ip.split(".")
            if all(0 <= int(segment) <= 255 for segment in segments):
                return True
        return False

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("5GCARS1 Simulator")
        self.geometry(f"{1244}x{750}")
        self.resizable(False,False)
        # initialize secondary widows
        self.toplevel_window = None
        self.message_window = None

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
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_toplevel)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(text="Settings")        
         
        ## INPUT FRAME
        self.input_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.input_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=3)
        self.input_frame.grid_rowconfigure(9, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)

        ## CV PARAMETERS
        self.cvlabel = customtkinter.CTkLabel(self.input_frame, text="Cv model parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.cvlabel.grid(row=0,column=0,columnspan=1, pady=10)
        self.info_button_cv = customtkinter.CTkButton(self.input_frame,text="info",font=customtkinter.CTkFont(size=12, weight="bold"),command=self.open_cvInfoWindow)
        self.info_button_cv.grid(row=0,column=1, pady=10)
        
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
        self.virtual_entry.bind('<Return>',command=self.parse_virtual_entry)
        self.virtual_entry.configure(state="disabled")
        self.virtual_label.grid(row=4, column=0, padx=10, pady=10)
        self.virtual_entry.grid(row=4, column=1, padx=10, pady=10)

        ## CHANNEL PARAMETERS
        self.label_fr = customtkinter.CTkLabel(self.input_frame, text="Channel parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_fr.grid(row=5,column=0, pady=10)
        self.info_button_channel = customtkinter.CTkButton(self.input_frame,text="info",font=customtkinter.CTkFont(size=12, weight="bold"),command=self.open_channelInfoWindow)
        self.info_button_channel.grid(row=5,column=1, pady=10)
        #Bandwidth
        self.bandwidth = customtkinter.CTkLabel(self.input_frame,text="Bandwidth [MHz]:",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.bandwidth.grid(row=7,column=0,padx=10,pady=10)
        self.bandwidth_values = customtkinter.CTkComboBox(self.input_frame,values=["20","40","80","160"],state="readonly")
        self.bandwidth_values.grid(row=7,column=1,padx=10,pady=10)
        self.bandwidth_values.set("20")

        #Central frequency
        self.central_frequency = customtkinter.CTkLabel(self.input_frame,text="Central frequency[GHz]:",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.central_frequency.grid(row=6,column=0,padx=10,pady=10)
        self.frequency_values = customtkinter.CTkComboBox(self.input_frame,values=["2.4","5"],state="readonly",command=self.update_bandwidth_values)
        self.frequency_values.grid(row=6,column=1,padx=10,pady=10)
        self.frequency_values.set("5")
 
        #Transmitted power 
        self.ptx = customtkinter.CTkLabel(self.input_frame,text="Ptx [dBm]:",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.ptx.grid(row=8,column=0,padx=10,pady=10)
        self.ptx_values = customtkinter.CTkComboBox(self.input_frame,values=["-15","-20","-25","-30"],state="readonly")
        self.ptx_values.grid(row=8,column=1,padx=10,pady=10)
        self.ptx_values.set("-15")
        
        ## LOGBOX
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=3, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.insert(index="0.0", text="Simulation output:")

        ## SIDE IMAGES
        self.image_frame = customtkinter.CTkFrame(self, width=500, corner_radius=0)
        self.image_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=4)
        self.image_frame.grid_rowconfigure((0),weight=1)
        self.image_frame.grid_rowconfigure((1,2), weight=2)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Images")
        self.img1 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_1.png")), size=(533, 300))
        self.image1 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img1)
        self.label_img = customtkinter.CTkLabel(self.image_frame,text="Last Segmented Image",font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_img.grid(row=0,column=0,padx=20,pady=5)
        self.image1.grid(row=1, column=0, padx=20, pady=5)
        self.img2 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_2.png")), size=(533, 300))
        self.image2 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img2)
        self.image2.grid(row=2, column=0, padx=20, pady=5)
        tot = [12,50,20]
        self.set_plot(tot)
        #Retrived parameter from settings
        self.ip_address = None
        self.output_directory = None
    
    def update_bandwidth_values(self, event):
        selected_frequency = self.frequency_values.get()
        if selected_frequency == '2.4':
            self.bandwidth_values=customtkinter.CTkComboBox(self.input_frame,values=["20","40"],state="readonly")
            self.bandwidth_values.grid(row=7,column=1,padx=10,pady=10)
        elif selected_frequency == '5':
            self.bandwidth_values=customtkinter.CTkComboBox(self.input_frame,values=["20","40","80","160"],state="readonly")
            self.bandwidth_values.grid(row=7,column=1,padx=10,pady=10)  # Default to 20 MHz if previously selected bandwidth is not available
    
    def set_image(self, img_path):
        self.img1 = customtkinter.CTkImage(Image.open(os.path.join(img_path, "image_1.png")), size=(533, 300))
        self.image1 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img1)
        self.image1.grid(row=0, column=0, padx=20, pady=20)# TODO:It must load the image at img_path
        return
    
    def set_plot(self, Total_lat):
            # Desired pixel dimensions
            pixel_width = 533
            pixel_height = 370

            # Convert pixels to inches (default DPI is 100)
            inch_width = pixel_width / 100
            inch_height = pixel_height / 100

            # Create the figure and axis with the specified size
            fig, ax = plt.subplots(figsize=(inch_width, inch_height))

            # Create a lollipop plot
            ax.stem(range(len(Total_lat)), Total_lat)

            # Customize the plot
            ax.set_title('Overall latency')
            ax.set_xlabel('Index')
            ax.set_ylabel('Latency')
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
    def set_ip_address(self,ip):
        self.ip_address = ip
        

    def set_output_directory(self,Directory):
        self.output_directory = Directory

    def update_gpu_info(self, event):
        selected_gpu = self.gpu_var.get()
        if selected_gpu == "device":
            self.virtual_entry.delete(0,tk.END)
            self.virtual_entry.configure(state="disabled")
        else:
            self.virtual_entry.configure(state="normal")

    def parse_virtual_entry(self,event):
        try:
            float(self.virtual_entry.get())
        except ValueError:
            self.virtual_entry.delete(0,tk.END)
            self.virtual_entry.insert(0,"")

    
    def run_button_event(self):
        if self.parse_input():
            # TODO:HERE RUN THE SIMULATION
            return    

    def open_cvInfoWindow(self):
        text = "CV INFO:\n\nAggiungi descrizione"
        if self.message_window is None or not self.message_window.winfo_exists():
            self.message_window = MessageWindow(text=text)  # create window if its None or destroyed
        self.message_window.focus()

    def open_channelInfoWindow(self):
        cv_text = "CHANNEL INFO:\n\nAggiungi descrizione"
        if self.message_window is None or not self.message_window.winfo_exists():
            self.message_window = MessageWindow(text=cv_text)  # create window if its None or destroyed
        self.message_window.focus()
    
    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        self.toplevel_window.focus()
        self.toplevel_window.grab_set()

if __name__ == "__main__":
    app = App()
    app.mainloop()
