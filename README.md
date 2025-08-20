Stock Market Analysis and Trading Bot
A Python-based project that fetches stock market data, analyzes it with technical indicators and machine learning, simulates trading strategies, and visualizes results. Features include real-time data integration, risk management, and a Flask web app for user interaction.
Setup Instructions

Clone the repository:
git clone https://github.com/p1118231/stock-trading-bot.git
cd stock-trading-bot


Set up virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Run the Flask app:
python run.py

Open http://127.0.0.1:5000 in your browser.

Run core modules:

Fetch data: python src/fetch_data.py
Analyze data: python src/analyze.py
Backtest strategy: python src/backtest.py
Visualize results: python src/visualize.py
Predict prices: python src/ml_predict.py
Optimize parameters: python src/optimize.py



Project Structure

src/:
fetch_data.py: Fetches historical and real-time stock data using yfinance with retries.
analyze.py: Calculates SMA, RSI, and trading signals, enhanced with LSTM predictions.
backtest.py: Simulates trading with backtrader, including stop-loss and take-profit.
visualize.py: Creates interactive Plotly charts for prices, signals, and performance.
ml_predict.py: Predicts future stock prices using LSTM.
optimize.py: Optimizes SMA window parameters for maximum returns.


data/: Stores stock data, predictions, and visualizations (ignored by .gitignore).
tests/: Unit tests for reliability.
notebooks/: Exploratory data analysis.
app/: Flask web app for deployment.

Notes

Added .gitignore to exclude venv/, data files, and artifacts.
Removed venv/ from Git history to resolve large file issues.
Core implementation complete with robust data fetching, analysis, backtesting, and visualization.
Extensions added: LSTM predictions and parameter optimization.
requirements.txt uses latest package versions for flexibility.

Next Steps

Add unit tests (tests/).
Integrate results into Flask app for web display.
Deploy with Docker.
