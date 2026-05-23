from .base_site import BaseSite
from selenium import webdriver
from sites.driver_manager import ChromeManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from tkinter import messagebox
from selenium.webdriver.common.by import By
import time


class TracesSite(BaseSite):
    def __init__(self):
        super().__init__(
            sheet_name="Traces",
            site_name="Traces"
        )

    def login(self, tan,pan, password):
        if(tan == "" or password == ""):
            messagebox.showerror("Error","Empty Fields, can't login")
            return
        url = "https://traces.tdscpc.gov.in/auth/login/loginScreen"
        self.open_new_tab(url)
        
        driver = ChromeManager.get_driver()

        time.sleep(5)

        actions = ActionChains(driver)


        # USERNAME
        for _ in range(19):
            actions.send_keys(Keys.TAB).perform()

        time.sleep(1)

        for ch in tan:
            actions.send_keys(ch).perform()
            time.sleep(0.1)

        # PASSWORD
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()

        time.sleep(1)

        for ch in password:
            actions.send_keys(ch).perform()
            time.sleep(0.1)

        # CAPTCHA
        for _ in range(4):
            actions.send_keys(Keys.TAB).perform()


