import backtrader as bt
import pandas as pd
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

class SMACrossoverStrategy(bt.Strategy):
    params = (
        ('stop_loss', 0.05),  # 5% stop-loss
        ('take_profit', 0.10),  # 10% take-profit
    )

    def __init__(self):
        self.order = None
        self.entry_price = None
        # Access the signal line directly
        self.signal = self.datas[0].signal
        logger.info("Initialized SMACrossoverStrategy")

    def next(self):
        if self.order:  # Skip if order is pending
            return
        # Ensure signal is numeric
        current_signal = float(self.signal[0]) if self.signal[0] is not None else 0.0
        if not self.position:
            if current_signal == 1.0:  # Buy signal
                self.order = self.buy()
                self.entry_price = self.datas[0].close[0]
                logger.info(f"Buy order placed at {self.entry_price}")
        else:
            if current_signal == -1.0:  # Sell signal
                self.order = self.sell()
                self.entry_price = None
                logger.info("Sell order placed")
            else:
                current_price = self.datas[0].close[0]
                if self.entry_price:
                    if current_price <= self.entry_price * (1 - self.params.stop_loss):
                        self.order = self.sell()
                        logger.info(f"Stop-loss triggered at {current_price}")
                    elif current_price >= self.entry_price * (1 + self.params.take_profit):
                        self.order = self.sell()
                        logger.info(f"Take-profit triggered at {current_price}")

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None

class PandasDataWithSignals(bt.feeds.PandasData):
    # Define lines for backtrader
    lines = ('signal',)
    params = (
        ('datetime', None),  # Auto-detect datetime column (index)
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('signal', 'Signal'),
    )

def run_backtest(ticker, cash=10000.0, commission=0.001):
    try:
        df = pd.read_csv(f'data/{ticker}_historical.csv', index_col='Date', parse_dates=True)
        df = calculate_indicators(df)
        if df is None or df.empty:
            logger.error("Failed to load or process data for backtesting")
            return None

        # Ensure 'Signal' column is numeric
        df['Signal'] = df['Signal'].astype(float)
        cerebro = bt.Cerebro()
        cerebro.addstrategy(SMACrossoverStrategy)
        cerebro.broker.setcash(cash)
        cerebro.broker.setcommission(commission=commission)

        # Add data feed
        data = PandasDataWithSignals(dataname=df)
        cerebro.adddata(data)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        logger.info(f"Starting backtest for {ticker}")
        results = cerebro.run()
        strategy = results[0]

        final_value = cerebro.broker.getvalue()
        returns = strategy.analyzers.returns.get_analysis().get('rtot', 0.0) * 100
        sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', None)
        trades = strategy.analyzers.trades.get_analysis()
        win_rate = (trades.get('won', {}).get('total', 0) / trades.get('total', 1)) * 100 if trades.get('total', 0) > 0 else 0

        result = {
            'final_value': final_value,
            'returns': returns,
            'sharpe_ratio': sharpe,
            'win_rate': win_rate
        }
        logger.info(f"Backtest complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in backtest for {ticker}: {e}")
        return None

if __name__ == '__main__':
    result = run_backtest('AAPL')
    if result:
        print(f"Final Portfolio Value: ${result['final_value']:.2f}")
        print(f"Total Return: {result['returns']:.2f}%")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"Win Rate: {result['win_rate']:.2f}%")
