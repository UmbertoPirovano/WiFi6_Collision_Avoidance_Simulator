import tkinter as tk
import customtkinter

class ScenarioEditorWindow(customtkinter.CTkToplevel):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x300")
        self.title("Scenario Editor")
        self.resizable(False,False)
        self.parent=parent

        #Grid 
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.scenario_name_label = customtkinter.CTkLabel(self, text="Scenario Name:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.scenario_name_label.grid(row=0,column=1, padx=20, pady=10)
        self.scenario_name_entry = customtkinter.CTkEntry(self)
        self.scenario_name_entry.grid(row=0, column=2, padx=20, pady=20)
        self.scenario_name_entry.insert(0,"Custom scenario")
        self.instruction_text = customtkinter.CTkTextbox(self, width=40, height=5, corner_radius=0, font=customtkinter.CTkFont(size=16))
        self.instruction_text.grid(row=1, column=0, padx=20, pady=10, columnspan=4, rowspan=2, sticky="nsew")
        self.instruction_text.insert(tk.END, "In AirSim, manually drive the car to the desired position and orientation.\n\nWhen done, come back here and click the 'Save' button.")
        self.instruction_text.configure(state="disabled")
        self.save_button = customtkinter.CTkButton(self, text="Save", command=self.save_scenario)
        self.save_button.grid(row=3, column=1, padx=20, pady=10, columnspan=2)

    def save_scenario(self):
        name = self.scenario_name_entry.get()
        self.parent.add_scenario(name)
        self.destroy()


        
    
        
    