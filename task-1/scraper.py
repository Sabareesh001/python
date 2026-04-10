from datetime import datetime
from playwright.async_api import async_playwright
from rate_limiter import retry
from user_agents import get_user_agent

async def scrape(link, pageNo, totalPages):
    """Scrape a single page with retries."""
    
    async def fetch():
        user_agent = get_user_agent()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=user_agent)
            
            try:
                await page.goto(link, timeout=60000, wait_until="domcontentloaded")
                products = await page.query_selector_all(".nZIRY7")
                
                product_list = []
                for product in products:
                    try:
                        name_elem = await product.query_selector(".pIpigb")
                        price_elem = await product.query_selector(".hZ3P6w")
                        sku_elem = await product.query_selector("a[href*='/p/']")
                        
                        name = await name_elem.get_attribute("title") if name_elem else "N/A"
                        price = await price_elem.inner_text() if price_elem else "N/A"
                        
                        sku = "N/A"
                        if sku_elem:
                            href = await sku_elem.get_attribute("href")
                            if href and '/p/' in href:
                                sku = href.split('/p/')[-1].split('?')[0]
                        
                        product_list.append({
                            "name": name,
                            "price": float(price.strip("₹").replace(",", "")),
                            "sku": sku
                        })
                    except Exception as e:
                        print(f"Error parsing product: {e}")
                        continue
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] Page {str(pageNo).zfill(2)}/{totalPages} — {len(product_list)} products")
                return product_list
            finally:
                await browser.close()
    
    return await retry(fetch)