import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_signals_file(file_path='data/signals.csv'):
    try:
        if not os.path.exists(file_path):
            logger.error(f"{file_path} does not exist.")
            return False
        
        df = pd.read_csv(file_path, index_col='Date', parse_dates=['Date'])
        if df.empty:
            logger.error(f"{file_path} is empty.")
            return False
        
        logger.info(f"Rows in signals.csv: {len(df)}")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Sample dates: {df.index[:5].tolist()}")
        
        required_columns = ['Close', 'SMA_50', 'SMA_200', 'Signal']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            return False
        
        for col in required_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                logger.error(f"Column {col} contains non-numeric data.")
                return False
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                logger.warning(f"Column {col} has {nan_count} NaN values.")
        
        # Count valid rows (non-NaN in required columns)
        valid_df = df.dropna(subset=required_columns)
        logger.info(f"Valid rows (non-NaN in required columns): {len(valid_df)}")
        
        if 'Predicted_Close' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['Predicted_Close']):
                logger.warning("Predicted_Close contains non-numeric data.")
            nan_count = df['Predicted_Close'].isna().sum()
            if nan_count > 0:
                logger.warning(f"Predicted_Close has {nan_count} NaN values.")
        
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            logger.error("Date index is not in datetime format.")
            return False
        
        logger.info("signals.csv is valid.")
        return True
    
    except Exception as e:
        logger.error(f"Error checking signals.csv: {e}")
        return False

if __name__ == '__main__':
    check_signals_file()
