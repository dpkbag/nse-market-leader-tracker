#!/usr/bin/env python3
"""
NSE Market Leader Tracker - Automates fetching top gainers daily
and maintains a week's history
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

try:
    from nsefin import NSEClient
except ImportError:
    print("Warning: nsefin not installed. Install with: pip install nsefin")

class NSEMarketLeaderTracker:
    def __init__(self, data_dir='nse_market_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / 'weekly_leaders.csv'
        self.nse = NSEClient()
    
    def fetch_top_gainers(self):
        """Fetch top 10 gainers from NSE using nsefin library"""
        try:
            # Get pre-market data with all stocks
            data = self.NSEClient()_info(category="All")
            
            # Get top 10 by percentage change
            if 'pchange' in data.columns:
                gainers = data.nlargest(10, 'pchange')
            elif 'change' in data.columns:
                gainers = data.nlargest(10, 'change')
            else:
                print("Available columns:", data.columns.tolist())
                gainers = data.head(10)
            
            return gainers
        except Exception as e:
            print(f"Error fetching via nsefin: {e}")
            return None
    
    def record_daily_leaders(self):
        """Record today's market leaders"""
        today = datetime.now().date()
        gainers = self.fetch_top_gainers()
        
        if gainers is not None and len(gainers) > 0:
            data = gainers.copy()
            data['date'] = today
            data['rank'] = range(1, len(data) + 1)
            
            if self.history_file.exists():
                existing_data = pd.read_csv(self.history_file)
                combined = pd.concat([existing_data, data], ignore_index=True)
            else:
                combined = data
            
            combined.to_csv(self.history_file, index=False)
            print(f"✓ Recorded {len(data)} leaders for {today}")
            return data
        else:
            print(f"✗ Failed to fetch data for {today}")
            return None
    
    def get_weekly_summary(self):
        """Get market leader summary for last 7 days"""
        if not self.history_file.exists():
            print("No data available yet")
            return None
        
        data = pd.read_csv(self.history_file)
        data['date'] = pd.to_datetime(data['date'])
        
        last_week = datetime.now().date() - timedelta(days=7)
        weekly_data = data[data['date'] >= pd.Timestamp(last_week)]
        
        if len(weekly_data) == 0:
            print("No data for last 7 days")
            return None
        
        # Try to identify symbol column
        symbol_col = None
        for col in ['symbol', 'Symbol', 'SYMBOL', 'Name', 'name']:
            if col in weekly_data.columns:
                symbol_col = col
                break
        
        if symbol_col is None:
            symbol_col = weekly_data.columns[0]
        
        summary = weekly_data.groupby(symbol_col).agg({
            'rank': 'mean',
            'date': 'count'
        }).rename(columns={'date': 'days_in_top10', 'rank': 'avg_rank'})
        
        summary = summary.sort_values('days_in_top10', ascending=False)
        return summary
    
    def print_report(self):
        """Print formatted weekly report"""
        print("\n" + "="*70)
        print("NSE MARKET LEADER REPORT - LAST 7 DAYS")
        print("="*70)
        
        summary = self.get_weekly_summary()
        if summary is not None:
            print("\nStocks appearing most in Top 10 Gainers:")
            print(summary.to_string())
        
        print(f"\nReport generated: {datetime.now()}")
        print("="*70 + "\n")

if __name__ == "__main__":
    tracker = NSEMarketLeaderTracker()
    tracker.record_daily_leaders()
    tracker.print_report()
