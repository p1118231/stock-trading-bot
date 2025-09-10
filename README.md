Stock Trading Bot
A Flask-based web application for visualizing AAPL stock data and managing trade logs. The app displays a Plotly chart with stock prices, moving averages, and trading signals, and allows users to log trades in a SQLite database.
Project Structure
stock-trading-bot/
├── run.py              # Entry point for the Flask app
├── app/
│   ├── __init__.py     # Flask app and database initialization
│   ├── main.py         # Core routes and logic
│   ├── static/
│   │   └── plotly.min.js # Plotly library for charts
│   └── templates/
│       └── index.html  # Main page with chart and trade form
├── tests/
│   └── test_app.py     # Unit tests for Flask app
├── data/
│   └── signals.csv     # Stock data and signals
├── src/
│   ├── fetch_data.py   # Fetches stock data
│   ├── ml_predict.py   # Generates predictions
│   ├── analyze.py      # Creates trading signals
│   └── check_signals.py # Validates signals.csv
└── requirements.txt    # Python dependencies

Features

Stock Chart: Displays AAPL stock prices, 50-day and 200-day SMAs, buy/sell signals, and predicted prices using Plotly.
Trade Logs: Allows users to add trades (ticker, signal, price) via a form, stored in a SQLite database (trades.db).
Real-Time Updates: Trade table updates dynamically without page refresh.
Error Handling: Robust validation and user feedback for chart rendering and trade submission.
Unit Tests: Tests for routes, database operations, and static file serving.

Prerequisites

Python 3.12+
pip
Git

Setup

Clone the Repository:
git clone <repository-url>
cd stock-trading-bot


Install Dependencies:
pip install -r requirements.txt


Download Plotly:
mkdir -p app/static
curl -o app/static/plotly.min.js https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js
chmod 644 app/static/plotly.min.js


Generate Stock Data:
python src/fetch_data.py
python src/ml_predict.py
python src/analyze.py
python src/check_signals.py

This creates data/signals.csv with stock prices, SMAs, signals, and predictions.


Running the App

Start the Flask App:
python run.py


Access the App:

Open http://127.0.0.1:5000 in a browser.
View the AAPL stock chart and trade logs table.
Use the form to add trades (e.g., Ticker: AAPL, Signal: Buy, Price: 150.25).



Running Tests

Set PYTHONPATH:
export PYTHONPATH=$PYTHONPATH:/Users/breezy/Desktop/stock-trading-bot


Run Tests:
pytest tests/test_app.py -v

Or:
python -m pytest tests/test_app.py -v

Expected output:
============================= test session starts =============================
...
tests/test_app.py::TestFlaskApp::test_index_route PASSED
tests/test_app.py::TestFlaskApp::test_index_route_no_signals_file PASSED
tests/test_app.py::TestFlaskApp::test_save_trade PASSED
tests/test_app.py::TestFlaskApp::test_save_trade_invalid_data PASSED
tests/test_app.py::TestFlaskApp::test_static_file_serving PASSED
tests/test_app.py::TestFlaskApp::test_trade_logs_display PASSED
============================= 6 passed in X.XXs =============================



Troubleshooting

Chart Fails to Load:

Verify app/static/plotly.min.js exists:ls -l app/static/plotly.min.js
head -c 100 app/static/plotly.min.js


Re-download if missing:curl -o app/static/plotly.min.js https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js




Trade Table Empty:

Add trades via the form at http://127.0.0.1:5000.
Check trades.db in the project root for stored trades.


Test Failures:

Ensure data/signals.csv exists and has at least 10 rows.
Check terminal output from pytest and browser console (right-click > Inspect > Console).



Future Enhancements

Automate trade saving from signals.csv.
Add tests for src/ scripts.
Package the app with Docker.

License
MIT License