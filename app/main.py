from flask import Blueprint, render_template, request, jsonify
from . import db
import pandas as pd
import os
import plotly
import plotly.graph_objects as go
import json
import logging
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    signal = db.Column(db.Integer, nullable=False)  # 1: Buy, -1: Sell, 0: Hold
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@main.route('/', methods=['GET', 'POST'])
def index():
    try:
        # Check if signals.csv exists
        signals_file = 'data/signals.csv'
        if not os.path.exists(signals_file):
            logger.error(f"{signals_file} not found. Run analyze.py first.")
            return "Error: Please run analyze.py to generate signals.csv."

        # Load signals data
        df = pd.read_csv(signals_file, index_col='Date', parse_dates=True)
        if df.empty:
            logger.error("signals.csv is empty.")
            return "Error: signals.csv is empty."

        # Validate required columns
        required_columns = ['Close', 'SMA_50', 'SMA_200', 'Signal']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing columns in signals.csv: {missing_columns}")
            return f"Error: Missing columns in signals.csv: {missing_columns}"

        # Validate data types and handle NaN values
        for col in required_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                logger.error(f"Column {col} contains non-numeric data.")
                return f"Error: Column {col} in signals.csv contains non-numeric data."
        
        # Drop rows with NaN in required columns
        original_len = len(df)
        df = df.dropna(subset=required_columns)
        if df.empty:
            logger.error(f"All rows in signals.csv contain NaN values in required columns.")
            return "Error: No valid data in signals.csv after removing NaN values."
        if len(df) < 10:
            logger.error(f"Too few valid rows ({len(df)}) after dropping NaN values.")
            return f"Error: Too few valid rows ({len(df)}) in signals.csv for plotting."
        if len(df) < original_len:
            logger.warning(f"Dropped {original_len - len(df)} rows with NaN values.")

        # Ensure index is datetime
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            logger.warning("Date index is not datetime; attempting to convert")
            df.index = pd.to_datetime(df.index, errors='coerce')
            if df.index.isna().any():
                logger.error("Failed to convert Date index to datetime.")
                return "Error: Invalid date format in signals.csv."

        # Create Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='50-day SMA', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], mode='lines', name='200-day SMA', line=dict(color='purple')))
        if 'Predicted_Close' in df.columns:
            if pd.api.types.is_numeric_dtype(df['Predicted_Close']):
                pred_df = df.dropna(subset=['Predicted_Close'])
                if not pred_df.empty:
                    fig.add_trace(go.Scatter(x=pred_df.index, y=pred_df['Predicted_Close'], mode='lines', 
                                            name='Predicted Close', line=dict(color='green', dash='dash')))
                else:
                    logger.warning("Predicted_Close column has no valid data after dropping NaN.")
            else:
                logger.warning("Predicted_Close column contains non-numeric data; skipping.")

        # Add buy/sell signals
        buys = df[df['Signal'] == 1]
        sells = df[df['Signal'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers', name='Buy Signal',
                                marker=dict(symbol='triangle-up', size=10, color='limegreen')))
        fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers', name='Sell Signal',
                                marker=dict(symbol='triangle-down', size=10, color='red')))
        
        fig.update_layout(
            title='AAPL Stock Price with Trading Signals and Predictions',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Convert to JSON for rendering
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        logger.info(f"Chart JSON generated successfully with {len(df)} valid rows.")
        
        # Get trade logs from database
        trades = Trade.query.all()
        return render_template('index.html', graphJSON=graphJSON, trades=trades)
    except Exception as e:
        logger.error(f"Error in Flask app: {e}")
        return f"Error: {str(e)}"

@main.route('/save_trade', methods=['POST'])
def save_trade():
    try:
        ticker = request.json['ticker']
        signal = request.json['signal']
        price = request.json['price']
        
        trade = Trade(ticker=ticker, signal=signal, price=price)
        db.session.add(trade)
        db.session.commit()
        logger.info(f"Saved trade: {ticker}, {signal}, {price}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving trade: {e}")
        return jsonify({'status': 'error'})

@main.route('/static/<path:filename>')
def static_files(filename):
    try:
        logger.info(f"Serving static file: {filename}")
        return send_from_directory('static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return "Static file not found", 404
