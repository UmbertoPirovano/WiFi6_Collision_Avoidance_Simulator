import os
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog
import customtkinter
from PIL import Image
import re

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self,text=""):
        self.geometry("600x500")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.textbox= customtkinter.CTkTextbox(self,text=text,state="readonly")
        self.textbox.grid(row=0,column=0)



class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x500")

    #Grid 
        self.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.grid_rowconfigure((0, 1, 2,3,4), weight=1)
        self.input_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.input_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=3,columnspan=4)
        self.input_frame.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.input_frame.grid_columnconfigure((0,1,2,3), weight=1)
        # Client IP Checkbox
        self.client_ip_var = tk.BooleanVar()
        self.client_ip_checkbox = customtkinter.CTkCheckBox(self.input_frame, text="Client IP", variable=self.client_ip_var, command=self.toggle_ip_entry)
        self.client_ip_checkbox.grid(row=0, column=0, padx=20, pady=10)

        # Client IP Entry Frame (initially hidden)
        self.ip_label = customtkinter.CTkLabel(self.input_frame, text="Enter IP:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.ip_label.grid(row=0,column=1)
        self.ip_entry = customtkinter.CTkEntry(self.input_frame)
        self.ip_entry.grid(row=0, column=2, padx=20, pady=10,columnspan=2, sticky="nsew")
    
        #Directory
        # create a button
        self.select_directory_button = customtkinter.CTkButton(self.input_frame, text="Select Directory", command=self.select_directory)
        self.select_directory_button.grid(row=1, column=0, padx=20, pady=20)

        # create a label to display the selected directory
        self.directory_label = customtkinter.CTkLabel(self.input_frame, text="./run/")
        self.directory_label.grid(row=1, column=1, padx=20, pady=20,columnspan=3)
        

        self.buttonframe =customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.buttonframe.grid(row=4,column=0,columnspan=4, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.buttonframe.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.buttonframe.grid_columnconfigure((0,1,2,3,4), weight=1)

        # create a Save button
        self.save_button = customtkinter.CTkButton(self.buttonframe, text="Save", command=self.save_directory)
        self.save_button.grid(row=0, column=3, padx=20, pady=10)

        # create an Exit button
        self.exit_button = customtkinter.CTkButton(self.buttonframe, text="Exit", command=self.destroy)
        self.exit_button.grid(row=0, column=4, padx=20, pady=10)

    def save_directory(self):
        return
    
    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.directory_label.configure(text=self.directory)


    def toggle_ip_entry(self):
        if self.client_ip_var.get():
            self.ip_frame.grid()
        else:
            self.ip_frame.grid_remove()

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
        self.geometry(f"{1244}x{700}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="5GCARS1", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_1.configure(text="RUN")
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_toplevel)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(text="Settings")
        self.toplevel_window = None
        self.message_window = None
         
        # Input Frame
        self.input_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.input_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=3)
        self.input_frame.grid_rowconfigure(9, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)

        self.cvlabel = customtkinter.CTkLabel(self.input_frame, text="Cv model parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.cvlabel.grid(row=0,column=0,columnspan=1)
        self.cv_text = "-------------ciao"
        self.info_button_cv = customtkinter.CTkButton(self.input_frame,text="info",font=customtkinter.CTkFont(size=12, weight="bold"),command=self.open_textmessage)
        self.info_button_cv.grid(row=0,column=1)
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
        self.gpu_combobox = customtkinter.CTkComboBox(self.input_frame, values=["device", "virtual"], state="readonly", variable=self.gpu_var)
        self.gpu_combobox.grid(row=3, column=1, padx=20, pady=(10, 10))
        self.gpu_combobox.set("device")
        self.gpu_combobox.bind("<<ComboboxSelected>>", self.update_gpu_info)

        # Virtual GPU Entry
        self.virtual_label = customtkinter.CTkLabel(self.input_frame, text="Enter Virtual GPU:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.virtual_entry = customtkinter.CTkEntry(self.input_frame)
        self.virtual_label.grid(row=4, column=0, padx=10, pady=10)
        self.virtual_entry.grid(row=4, column=1, padx=10, pady=10)  # Initially hide the virtual frame

        self.label_fr = customtkinter.CTkLabel(self.input_frame, text="Channel parameters:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_fr.grid(row=5,column=0,columnspan=2)
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
        # create logbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=3, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.insert(index="0.0", text="Simulation output:")

        # create image frame
        self.image_frame = customtkinter.CTkFrame(self, width=500, corner_radius=0)
        self.image_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew", rowspan=4)
        self.image_frame.grid_rowconfigure(2, weight=1)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Images")
        self.img1 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_0.png")), size=(533, 300))
        self.image1 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img1)
        self.image1.grid(row=0, column=0, padx=20, pady=20)
        self.img2 = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_1.png")), size=(533, 300))
        self.image2 = customtkinter.CTkLabel(self.image_frame, text="", image=self.img2)
        self.image2.grid(row=1, column=0, padx=20, pady=20)


    def update_bandwidth_values(self, event):
        selected_frequency = self.frequency_values.get()
        if selected_frequency == '2.4':
            self.bandwidth_values=customtkinter.CTkComboBox(self.input_frame,values=["20","40"],state="readonly")
            self.bandwidth_values.grid(row=5,column=1,padx=10,pady=10)
            print("ook") # Default to 20 MHz if previously selected bandwidth is not available
        elif selected_frequency == '5':
            self.bandwidth_values=customtkinter.CTkComboBox(self.input_frame,values=["20","40","80","160"],state="readonly")
            self.bandwidth_values.grid(row=5,column=1,padx=10,pady=10)  # Default to 20 MHz if previously selected bandwidth is not available
    
    def update_gpu_info(self, event):
        selected_gpu = self.gpu_var.get()

        if selected_gpu == 'device':
            self.hide_virtual_gpu_entry()
        elif selected_gpu == 'virtual':
            self.show_virtual_gpu_entry()
        else:
            self.virtual_label.config(text="Unknown GPU selection.")
            self.hide_virtual_gpu_entry()

    def show_virtual_gpu_entry(self):
        self.virtual_frame.grid()
        self.virtual_frame.lift()  # Ensure it's visible above other widgets

    def hide_virtual_gpu_entry(self):
        self.virtual_frame.grid_remove()

    def sidebar_button_event(self):
        if self.client_ip_var.get() and not self.validate_ip():
            tkinter.messagebox.showerror("Invalid IP", "The entered IP address is not valid.")
        else:
            print("sidebar_button click")
            if self.client_ip_var.get():
                print("Client IP:", self.ip_entry.get())
    

    def open_textmessage(self):
        if self.message_window is None or not self.message_window.winfo_exists():
            self.message_window = MessageWindow(self,self.cv_text)  # create window if its None or destroyed
        else:
            self.message_window.focus() 
    
    
    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

if __name__ == "__main__":
    app = App()
    app.mainloop()
