# Task 1: Async Web Scraper with Rate Limiting

## Overview

An asynchronous web scraper that fetches product data from Flipkart, implements intelligent rate limiting and retry logic, randomizes user agents, and stores results in a PostgreSQL database with efficient batch upserts.

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install playwright asyncpg python-dotenv
playwright install chromium
```

### 3. Configure Database

Copy `.example.env` to `.env` and update with your PostgreSQL credentials:

```bash
cp .example.env .env
```

Then edit `.env`:

```
DB_NAME=your_database_name
DB_USER=your_postgres_user
DB_PASS=your_postgres_password
```

### 4. Run the Scraper

```bash
python main.py
```

## Features

- **Async Scraping**: Concurrent page fetches using asyncio and Playwright
- **Rate Limiting**: Configurable delays between requests to respect server resources
- **Retry Logic**: Automatic retries with exponential backoff for failed requests
- **User Agent Rotation**: Random user agent selection to avoid detection
- **Batch Operations**: Efficient bulk upserts to PostgreSQL database
- **Price Tracking**: Detects and logs price changes for monitored products

## Architecture

- **main.py**: Orchestrates scraping batches and database operations
- **scraper.py**: Handles page fetching and HTML parsing with Playwright
- **db.py**: PostgreSQL connection and data persistence
- **rate_limiter.py**: Request throttling and retry mechanism
- **user_agents.py**: User agent pool for request rotation
