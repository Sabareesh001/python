import asyncio
from scraper import scrape
from datetime import datetime
from db import bulkUpsert, getConnection
from rate_limiter import delay
import csv
import os

async def main():
    start = datetime.now()
    price_changes = []
    link = "https://www.flipkart.com/search?q=table%20lights&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page="
    buffer = []
    count = 0
    connection = await getConnection()
    MAX_PAGES = 20
    
    for i in range(1, MAX_PAGES + 1, 4):
        batch = asyncio.gather(*(scrape(f"{link}{page}", page, MAX_PAGES) for page in range(i, min(i + 4, MAX_PAGES + 1))))
        results = await batch
        for result in results:
            buffer.extend(result)
        await bulkUpsert(buffer, connection, price_changes)
        count += len(buffer)
        buffer.clear()
        
        # Wait between batches
        if i + 4 <= MAX_PAGES:
            await delay(3.0)
    
    end = datetime.now()
    now = end.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] Total: {count} products saved to DB")
    print(f"time taken : {(end-start).total_seconds()} seconds")
    

    # Export price changes to CSV
    export_price_changes_to_csv(price_changes)
    
def export_price_changes_to_csv(price_changes):
    """Export price changes to CSV file in the reports directory"""
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_file = os.path.join(reports_dir, f"{timestamp}.csv")
    change_count = 0;
    # Write CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['Product', 'Old Price', 'New Price', 'Change'])
        
        # Write data rows
        for change in price_changes:
            product_name = change['name']
            old_price = change['old_price']
            new_price = change['new_price']
            price_diff = change['change']
            
            # Calculate percentage change
            if old_price != 0:
                percent_change = (price_diff / old_price) * 100
            else:
                percent_change = 0
            
            if percent_change!=0 :
                change_count+=1

            # Format change as percentage with sign
            if percent_change >= 0:
                change_str = f"+{percent_change:.1f}%"
            else:
                change_str = f"{percent_change:.1f}%"
            
            # Format prices as currency
            old_price_str = f"{old_price:,.2f}"
            new_price_str = f"{new_price:,.2f}"
            print(product_name, old_price_str, new_price_str, change_str)
            writer.writerow([product_name, old_price_str, new_price_str, change_str])
    
    print(f"\n{change_count} price changes detected. Report saved to {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())

# time taken - synchronous - headed = 50seconds 
# time taken - synchronous - headless = 38seconds 