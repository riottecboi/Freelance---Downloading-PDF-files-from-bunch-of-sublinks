import random
import logging
import json
import re
import os
from time import sleep
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class ArchitecturePDFDownloader:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = 'https://members.architecture.com.au/Web/Sign_In.aspx'
        self.main_page_url = 'https://acumen.architecture.com.au/'
        # URLs to include
        self.default_parent_url = "https://acumen.architecture.com.au/practice/negotiation-and-dispute-resolution/"
        self.allowed_urls = [
            "https://acumen.architecture.com.au/project",
            "https://acumen.architecture.com.au/practice",
            "https://acumen.architecture.com.au/resources",
            "https://acumen.architecture.com.au/environment",
            "https://acumen.architecture.com.au/notepacks"
        ]
        # Set Options to specify download directory
        self.pdf_download_dir = "/tmp/links/"
        self.chrome_options = Options()
        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        self.chrome_options.add_experimental_option("prefs", {
            "download.extensions_to_open": "pdf",
            'printing.print_preview_sticky_settings.appState': json.dumps(settings),
            "download.default_directory": self.pdf_download_dir,
            "savefile.default_directory": self.pdf_download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        self.chrome_options.add_argument('--kiosk-printing')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),  options=self.chrome_options)

        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def check_login_status(self, link):
        self.driver.get(link)
        try:
            self.wait_for_element_visible_by_xpath("/html/body/div/div/div[2]", timeout=random.randint(5, 7))
            # Check if "Currently logged in" and "Logout" appear on the page
            if not ("Currently logged in" and "My notes") in self.driver.page_source:
                self.logger.info("Have not log in. Logging in...")
                self.login(link)
            else:
                self.logger.info("Already logged in.")
        except NoSuchElementException:
            self.logger.warning("Exception raised while checking login status.")

    def login(self, redirect):
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
                self.logger.info("Redirecting ...")
                # Check if login was successful by verifying the presence of a certain element in the page
                if "My Profile" in self.driver.page_source:
                    self.logger.info("Login successful!")
                    return
                else:
                    self.logger.warning("Login failed. Please check your credentials.")
            except TimeoutException:
                self.logger.error("Timed out waiting for page to load after login.")
                if attempt < retries:
                    self.logger.info(f"Retrying login (attempt {attempt + 1}/{retries + 1})...")
                else:
                    raise TimeoutException("All login attempts failed.")


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

    def pdf_download(self, url):
        repeats = 0
        self.driver.get(url)
        sleep(3)
        try:
            button = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div/article/main/section[3]/div/div[2]/a[2]/span")
            button.click()
            while True:
                try:
                    WebDriverWait(self.driver, random.randint(5, 7)).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/article/nav/div/section/div/button[1]')))
                    break
                except Exception as e:
                    self.logger.info(f"Refreshing a page - {repeats} time(s)")
                    self.driver.refresh()
                    if repeats == 3:
                        raise Exception(str(e))
                    repeats += 1

        except Exception as e:
            pass
        self.logger.info(f'Downloading PDF ...')
        self.driver.execute_script('window.print();')
        self.logger.info(f"File PDF name {self.driver.title} saved to {self.pdf_download_dir}")

    def count_url_segments(self, url):
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip('/').split('/')
        return len(path_segments)

    def is_directory_exists(self, directory):
        # Check if the directory exists
        if not os.path.exists(directory):
            self.logger.warning("Folder not exists")
            self.logger.info("Creating ...")
            os.makedirs(directory)
            self.logger.info(f"Directory {directory} created successfully")
        else:
            self.logger.info(f"Directory {directory} already exists")
        return directory

    def links_gather(self):
        try:
            self.driver.get(self.default_parent_url)
            sleep(3)
            # Find the div with the specified class name
            div_element = self.driver.find_element_by_class_name("accordion-navigation-group__container")

            # Find all descendant elements within the div that contain the href attribute
            elements = div_element.find_elements_by_xpath(".//*[@href]")

            # Extract href attributes from the elements that match allowed URLs and having max segment equal or below 3
            href_list = [
                element.get_attribute("href")
                for element in elements
                if any(re.match(url_pattern, element.get_attribute("href")) for url_pattern in self.allowed_urls)
                   and self.count_url_segments(element.get_attribute("href")) <= 3 and element.get_attribute("href").strip('/') not in self.allowed_urls
            ]
            return href_list
        except Exception as e:
            self.logger.warning(str(e))
            return []

    def main(self):
        self.logger.info('Starting ...')
        self.logger.info("Gathering links for PDF download ...")
        links = self.links_gather()
        self.logger.info(f"Gathered {len(links)} link(s) in total")
        self.is_directory_exists(self.pdf_download_dir)
        for url in links:
            self.check_login_status(url)
            self.logger.info(f"Downloading PDF from {url}")
            self.pdf_download(url)
            self.logger.info(f"PDF downloaded successful from {url}")
        self.logger.info('Finished a process')

if __name__ == '__main__':
    username = 'xxxx'
    password = 'xxxx'
    architecture_login = ArchitecturePDFDownloader(username, password)
    architecture_login.main()