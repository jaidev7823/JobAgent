from planner import plan_strategy
from browser import BrowserAgent
from vision import decide_action
from logger import log_data
import time
import os

USER_PROMPT = """
Find Indian AI startups funded at Seed stage
with less than 20 employees.
"""

def run():
    plan = plan_strategy(USER_PROMPT)
    goal = plan["goal"]

    browser = BrowserAgent()
    browser.open("https://peakxv.com")

    for step in range(15):  # safety limit
        browser.inject_numbers()
        ss = browser.screenshot(f"step_{step}")

        decision = decide_action(ss, goal)

        if decision["action"] == "click":
            browser.click_index(decision["target"])
            time.sleep(2)

        elif decision["action"] == "scroll":
            browser.scroll()
            time.sleep(1)

        elif decision["action"] == "done":
            page_text = browser.get_text()
            log_data(page_text[:3000])
            break

    browser.close()

if not os.path.exists("outputs/screenshots"):
    os.makedirs("outputs/screenshots")

if __name__ == "__main__":
    run()
