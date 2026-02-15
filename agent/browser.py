import undetected_chromedriver as uc
import shutil

# This script finds interactive elements and overlays a visible number on them
INJECT_NUMBERS = """
(function() {
    // Remove any existing labels first
    const existingLabels = document.querySelectorAll('.ai-label');
    existingLabels.forEach(el => el.remove());

    const selectors = 'a, button, input, select, textarea, [role="button"]';
    const elements = document.querySelectorAll(selectors);
    
    let count = 0;
    elements.forEach((el) => {
        // Only label visible elements
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden') {
            
            // 1. Set the attribute so the code can click it later
            el.setAttribute('data-ai-idx', count);
            
            // 2. Create a visual label for the screenshot
            const label = document.createElement('div');
            label.className = 'ai-label';
            label.innerText = count;
            label.style.position = 'fixed';
            label.style.top = rect.top + 'px';
            label.style.left = rect.left + 'px';
            label.style.backgroundColor = 'red';
            label.style.color = 'white';
            label.style.padding = '2px 5px';
            label.style.fontSize = '12px';
            label.style.fontWeight = 'bold';
            label.style.zIndex = '9999999';
            label.style.pointerEvents = 'none'; // Don't block clicks
            label.style.borderRadius = '3px';
            
            document.body.appendChild(label);
            count++;
        }
    });
})();
"""

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