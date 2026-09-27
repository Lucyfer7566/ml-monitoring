import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # 1. Login page
        print('Taking screenshot of Airflow login...')
        await page.goto('http://localhost:8080/login/')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='screenshots/airflow_login.png')
        
        # Login
        try:
            await page.fill('input#username', 'admin')
            await page.fill('input#password', 'admin')
            await page.click('input[type="submit"]')
            await page.wait_for_timeout(3000)
        except Exception as e:
            print('Login error:', e)
            
        # 2. DAGs list
        print('Taking screenshot of Airflow DAGs list...')
        await page.goto('http://localhost:8080/home')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/airflow_dags_list.png')
        
        # 3. ml_monitoring_health_check DAG
        print('Taking screenshot of ml_monitoring_health_check...')
        await page.goto('http://localhost:8080/dags/ml_monitoring_health_check/grid')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/airflow_health_check_grid.png')
        
        # 4. ml_training_pipeline DAG
        print('Taking screenshot of ml_training_pipeline...')
        await page.goto('http://localhost:8080/dags/ml_training_pipeline/grid')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/airflow_training_pipeline_grid.png')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
