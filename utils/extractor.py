import sys
import time
import threading
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
class Extarctor:
    def __init__(self, url):
        self.url = url
        self.stop_spinner = False
        logging.debug(f"Initialized Extarctor with URL: {self.url}")
    def spinning_cursor(self):
        while not self.stop_spinner:
            for cursor in "|/-\\":
                sys.stdout.write(f"\rLoading... {cursor}")
                sys.stdout.flush()
                time.sleep(0.1)
    def convert_duration_to_seconds(self, duration: str) -> int:
        logging.debug(f"Converting duration string to seconds: '{duration}'")
        try:
            parts = [int(p) for p in duration.strip().split(":")]
            if len(parts) == 3:
                seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                seconds = parts[0] * 60 + parts[1]
            else:
                logging.warning(f"Unexpected duration format: '{duration}'")
                return 0
            logging.debug(f"Converted duration: {seconds} seconds")
            return seconds
        except Exception as e:
            logging.error(f"Error converting duration: {e}")
            return 0
    def get_svg_string_and_duration_in_sec(self):
        chrome_options = Options()
        chrome_options.binary_location = os.environ.get("BRAVE_BIN", "/usr/bin/brave-browser")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,1696")
        logging.debug("Configured Chrome options for headless Brave browser")
        try:
            service = Service("/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.debug("Initialized WebDriver successfully")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            raise RuntimeError("Failed to launch Brave with Selenium") from e
        self.stop_spinner = False
        spinner = threading.Thread(target=self.spinning_cursor)
        spinner.start()
        svg_d, duration_seconds = None, 0
        try:
            logging.debug(f"Navigating to URL: {self.url}")
            driver.get(self.url)
            wait = WebDriverWait(driver, 30)
            logging.debug("Waiting for SVG heatmap element")
            heatmap_el = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-heat-map-path"))
            )
            svg_d = heatmap_el.get_attribute("d")
            logging.debug(f"Extracted SVG path data: {svg_d[:100]}...")  # Log first 100 chars
            # def get_duration_text(driver):
            #     try:
            #         logging.debug(f"Ia m in the get duration function")
            #         txt = driver.find_element(By.CSS_SELECTOR, ".ytp-time-duration").text.strip()
            #         return txt if txt else False
            #     except Exception as e:
            #         logging.debug(f"Duration text not found yet: {e}")
            #         return False
            # logging.debug("Waiting for video duration text")
            # duration_txt = wait.until(get_duration_text)
            # logging.debug(f"Extracted duration text: {duration_txt}")
            # duration_seconds = self.convert_duration_to_seconds(duration_txt)
        except Exception as e:
            logging.error(f"Error during SVG: {e}")
        finally:
            self.stop_spinner = True
            spinner.join()
            sys.stdout.write("\rPage Loaded! ✅\n")
            driver.quit()
            logging.debug("WebDriver session ended")
        return svg_d