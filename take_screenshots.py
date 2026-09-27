import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print('Airflow')
        await page.goto('http://localhost:8080')
        try:
            await page.fill('input#username', 'admin')
            await page.fill('input#password', 'admin')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
        except Exception as e:
            print("Login failed or not needed:", e)
        await page.screenshot(path='screenshots/airflow.png')
        
        print('MLflow')
        await page.goto('http://localhost:5000')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/mlflow.png')
        
        print('Prometheus')
        await page.goto('http://localhost:9090/alerts')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/prometheus.png')
        
        print('Alertmanager')
        await page.goto('http://localhost:9093')
        await page.wait_for_timeout(3000)
        await page.screenshot(path='screenshots/alertmanager.png')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
