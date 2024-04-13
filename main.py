import random
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class ArchitectureClass:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = 'https://members.architecture.com.au/Web/Sign_In.aspx'
        self.main_page_url = 'https://acumen.architecture.com.au/'
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def check_login_status(self):
        status = True
        self.driver.get(self.main_page_url)
        try:
            self.wait_for_element_visible_by_xpath("/html/body/div/div/div[2]", timeout=random.randint(5, 7))
            # Check if "Currently logged in" and "Logout" appear on the page
            if not ("Currently logged in" and "Logged in") in self.driver.page_source:
                self.logger.info("Have not log in. Logging in...")
                status = self.login()
            else:
                self.logger.info("Already logged in.")
            return status
        except NoSuchElementException:
            self.logger.warning("Exception raised while checking login status.")
            return False

    def login(self):
        retries = 2  # Number of login retry attempts
        for attempt in range(retries + 1):  # Including the initial attempt
            self.driver.get(self.login_url) # Moving to the login page
            username_field = self.wait_for_element_visible_by_xpath(
                "//input[@id='ctl01_TemplateBody_WebPartManager1_gwpciwelcomebannersignin_ciwelcomebannersignin_signInUserName']")
            self.logger.info("Inputting username...")
            username_field.send_keys(self.username)
            password_field = self.wait_for_element_visible_by_xpath(
                "//input[@id='ctl01_TemplateBody_WebPartManager1_gwpciwelcomebannersignin_ciwelcomebannersignin_signInPassword']")
            self.logger.info("Inputting password...")
            password_field.send_keys(self.password)
            self.logger.info("Logging...")
            password_field.send_keys(Keys.ENTER)
            sleep(random.randint(3, 5))
            # Wait for the page to load after login
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID,
                    "ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00__0")))
                self.logger.info("Redirecting to main page...")
                # Check if login was successful by verifying the presence of a certain element in the page
                if "My Profile" in self.driver.page_source:
                    self.logger.info("Login successful!")
                    return True
                else:
                    self.logger.warning("Login failed. Please check your credentials.")
            except TimeoutException:
                self.logger.error("Timed out waiting for page to load after login.")
                if attempt < retries:
                    self.logger.info(f"Retrying login (attempt {attempt + 1}/{retries + 1})...")
                else:
                    self.logger.error("All login attempts failed.")
        return False

    def handle_login(self):
        loggedin = False
        if not self.check_login_status():
            loggedin = self.login()
        self.driver.close()
        self.driver.quit()
        return loggedin

    def wait_for_element_visible_by_xpath(self, xpath, retries=3, max_reload_attempts=3, timeout=random.randint(10, 15)):
        reload_attempts = 0
        for _ in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                return element
            except TimeoutException:
                print(f"Timed out waiting for element with XPATH: {xpath}. Retrying...")
                reload_attempts += 1
                if reload_attempts >= max_reload_attempts:
                    raise TimeoutException(f"Failed to locate element with XPATH: {xpath} after {retries} retries and {max_reload_attempts} reload attempts.")
                self.driver.refresh()
        raise TimeoutException(f"Failed to locate element with XPATH: {xpath} after {retries} retries.")



