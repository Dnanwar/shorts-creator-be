import sys
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Extarctor:
    def __init__(self, url):
        self.stop_spinner = False
        self.url = url

    def spinning_cursor(self):
        """Displays a spinner in the terminal until self.stop_spinner is True."""
        while not self.stop_spinner:
            for cursor in "|/-\\":
                sys.stdout.write(f"\rLoading... {cursor}")
                sys.stdout.flush()
                time.sleep(0.1)

    def convert_duration_to_seconds(self, duration: str) -> int:
        """Safely convert 'hh:mm:ss' or 'mm:ss' into total seconds."""
        try:
            parts = [int(p) for p in duration.split(":")]
            if len(parts) == 3:
                return parts[0]*3600 + parts[1]*60 + parts[2]
            if len(parts) == 2:
                return parts[0]*60 + parts[1]
        except (ValueError, AttributeError):
            pass
        return 0

    def get_svg_string_and_duration_in_sec(self):
        """Fetch YouTube, wait for elements, extract heatmap 'd' and duration in seconds."""
        chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
        driver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        # Sanity checks
        if not os.path.exists(chrome_bin):
            raise FileNotFoundError(f"Chromium binary not found: {chrome_bin}")
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"chromedriver not found: {driver_path}")

        # Setup Chrome in headless mode
        chrome_options = Options()
        chrome_options.binary_location = chrome_bin
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,1696")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(self.url)

        # Spinner
        self.stop_spinner = False
        spinner = threading.Thread(target=self.spinning_cursor)
        spinner.start()

        try:
            # Wait up to 30s for the heatmap path element to appear
            wait = WebDriverWait(driver, 30)

            heatmap_el = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-heat-map-path"))
            )
            svg_d = heatmap_el.get_attribute("d")

            # Wait until the duration text is present and non-empty
            def non_empty_duration(drv):
                txt = drv.find_element(By.CSS_SELECTOR, ".ytp-time-duration").text.strip()
                return txt if txt else False

            duration_txt = wait.until(non_empty_duration)
            duration_seconds = self.convert_duration_to_seconds(duration_txt)

        except Exception as e:
            print("Error extracting SVG or duration:", e)
            svg_d, duration_seconds = None, 0

        finally:
            # Stop and clear spinner
            self.stop_spinner = True
            spinner.join()
            sys.stdout.write("\rPage Loaded! ✅\n")
            driver.quit()

        return svg_d, duration_seconds
