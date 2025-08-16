import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging
import os
import sys
# Get the current working directory
current_dir = os.getcwd()
# Add the parent directory to the path (assuming src is in the same directory as your notebook)
sys.path.append(current_dir)
from src.analyze import calculate_indicators

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def plot_trading_signals(ticker):
    try:
        df = pd.read_csv(f'data/{ticker}_historical.csv', index_col='Date', parse_dates=True)
        df = calculate_indicators(df)
        if df is None or df.empty:
            logger.error("Failed to load or process data for visualization")
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='50-day SMA', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], mode='lines', name='200-day SMA', line=dict(color='green')))

        buys = df[df['Signal'] == 1]
        sells = df[df['Signal'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers', name='Buy Signal',
                                marker=dict(symbol='triangle-up', size=10, color='limegreen')))
        fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers', name='Sell Signal',
                                marker=dict(symbol='triangle-down', size=10, color='red')))

        fig.update_layout(
            title=f'{ticker} Stock Price with Trading Signals',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_dark',
            showlegend=True
        )

        fig.write_html(f'data/{ticker}_signals.html')
        logger.info(f"Saved trading signals plot to data/{ticker}_signals.html")
        return fig

    except Exception as e:
        logger.error(f"Error creating trading signals plot for {ticker}: {e}")
        return None

def plot_backtest_performance(ticker, backtest_results):
    try:
        df = pd.read_csv(f'data/{ticker}_historical.csv', index_col='Date', parse_dates=True)
        portfolio_value = [10000 + i * 100 for i in range(len(df))]  # Placeholder

        fig = px.line(x=df.index, y=portfolio_value, title=f'{ticker} Portfolio Value Over Time')
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Portfolio Value (USD)',
            template='plotly_dark'
        )

        annotations = [
            dict(x=0.5, y=0.95, xref="paper", yref="paper",
                 text=f"Final Value: ${backtest_results['final_value']:.2f}", showarrow=False),
            dict(x=0.5, y=0.90, xref="paper", yref="paper",
                 text=f"Return: {backtest_results['returns']:.2f}%", showarrow=False),
            dict(x=0.5, y=0.85, xref="paper", yref="paper",
                 text=f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}", showarrow=False)
        ]
        fig.update_layout(annotations=annotations)

        fig.write_html(f'data/{ticker}_portfolio.html')
        logger.info(f"Saved portfolio value plot to data/{ticker}_portfolio.html")
        return fig

    except Exception as e:
        logger.error(f"Error creating portfolio value plot for {ticker}: {e}")
        return None

if __name__ == '__main__':
    ticker = 'AAPL'
    plot_trading_signals(ticker)
    from src.backtest import run_backtest
    results = run_backtest(ticker)
    if results:
        plot_backtest_performance(ticker, results)
