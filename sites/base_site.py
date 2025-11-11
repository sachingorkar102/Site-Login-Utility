import gspread
from google.oauth2.service_account import Credentials
from sites.driver_manager import ChromeManager
from sites.sheet_manager import SheetManager
import subprocess
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class BaseSite:

    CREDENTIALS = "credentials.json"
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    

    def __init__(self, sheet_name: str,site_name: str):
        self.sheet_name = sheet_name
        self.site_name = site_name
        self.chrome_path = None
        self.user_data_path = None
        self.spreadsheet_id = None
        self.records = None
        self.read_config()
        self.load_records()



    def load_records(self):
        if(SheetManager.get_sheet() == None):
            self.connect()
        if(SheetManager.get_sheet() != None):
            self.sheet = SheetManager.get_sheet().worksheet(self.sheet_name)
            self.records = self.sheet.get_all_records()
        

    def reload_records(self):
        self.connect()
        self.load_records()

    def connect(self):
        try:
            creds = Credentials.from_service_account_file(self.CREDENTIALS, scopes=self.SCOPES)
            SheetManager.set_sheet(gspread.authorize(creds).open_by_key(self.spreadsheet_id))
        except:
            print("Failed to load the sheet")


    def start_chrome(self):
        port = 9222
        subprocess.Popen([
        self.chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={self.user_data_path}"
        ])
        options = Options()
        options.debugger_address = f"127.0.0.1:{port}"
        ChromeManager.set_driver(webdriver.Chrome(options=options))
        ChromeManager.get_driver().maximize_window()

    def open_new_tab(self, url):
        if(ChromeManager.get_driver() == None):
            self.start_chrome()
            ChromeManager.get_driver().get(url)
        else:
            try:
                ChromeManager.get_driver().execute_script(f"window.open('{url}', '_blank');")
                ChromeManager.get_driver().switch_to.window(ChromeManager.get_driver().window_handles[-1])
            except:
                self.start_chrome()
                ChromeManager.get_driver().get(url)

    
    def wait_and_find(self,driver, by, locator, timeout=10):
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.visibility_of_element_located((by, locator)))


    def get_assessees(self):
        if (self.records == None):
            self.load_records()
        return [r["Assessee"] for r in self.records]
        

    def get_login_details(self, assessee_name: str):
        if (self.records == None):
            self.load_records()
        for r in self.records:
            if r["Assessee"].lower() == assessee_name.lower():
                return r["TAN"],r["PAN"], r["Username"], r["Password"]
        return None, None, None, None

    
    def login(self, tan,pan, username, password):
        pass

    def read_config(self):
        with open("config.txt", 'r') as f:
            for line in f:
                if(line.startswith("chrome_path:")):
                    self.chrome_path = line.split("chrome_path:")[1].strip()
                elif(line.startswith("user_data_path:")):
                    self.user_data_path = line.split("user_data_path:")[1].strip()
                elif(line.startswith("spreadsheet_id:")):
                    self.spreadsheet_id = line.split("spreadsheet_id:")[1].strip()

                

