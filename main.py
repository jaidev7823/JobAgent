import asyncio
import requests
import sqlite3
from datetime import datetime
from playwright.async_api import async_playwright

OLLAMA_MODEL = "ministral-3:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"
DB_NAME = "db/jobagent.db"


# -------------------------
# OLLAMA
# -------------------------
def ask_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def select_website() -> str:
    prompt = """
Respond ONLY with a full valid URL.
Pick one popular technology learning website.
Example: https://example.com
No explanation.
"""
    url = ask_ollama(prompt)

    if not url.startswith("http"):
        return "https://example.com"

    return url


def summarize_content(content: str) -> str:
    prompt = f"""
Summarize the following website content in 5 bullet points:

{content[:8000]}
"""
    return ask_ollama(prompt)


# -------------------------
# DATABASE
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS website_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(website: str, summary: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO website_summaries (website, summary, created_at)
        VALUES (?, ?, ?)
    """, (website, summary, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


# -------------------------
# MAIN WORKFLOW
# -------------------------
async def main():
    init_db()

    website = select_website()
    print(f"\nSelected website: {website}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Opening website...")
        await page.goto(website, timeout=60000, wait_until="networkidle")

        print("Extracting content...")
        content = await page.evaluate("""
        () => {
            return document.body.innerText;
        }
        """)

        print("Summarizing...")
        summary = summarize_content(content)

        print("\n--- SUMMARY ---\n")
        print(summary)

        print("\nSaving to SQLite...")
        save_to_db(website, summary)

        await browser.close()

    print("\nDone. Data stored in jobagent.db")


if __name__ == "__main__":
    asyncio.run(main())
