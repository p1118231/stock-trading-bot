import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Define the stock ticker and date range
ticker = "AAPL"
start_date = "2023-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")  # Dynamic end date (e.g., 2025-09-10)

try:
    # Fetch data from Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date)

    # Select relevant columns
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)

    # Save to CSV
    csv_path = os.path.join("data", "raw_data.csv")
    data.to_csv(csv_path)
    print(f"Data fetched and saved to {csv_path}")
except Exception as e:
    print(f"Error fetching data: {str(e)}")
    raise  # Re-raise to fail the Dockerfile build if it fails
