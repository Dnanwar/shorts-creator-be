import sys
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class Extarctor:
    def __init__(self,url):
        self.stop_spinner = False
        self.url = url

    def spinning_cursor(self):
        """Displays a spinner in the terminal until self.stop_spinner is True."""
        while not self.stop_spinner:
            for cursor in "|/-\\":
                sys.stdout.write(f"\rLoading... {cursor}")
                sys.stdout.flush()
                time.sleep(0.1)

    def convert_duration_to_seconds(self, duration):
        parts = duration.split(":")
        parts = [int(p) for p in parts]
        
        if len(parts) == 3:  # Format: hh:mm:ss
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:  # Format: mm:ss
            return parts[0] * 60 + parts[1]
        else:
            return 0

    def get_svg_string_and_duration_in_sec(self):
        """Fetches the YouTube page and extracts the SVG path's 'd' attribute from the heatmap."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode

        # Automatically download and use the latest ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(self.url)

        # Start spinner thread
        self.stop_spinner = False
        spinner_thread = threading.Thread(target=self.spinning_cursor)
        spinner_thread.start()

        # Wait for the page to load (adjust time as necessary)
        time.sleep(5)

        # Stop spinner and wait for thread to finish
        self.stop_spinner = True
        spinner_thread.join()
        sys.stdout.write("\rPage Loaded! ✅\n")

        try:
            # Locate the SVG heat map path element
            heatmap_element = driver.find_element(By.CSS_SELECTOR, ".ytp-heat-map-path")
            svg_string = heatmap_element.get_attribute("d")

            # Extract the video duration
            duration_element = driver.find_element(By.CSS_SELECTOR, ".ytp-time-duration")
            video_duration = duration_element.text.strip()  # Get text inside <span>
            duration_seconds = self.convert_duration_to_seconds(video_duration)
            print("Video Duration:", duration_seconds)

            
            driver.quit()
            return svg_string, duration_seconds
        except Exception as e:
            print("Error extracting SVG:", e)
            driver.quit()
            return None,None


