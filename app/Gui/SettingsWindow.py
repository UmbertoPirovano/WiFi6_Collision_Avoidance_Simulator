import random
import re
import tkinter as tk
import customtkinter

class SettingsWindow(customtkinter.CTkToplevel):
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
        self.directory = tk.filedialog.askdirectory()
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