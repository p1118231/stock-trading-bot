import pandas as pd
import numpy as np
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_indicators(df, prediction_file=None):
    """
    Calculate technical indicators (SMA, RSI) and trading signals, optionally using LSTM predictions.
    
    Args:
        df (pd.DataFrame): DataFrame with stock data (must include 'Close' column).
        prediction_file (str, optional): Path to CSV with LSTM predictions (e.g., 'data/AAPL_predictions.csv').
    
    Returns:
        pd.DataFrame: DataFrame with indicators and signals.
    """
    try:
        if 'Close' not in df.columns:
            logger.error("DataFrame missing 'Close' column")
            return None
        
        # Ensure index is datetime and timezone-naive
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            logger.warning("Index is not datetime; converting to datetime")
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        
        # Calculate SMA (50-day and 200-day)
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Calculate RSI (14-period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Load LSTM predictions if provided
        if prediction_file and os.path.exists(prediction_file):
            try:
                pred_df = pd.read_csv(prediction_file, index_col='Date', parse_dates=['Date'])
                # Ensure pred_df index is timezone-naive
                pred_df.index = pd.to_datetime(pred_df.index, utc=True).tz_localize(None)
                if 'Predicted_Close' in pred_df.columns:
                    df = df.join(pred_df['Predicted_Close'])
                    logger.info(f"Loaded LSTM predictions from {prediction_file}")
                else:
                    logger.warning(f"No 'Predicted_Close' column in {prediction_file}")
            except Exception as e:
                logger.warning(f"Failed to load predictions from {prediction_file}: {e}")
        else:
            logger.warning(f"Prediction file {prediction_file} not found; skipping LSTM predictions")
        
        # Generate trading signals
        df['Signal'] = 0
        # Basic SMA + RSI signals
        df['Signal'] = np.where((df['SMA_50'] > df['SMA_200']) & (df['RSI'] < 30), 1, df['Signal'])
        df['Signal'] = np.where((df['SMA_50'] < df['SMA_200']) & (df['RSI'] > 70), -1, df['Signal'])
        
        # Enhance with LSTM predictions (if available)
        if 'Predicted_Close' in df.columns:
            # Buy if predicted price is 5% higher than current, sell if 5% lower
            df['Signal'] = np.where(
                (df['Predicted_Close'] > df['Close'] * 1.05) & (df['SMA_50'] > df['SMA_200']),
                1, df['Signal']
            )
            df['Signal'] = np.where(
                (df['Predicted_Close'] < df['Close'] * 0.95) & (df['SMA_50'] < df['SMA_200']),
                -1, df['Signal']
            )
            logger.info("Incorporated LSTM predictions into trading signals")
        
        os.makedirs('data', exist_ok=True)
        # Save with explicit datetime format, timezone-naive
        df.to_csv('data/signals.csv', date_format='%Y-%m-%d')
        logger.info("Calculated indicators and signals, saved to data/signals.csv")
        return df
    
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None

if __name__ == '__main__':
    try:
        df = pd.read_csv('data/AAPL_historical.csv', index_col='Date', parse_dates=['Date'])
        # Ensure input index is timezone-naive
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        df = calculate_indicators(df, prediction_file='data/AAPL_predictions.csv')
        if df is not None:
            # Only include columns that exist in the DataFrame
            columns = ['Close', 'SMA_50', 'SMA_200', 'RSI', 'Signal']
            if 'Predicted_Close' in df.columns:
                columns.append('Predicted_Close')
            print(df[columns].tail())
    except FileNotFoundError:
        logger.error("Historical data file not found. Run fetch_data.py first.")
    except Exception as e:
        logger.error(f"Error in main: {e}")
