import pandas as pd
import numpy as np
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_indicators(df):
    """
    Calculate technical indicators (SMA, RSI) and trading signals.
    
    Args:
        df (pd.DataFrame): DataFrame with stock data (must include 'Close' column).
    
    Returns:
        pd.DataFrame: DataFrame with added columns for indicators and signals.
    """
    try:
        if 'Close' not in df.columns:
            logger.error("DataFrame missing 'Close' column")
            return None
        
        # Simple Moving Averages (50-day and 200-day)
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI (14-period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate trading signals
        df['Signal'] = 0
        df['Signal'] = np.where((df['SMA_50'] > df['SMA_200']) & (df['RSI'] < 30), 1, df['Signal'])
        df['Signal'] = np.where((df['SMA_50'] < df['SMA_200']) & (df['RSI'] > 70), -1, df['Signal'])
        
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/signals.csv')
        logger.info("Calculated indicators and signals, saved to data/signals.csv")
        return df
    
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None

if __name__ == '__main__':
    try:
        df = pd.read_csv('data/AAPL_historical.csv', index_col='Date', parse_dates=True)
        df = calculate_indicators(df)
        if df is not None:
            print(df[['Close', 'SMA_50', 'SMA_200', 'RSI', 'Signal']].tail())
    except FileNotFoundError:
        logger.error("Historical data file not found. Run fetch_data.py first.")
