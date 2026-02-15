import asyncio
import requests
from playwright.async_api import async_playwright

OLLAMA_MODEL = "ministral-3:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------
# OLLAMA HELPER
# -----------------------------
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


# -----------------------------
# STEP 1: Ask Ollama to pick website
# -----------------------------
def select_website() -> str:
    prompt = """
You must respond with ONLY a valid full URL.
Pick one useful public website for learning technology.
Example format: https://example.com
Do not explain anything.
"""
    url = ask_ollama(prompt)

    # Safety validation
    if not url.startswith("http"):
        return "https://example.com"

    return url


# -----------------------------
# STEP 2: Summarize page content
# -----------------------------
def summarize_content(content: str) -> str:
    prompt = f"""
Summarize the following website content in 5 bullet points:

{content[:8000]}
"""
    return ask_ollama(prompt)


# -----------------------------
# MAIN WORKFLOW
# -----------------------------
async def main():
    website = select_website()
    print(f"\nSelected website: {website}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Opening browser...")
        await page.goto(website, timeout=60000)

        print("Extracting content...")
        content = await page.inner_text("body")

        print("Summarizing with Ollama...\n")
        summary = summarize_content(content)

        print("------ SUMMARY ------\n")
        print(summary)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
