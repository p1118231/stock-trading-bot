import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_data(df, lookback=60, target_col='Close'):
    """
    Prepare data for LSTM model.
    
    Args:
        df (pd.DataFrame): DataFrame with stock data (must include target_col).
        lookback (int): Number of time steps to look back for prediction.
        target_col (str): Column to predict (e.g., 'Close').
    
    Returns:
        tuple: Scaled data, scaler, and sequences (X, y).
    """
    try:
        if target_col not in df.columns:
            logger.error(f"{target_col} column missing in DataFrame")
            return None, None, None, None
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df[[target_col]])
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i, 0])
        
        X = np.array(X)
        y = np.array(y)
        logger.info(f"Prepared {len(X)} sequences with {lookback} lookback periods")
        return scaled_data, scaler, X, y
    except Exception as e:
        logger.error(f"Error preparing data: {e}")
        return None, None, None, None

def build_lstm_model(input_shape):
    """
    Build and compile LSTM model.
    
    Args:
        input_shape (tuple): Shape of input data (lookback, features).
    
    Returns:
        keras.Model: Compiled LSTM model.
    """
    try:
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(50))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        logger.info("Built and compiled LSTM model")
        return model
    except Exception as e:
        logger.error(f"Error building LSTM model: {e}")
        return None

def predict_prices(ticker, lookback=60, epochs=10):
    """
    Predict future stock prices using LSTM.
    
    Args:
        ticker (str): Stock ticker (e.g., 'AAPL').
        lookback (int): Number of time steps for LSTM input.
        epochs (int): Number of training epochs.
    
    Returns:
        pd.DataFrame: DataFrame with predicted prices.
    """
    try:
        df = pd.read_csv(f'data/{ticker}_historical.csv', index_col='Date', parse_dates=True)
        if df.empty:
            logger.error(f"No data found for {ticker}")
            return None
        
        # Prepare data
        scaled_data, scaler, X, y = prepare_data(df, lookback=lookback)
        if scaled_data is None:
            return None
        
        # Split data (80% train, 20% test)
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Build and train model
        model = build_lstm_model((lookback, 1))
        if model is None:
            return None
        model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=1)
        
        # Predict
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)
        
        # Create DataFrame with predictions
        pred_dates = df.index[train_size + lookback:]
        pred_df = pd.DataFrame(predictions, columns=['Predicted_Close'], index=pred_dates[:len(predictions)])
        df = df.join(pred_df)
        
        # Save predictions
        os.makedirs('data', exist_ok=True)
        df.to_csv(f'data/{ticker}_predictions.csv')
        logger.info(f"Saved predictions to data/{ticker}_predictions.csv")
        return df
    
    except Exception as e:
        logger.error(f"Error predicting prices for {ticker}: {e}")
        return None

if __name__ == '__main__':
    df = predict_prices('AAPL', lookback=60, epochs=10)
    if df is not None:
        print(df[['Close', 'Predicted_Close']].tail())
