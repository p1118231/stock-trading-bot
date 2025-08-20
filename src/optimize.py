import backtrader as bt
import pandas as pd
import numpy as np
import logging
import os
import sys
# Get the current working directory
current_dir = os.getcwd()
# Add the parent directory to the path
sys.path.append(os.path.dirname(current_dir))
from analyze import calculate_indicators
from backtest import SMACrossoverStrategy, PandasDataWithSignals

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_strategy(ticker, cash=10000.0, commission=0.001):
    """
    Optimize trading strategy parameters (SMA windows) for maximum returns.
    
    Args:
        ticker (str): Stock ticker (e.g., 'AAPL').
        cash (float): Initial capital.
        commission (float): Trading commission rate.
    
    Returns:
        dict: Best parameters and performance metrics.
    """
    try:
        df = pd.read_csv(f'data/{ticker}_historical.csv', index_col='Date', parse_dates=True)
        if df.empty:
            logger.error(f"No data found for {ticker}")
            return None
        
        # Calculate indicators (including RSI) before optimization
        df = calculate_indicators(df)
        if df is None:
            logger.error("Failed to calculate indicators")
            return None
        
        best_result = {'returns': float('-inf'), 'params': None}
        sma_50_range = [30, 50, 70]
        sma_200_range = [150, 200, 250]

        for sma_50 in sma_50_range:
            for sma_200 in sma_200_range:
                if sma_50 >= sma_200:
                    continue  # Skip invalid combinations
                # Recalculate SMAs with current parameters
                temp_df = df.copy()
                temp_df['SMA_50'] = temp_df['Close'].rolling(window=sma_50).mean()
                temp_df['SMA_200'] = temp_df['Close'].rolling(window=sma_200).mean()
                temp_df['Signal'] = 0
                temp_df['Signal'] = np.where(
                    (temp_df['SMA_50'] > temp_df['SMA_200']) & (temp_df['RSI'] < 30), 1, temp_df['Signal']
                )
                temp_df['Signal'] = np.where(
                    (temp_df['SMA_50'] < temp_df['SMA_200']) & (temp_df['RSI'] > 70), -1, temp_df['Signal']
                )
                
                # Run backtest
                cerebro = bt.Cerebro()
                cerebro.addstrategy(SMACrossoverStrategy)
                cerebro.broker.setcash(cash)
                cerebro.broker.setcommission(commission=commission)
                
                data = PandasDataWithSignals(dataname=temp_df)
                cerebro.adddata(data)
                cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
                
                logger.info(f"Testing SMA_50={sma_50}, SMA_200={sma_200}")
                results = cerebro.run()
                strategy = results[0]
                returns = strategy.analyzers.returns.get_analysis().get('rtot', 0.0) * 100
                
                if returns > best_result['returns']:
                    best_result = {
                        'returns': returns,
                        'final_value': cerebro.broker.getvalue(),
                        'params': {'sma_50': sma_50, 'sma_200': sma_200}
                    }
                    logger.info(f"New best result: {best_result}")
        
        os.makedirs('data', exist_ok=True)
        with open(f'data/{ticker}_optimization.txt', 'w') as f:
            f.write(str(best_result))
        logger.info(f"Saved optimization results to data/{ticker}_optimization.txt")
        return best_result
    
    except Exception as e:
        logger.error(f"Error optimizing strategy for {ticker}: {e}")
        return None

if __name__ == '__main__':
    result = optimize_strategy('AAPL')
    if result:
        print(f"Best Parameters: SMA_50={result['params']['sma_50']}, SMA_200={result['params']['sma_200']}")
        print(f"Returns: {result['returns']:.2f}%")
        print(f"Final Portfolio Value: ${result['final_value']:.2f}")
