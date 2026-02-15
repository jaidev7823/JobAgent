import undetected_chromedriver as uc
import shutil
from shortcut import INJECT_NUMBERS, REMOVE_NUMBERS 

# This script finds interactive elements and overlays a visible number on them

class BrowserAgent:
    def __init__(self):
        options = uc.ChromeOptions()

        # Use system chromium if available
        chrome_path = shutil.which("chromium") or shutil.which("google-chrome")
        if chrome_path:
            options.binary_location = chrome_path

        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = uc.Chrome(options=options)

    def open(self, url):
        self.driver.get(url)
        # Give the page a moment to load
        self.driver.implicitly_wait(5)

    def inject_numbers(self):
        self.driver.execute_script(INJECT_NUMBERS)

    def screenshot(self, name):
        import os
        os.makedirs("agent/output/screenshots", exist_ok=True)
        path = f"agent/output/screenshots/{name}.png"
        self.driver.save_screenshot(path)
        return path

    def click_index(self, idx):
        # We use a script to click based on our custom attribute
        self.driver.execute_script(f"""
            const el = document.querySelector('[data-ai-idx="{idx}"]');
            if (el) {{
                el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                el.click();
            }}
        """)

    def scroll(self):
        self.driver.execute_script("window.scrollBy(0, 800);")

    def get_text(self):
        return self.driver.find_element("tag name", "body").text

    def close(self):
        self.driver.quit()