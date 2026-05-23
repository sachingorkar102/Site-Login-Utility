
import tkinter as tk
import gspread
from google.oauth2.service_account import Credentials
from tkinter import ttk, messagebox
from tkinter import PhotoImage
from ttkwidgets.autocomplete import AutocompleteCombobox
import pystray
import os
import sys
from PIL import Image
import threading

from sites.traces_site import TracesSite
from sites.incometaxtds_site import IncomeTaxTDSSite
from sites.incometax import IncomeTaxSite



# --- Site Registry ---
SITE_CLASSES = {
    "TRACES": TracesSite,
    "Income Tax TDS": IncomeTaxTDSSite,
    "Income Tax": IncomeTaxSite
}

APP_NAME = "Site Login Utility"



class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("480x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#f7f7f7")
        
        
        self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        self.icon_path = os.path.join(self.base_path, "icon.png")
        self.icon = PhotoImage(file=self.icon_path)
        self.root.iconphoto(False, PhotoImage(file=self.icon_path))
        self.tray_icon = None
        self.icon_image = Image.open(self.icon_path)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.bind("<Unmap>", self.on_minimize)
        
        self.root.withdraw()
        self.loaded_sites = {}
        for site in SITE_CLASSES.keys():
            self.loaded_sites[site] = SITE_CLASSES[site]()
        self.setup_ui()
        self.hide_window()
        

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#f7f7f7", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TCombobox", font=("Segoe UI", 10))

        # --- Header Frame ---
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(10, 5), padx=10)
        header_frame.configure(style="Header.TFrame")

        style.configure("Header.TFrame", background="#f7f7f7")

        ttk.Label(
            header_frame,
            text="Site Login",
            font=("Segoe UI", 14, "bold"),
            foreground="#333"
        ).pack(side="left", expand=True)

        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        # --- Login Site ---
        ttk.Label(frame, text="Select Login Site:").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )

        self.site_var = tk.StringVar(value="TRACES")

        self.site_dropdown = ttk.Combobox(
            frame,
            textvariable=self.site_var,
            values=list(SITE_CLASSES.keys()),
            state="readonly",
            width=33
        )

        self.site_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.site_dropdown.bind("<<ComboboxSelected>>", self.load_site_data)

        # --- Assessee ---
        ttk.Label(frame, text="Select Assessee:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )

        self.assessee_var = tk.StringVar()

        self.assessee_dropdown = AutocompleteCombobox(
            frame,
            textvariable=self.assessee_var,
            width=35
        )

        self.assessee_dropdown.grid(row=1, column=1, padx=10, pady=5)
        self.assessee_dropdown.bind("<<ComboboxSelected>>", self.on_assessee_selected)
        self.assessee_dropdown.bind("<Return>", self.on_assessee_selected)

        # --- TAN / PAN ---
        self.tan_var = tk.StringVar()
        self.pan_var = tk.StringVar()

        ttk.Label(frame, text="TAN:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )

        ttk.Entry(frame, textvariable=self.tan_var, width=35).grid(
            row=2, column=1, padx=10, pady=5
        )

        ttk.Label(frame, text="PAN:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )

        ttk.Entry(frame, textvariable=self.pan_var, width=35).grid(
            row=3, column=1, padx=10, pady=5
        )

        # --- Password Only ---
        self.password_var = tk.StringVar()

        ttk.Label(frame, text="Password:").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )

        ttk.Entry(frame, textvariable=self.password_var, width=35).grid(
            row=4, column=1, padx=10, pady=5
        )

        # --- Buttons Frame ---
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Login",
            command=self.login_action
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            button_frame,
            text="Copy Details",
            command=self.copy_details_action
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_action
        ).grid(row=0, column=2, padx=10)

        self.load_site_data()


    def load_site_data(self, event=None):
        current_site = self.get_current_site()
        if(current_site != None):
            try:
                assessees = current_site.get_assessees()
                self.assessee_dropdown["completevalues"] = assessees
                if(self.get_string(self.assessee_var) not in assessees):
                    self.assessee_dropdown.set("")
                    self.tan_var.set("")
                    self.pan_var.set("")
                    # self.username_var.set("")
                    self.password_var.set("")
                else:
                    self.on_assessee_selected()
            except Exception as e:
                print(e)
                # messagebox.showerror("Error", f"Failed to load data for {self.site_var.get()}:\n{e}")
        
                

    def on_assessee_selected(self, event=None):
        assessee = self.get_string(self.assessee_var)
        
        tan,pan, username, password = self.get_current_site().get_login_details(assessee)
        self.tan_var.set(tan or "")
        self.pan_var.set(pan or "")
        # self.username_var.set(username or "")
        self.password_var.set(password or "")

    def refresh_action(self):
        confirm = messagebox.askyesno("Refresh Database",f"Are you sure you want to refresh the database for {self.site_var.get()}")
        if confirm:
            self.get_current_site().reload_records()
            self.load_site_data()


                

    def copy_details_action(self):
        if(self.get_string(self.assessee_var) == "" or self.get_string(self.password_var) == ""): return
        site_name = self.get_current_site().site_name
        details = f"{site_name} Login Details of {self.get_string(self.assessee_var)}"
        if((site_name == "Traces" or site_name == "Income Tax TDS") and self.get_string(self.tan_var) != ""):
            details += f"\n User ID: {self.get_string(self.tan_var)}"
        if(site_name == "Income Tax" and self.get_string(self.pan_var) != ""):
            details += f"\n User ID: {self.get_string(self.pan_var)}"
        # if(self.get_string(self.tan_var) != ""):
        #     details += f"\n TAN: {self.get_string(self.tan_var)}"
        # if(self.get_string(self.pan_var) != ""):
        #     details += f"\n PAN: {self.get_string(self.pan_var)}"
        # if(self.get_string(self.username_var) != ""):
        #     details += f"\n Username: {self.get_string(self.username_var)}"
        if(self.get_string(self.password_var) != ""):
            details += f"\n Password: {self.get_string(self.password_var)}"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(details)

    def login_action(self):
        tan = self.get_string(self.tan_var)
        pan = self.get_string(self.pan_var)
        # username = self.get_string(self.username_var)
        password = self.get_string(self.password_var)
        self.get_current_site().login(tan=tan,pan=pan,password=password)
        
    def get_string(self,var):
        return (var.get() or "").strip()

    def get_current_site(self):
        return self.loaded_sites[self.site_var.get()]
    
    def on_minimize(self, event):
        
        if self.root.state() == 'iconic':
            self.hide_window()

    def hide_window(self):
        
        self.root.withdraw()

        if self.tray_icon is None:
            menu = pystray.Menu(
                pystray.MenuItem("Maximize", self.show_window),
                pystray.MenuItem("Quit", self.quit_app)
            )
            self.tray_icon = pystray.Icon("app", self.icon_image, APP_NAME, menu)

            threading.Thread(target=self.tray_icon.run, daemon=True).start()

        self.tray_icon.visible = True

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.state('normal')
        self.root.focus_force()
        if self.tray_icon:
            self.tray_icon.visible = False
            self.tray_icon.stop()
            self.tray_icon = None


    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()

    

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    # app.hide_window()
    root.mainloop()


