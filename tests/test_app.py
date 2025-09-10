import unittest
import os
import pandas as pd
import json
from app import create_app, db
from app.main import Trade
from datetime import datetime, timedelta

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """Set up test client and temporary database."""
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_trades.db'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists('test_trades.db'):
            os.remove('test_trades.db')

    def test_index_route(self):
        """Test the index route renders correctly."""
        # Create a sample signals.csv with 10 rows
        dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
        data = {
            'Date': dates,
            'Close': [150.0 + i * 0.5 for i in range(10)],
            'SMA_50': [149.0 + i * 0.5 for i in range(10)],
            'SMA_200': [148.0 + i * 0.5 for i in range(10)],
            'Signal': [1 if i % 2 == 0 else -1 for i in range(10)]
        }
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        os.makedirs('data', exist_ok=True)
        df.set_index('Date').to_csv('data/signals.csv')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stock Trading Bot: AAPL Analysis', response.data)
        self.assertIn(b'graphJSON', response.data)
        self.assertIn(b'Trade Logs', response.data)

    def test_index_route_no_signals_file(self):
        """Test index route when signals.csv is missing."""
        if os.path.exists('data/signals.csv'):
            os.remove('data/signals.csv')
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Error: Please run analyze.py to generate signals.csv', response.data)

    def test_save_trade(self):
        """Test saving a trade via /save_trade endpoint."""
        trade_data = {
            'ticker': 'AAPL',
            'signal': 1,
            'price': 150.25
        }
        response = self.client.post('/save_trade', json=trade_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('trade_id', response.json)

        with self.app.app_context():
            trade = Trade.query.first()
            self.assertIsNotNone(trade)
            self.assertEqual(trade.ticker, 'AAPL')
            self.assertEqual(trade.signal, 1)
            self.assertEqual(trade.price, 150.25)

    def test_save_trade_invalid_data(self):
        """Test /save_trade with invalid data."""
        # Test empty ticker
        trade_data = {
            'ticker': '',
            'signal': 1,
            'price': 150.25
        }
        response = self.client.post('/save_trade', json=trade_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['message'], 'Ticker cannot be empty.')

        # Test invalid signal
        trade_data = {
            'ticker': 'AAPL',
            'signal': 2,
            'price': 150.25
        }
        response = self.client.post('/save_trade', json=trade_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['message'], 'Signal must be 0 (Hold), 1 (Buy), or -1 (Sell).')

        # Test invalid price
        trade_data = {
            'ticker': 'AAPL',
            'signal': 1,
            'price': -10
        }
        response = self.client.post('/save_trade', json=trade_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['message'], 'Price must be a positive number.')

    def test_static_file_serving(self):
        """Test serving plotly.min.js."""
        os.makedirs('app/static', exist_ok=True)
        with open('app/static/plotly.min.js', 'w') as f:
            f.write('dummy content')
        
        response = self.client.get('/static/plotly.min.js')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'dummy content')

    def test_trade_logs_display(self):
        """Test trade logs are displayed in the index page."""
        with self.app.app_context():
            trade = Trade(ticker='AAPL', signal=1, price=150.25)
            db.session.add(trade)
            db.session.commit()

        # Create a sample signals.csv with 10 rows
        dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
        data = {
            'Date': dates,
            'Close': [150.0 + i * 0.5 for i in range(10)],
            'SMA_50': [149.0 + i * 0.5 for i in range(10)],
            'SMA_200': [148.0 + i * 0.5 for i in range(10)],
            'Signal': [1 if i % 2 == 0 else -1 for i in range(10)]
        }
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        os.makedirs('data', exist_ok=True)
        df.set_index('Date').to_csv('data/signals.csv')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AAPL', response.data)
        self.assertIn(b'150.25', response.data)
