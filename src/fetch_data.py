#!/usr/bin/env python
# coding: utf-8



# In[8]:


import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import logging
import os
from retrying import retry

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=30000)
def fetch_historical_data(ticker, start_date, end_date, interval='1d'):
    """
    Fetch historical stock data for a given ticker with retries.
    
    Args:
        ticker (str): Stock ticker (e.g., 'AAPL').
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        interval (str): Data interval (e.g., '1d' for daily, '1h' for hourly).
    
    Returns:
        pd.DataFrame: Historical stock data.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, interval=interval, auto_adjust=True)
        if df.empty:
            logger.error(f"No historical data retrieved for {ticker}")
            return None
        os.makedirs('data', exist_ok=True)
        df.to_csv(f'data/{ticker}_historical.csv')
        logger.info(f"Fetched historical data for {ticker}, saved to data/{ticker}_historical.csv")
        return df
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        raise

@retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=30000)
def fetch_realtime_data(ticker, duration_seconds=3600, interval_seconds=60):
    """
    Fetch real-time stock data by polling at regular intervals.
    
    Args:
        ticker (str): Stock ticker.
        duration_seconds (int): Total duration to fetch data (in seconds).
        interval_seconds (int): Polling interval (in seconds).
    
    Returns:
        pd.DataFrame: Real-time stock data.
    """
    end_time = time.time() + duration_seconds
    data = []
    
    try:
        stock = yf.Ticker(ticker)
        while time.time() < end_time:
            try:
                quote = stock.history(period='1d', interval='1m', auto_adjust=True)
                if not quote.empty:
                    data.append(quote.iloc[-1:])
                    logger.info(f"Fetched real-time data for {ticker} at {datetime.now()}")
                else:
                    logger.warning(f"No real-time data for {ticker}")
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error fetching real-time data for {ticker}: {e}")
        
        if data:
            df = pd.concat(data)
            os.makedirs('data', exist_ok=True)
            df.to_csv(f'data/{ticker}_realtime.csv')
            logger.info(f"Saved real-time data for {ticker} to data/{ticker}_realtime.csv")
            return df
        else:
            logger.error(f"No real-time data collected for {ticker}")
            return None
    except Exception as e:
        logger.error(f"Error in real-time data collection for {ticker}: {e}")
        return None

if __name__ == '__main__':
    # Use last trading day as end date (avoid weekends)
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # 2025-08-15
    # Test with multiple tickers
    for ticker in ['AAPL', 'GOOGL', 'MSFT']:
        historical_df = fetch_historical_data(ticker, '2020-01-01', end_date)
        if historical_df is not None:
            print(f"{ticker} Historical Data:\n{historical_df.head()}")
        
        # Test real-time data for 5 minutes
        realtime_df = fetch_realtime_data(ticker, duration_seconds=300, interval_seconds=60)
        if realtime_df is not None:
            print(f"{ticker} Real-time Data:\n{realtime_df.head()}")

