import asyncpg,os
import dotenv
dotenv.load_dotenv()

async def getConnection():
    connection = await asyncpg.connect(dsn="postgres://",host="localhost",database=os.getenv("DB_NAME"),user=os.getenv("DB_USER"),password=os.getenv("DB_PASS"),port=5432)
    return connection

async def bulkUpsert(queue,connection,price_changes):
    values = []
    for product in queue:
        values.append((product["sku"], product["name"], product["price"]))
    select = await bulkSelect([p["sku"] for p in queue], connection)
    old_prices = {}
    for row in select:
        old_prices[row["sku"]] = row["price"]

    # Track price changes
    for product in queue:
        if product["sku"] in old_prices:
            old_price = old_prices[product["sku"]]
            new_price = product["price"]
            change = new_price - old_price
            price_changes.append({
                "name": product["name"],
                "old_price": old_price,
                "new_price": new_price,
                "change": change
            })

    # Build a query with placeholders
    query = '''INSERT INTO products (sku, name, price) VALUES ($1, $2, $3) 
               ON CONFLICT (sku) DO UPDATE 
               SET name = EXCLUDED.name, price = EXCLUDED.price'''

    async with connection.transaction():
        # Execute each insert with a loop of parameters
        await connection.executemany(query, values)
async def bulkSelect(skus,connection):
    query = '''SELECT sku, price FROM products WHERE sku = ANY($1)'''
    # Use a single fetch to return all matching rows
    return await connection.fetch(query, skus)
