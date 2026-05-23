from .base_site import BaseSite
import selenium.webdriver as webdriver
from sites.driver_manager import ChromeManager
from tkinter import messagebox
from selenium.webdriver.common.by import By
import time

class IncomeTaxTDSSite(BaseSite):
    def __init__(self):
        super().__init__(
            sheet_name="IncomeTaxTDS",
            site_name="Income Tax TDS"
        )

    def login(self, tan, pan, password):
        if(tan == "" or password == ""):
            messagebox.showerror("Error","Empty Fields, can't login")
            return
        url = "https://eportal.incometax.gov.in/iec/foservices/#/login"
        self.open_new_tab(url)
        input_username = self.wait_and_find(ChromeManager.get_driver(),By.NAME,"panAdhaarUserId")
        input_username.send_keys(tan)

        button1 = self.wait_and_find(ChromeManager.get_driver(),By.XPATH,"""//*[@id="maincontentid"]/app-login/div/app-login-page/div/div[2]/div[1]/div[2]/button""")
        button1.click()

        input_password = self.wait_and_find(ChromeManager.get_driver(),By.XPATH,"""//*[@id="loginPasswordField"]""")
        input_password.send_keys(password)

        checkbox = self.wait_and_find(ChromeManager.get_driver(),By.XPATH,"""//*[@id="passwordCheckBox"]""")
        checkbox.click()
        time.sleep(1)
        ChromeManager.get_driver().execute_script("window.scrollBy(0, 100);")
        time.sleep(1)
        button2 = self.wait_and_find(ChromeManager.get_driver(),By.XPATH,"""/html/body/app-root/div[1]/div[3]/app-login/div/app-password-page/div[1]/div[2]/div[1]/div[5]/button""")
        button2.click()
        time.sleep(3)
        button2.click()
