import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://learn.microsoft.com/en-us/rest/api/fabric/articles/")
        
        # Waiting for the dynamic content to load; adjust selector or timeout as needed
        #await page.wait_for_selector("nav#affixed-left-container", timeout=5000)
        await page.wait_for_selector("ul.tree.table-of-contents", timeout=5000)
        # Get the page content after dynamic rendering
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Locate the <nav> element with the specified id
        #nav = soup.find('nav', id='affixed-left-container')
        ul = soup.find('ul', class_='tree table-of-contents')
        if ul:
            li_elements = ul.find_all('li')
            for li in li_elements:
                print(li.get_text(strip=True))
        else:
            print("No ul.tree.table-of-contents element found.")
        
        await browser.close()

asyncio.run(run())