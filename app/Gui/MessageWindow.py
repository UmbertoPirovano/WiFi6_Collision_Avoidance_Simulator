import customtkinter

class MessageWindow(customtkinter.CTkToplevel):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x500")
        self.title("")
        self.resizable(False,False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self, state="normal", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")  # Disable after inserting text
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)