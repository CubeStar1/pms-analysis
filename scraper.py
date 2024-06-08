import os
import re
from playwright.async_api import Playwright, async_playwright, expect
import asyncio
import pandas as pd
all_data = pd.DataFrame()
async def scrape_manager(playwright: Playwright, option: dict, constant_pms2_value: str, semaphore: asyncio.Semaphore) -> None:
    global all_data
    # Acquire a permit from the semaphore
    async with semaphore:
        try:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://www.shepherdshill.in/showpmsperformance")

            manager_name = option['text'].replace(' ', '_')
            manager_dir = os.path.join('data', manager_name)

            # Create a directory for each manager if it doesn't exist
            if not os.path.exists(manager_dir):
                os.mkdir(manager_dir)

            await page.locator("select[name=\"pms1\"]").select_option(option['value'])
            await page.locator("select[name=\"pms2\"]").select_option(option['value'])
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
                print(f'{len(df.columns)} for {option["text"]}')

                # Only append the data from the first table to the all_data DataFrame
                if i == 0:
                    if df.shape[1] > 2:
                        # If there are more than 2 columns, select only the first two
                        df = df.iloc[:, :2]
                    # Rename the columns to the manager's name and merge with the all_data DataFrame
                    df.columns = ['Unnamed: 0', option['text']]
                    if all_data.empty:
                        all_data = df
                    else:
                        all_data = pd.merge(all_data, df, on='Unnamed: 0', how='outer')

            # Save the all_data DataFrame to a CSV file after each iteration
            all_data.to_csv('pms_performance_aggregate.csv', index=False)

        except Exception as e:
            print(f"Error processing {option['text']}: {e}")
        finally:
            await context.close()
            await browser.close()
async def main() -> None:
    async with async_playwright() as playwright:
        # Ensure the 'data' directory exists
        if not os.path.exists('data'):
            os.mkdir('data')

        # Get all options for the first dropdown, excluding the empty value
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.shepherdshill.in/showpmsperformance")
        options = await page.eval_on_selector_all("select[name=\"pms1\"] option", "options => options.map(option => ({value: option.value, text: option.textContent})).filter(option => option.value)")
        options = [option for option in options if option['value']!= '']
        print(f'Found {len(options)} options')
        await context.close()
        await browser.close()

        # Define the constant value for the second dropdown (assuming it is valid)
        constant_pms2_value = '17513'  # Replace this with the actual constant value you want to use

        # Create a semaphore with a maximum of 5 concurrent tasks
        semaphore = asyncio.Semaphore(5)

        # Create a list to hold all the tasks
        tasks = []

        # Loop through all valid options for the first dropdown and create a new task for each
        for option in options:
            task = asyncio.create_task(scrape_manager(playwright, option, constant_pms2_value, semaphore))
            tasks.append(task)

        # Run all the tasks concurrently
        await asyncio.gather(*tasks)

asyncio.run(main())