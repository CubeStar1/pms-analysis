import os
import re
from playwright.async_api import Playwright, async_playwright, expect
import asyncio
import pandas as pd

async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.shepherdshill.in/showpmsperformance")

    # Get all options for the first dropdown, excluding the empty value
    options = await page.eval_on_selector_all("select[name=\"pms1\"] option", "options => options.map(option => ({value: option.value, text: option.textContent})).filter(option => option.value)")
    options = [option for option in options if option['value']!= '']
    # Define the constant value for the second dropdown (assuming it is valid)
    constant_pms2_value = '17513'  # Replace this with the actual constant value you want to use

    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.mkdir('data')

    # Loop through all valid options for the first dropdown
    for option in options:
        manager_name = option['text'].replace(' ', '_')
        manager_dir = os.path.join('data', manager_name)

        # Create a directory for each manager if it doesn't exist
        if not os.path.exists(manager_dir):
            os.mkdir(manager_dir)

        await page.locator("select[name=\"pms1\"]").select_option(option['value'])
        await page.locator("select[name=\"pms2\"]").select_option(constant_pms2_value)
        await page.locator("#pms_tool_submit_btn").click()
        await page.wait_for_selector(".table-data", timeout=10000)

        # Extract tables
        tables = await page.eval_on_selector_all("table", "(tables) => tables.map((table) => table.outerHTML)")

        # Parse the table's HTML into a DataFrame and save to CSV
        for i, table in enumerate(tables):
            df = pd.read_html(table)[0]
            df_single = df.iloc[:, [0, 1]]  # Extract only the columns related to the first manager
            filename = os.path.join(manager_dir, f"{option['text']}table_{i}.csv")
            df_single.to_csv(filename, index=False)
            print(f"Saved {filename}")

    await context.close()
    await browser.close()

async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
