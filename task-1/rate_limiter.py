import asyncio

MIN_INTERVAL = 2.0  # Minimum seconds between requests
MAX_RETRIES = 3     # Number of retry attempts
BACKOFF = 1.5       # Multiplier for exponential backoff

async def delay(seconds=MIN_INTERVAL):
    """Sleep for specified seconds."""
    await asyncio.sleep(seconds)

async def retry(func, max_attempts=MAX_RETRIES):
    """Execute func with retries and exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = MIN_INTERVAL * (BACKOFF ** attempt)
                print(f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"All {max_attempts} attempts failed.")
                raise
