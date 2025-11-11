from .base_site import BaseSite
from selenium import webdriver
from sites.driver_manager import ChromeManager
from tkinter import messagebox
from selenium.webdriver.common.by import By

class TracesSite(BaseSite):
    def __init__(self):
        super().__init__(
            sheet_name="Traces",
            site_name="Traces"
        )

    

    def login(self, tan,pan, username, password):
        if(tan == "" or username == "" or password == ""):
            messagebox.showerror("Error","Empty Fields, can't login")
            return
        url = "https://www.tdscpc.gov.in/app/login.xhtml?usr=Ded"
        self.open_new_tab(url)
        input_username = self.wait_and_find(ChromeManager.get_driver(),By.NAME,"username")
        input_password = self.wait_and_find(ChromeManager.get_driver(),By.NAME,"j_password")
        input_tan = self.wait_and_find(ChromeManager.get_driver(),By.NAME,"j_tanPan")

        input_username.send_keys(username)
        input_password.send_keys(password)
        input_tan.send_keys(tan)

        input_captcha = ChromeManager.get_driver().find_element(By.NAME,"j_captcha")
        input_captcha.send_keys("")
        input_captcha.click()
