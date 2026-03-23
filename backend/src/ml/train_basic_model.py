import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sqlalchemy import select

# Handle potential import differences based on project structure
try:
    from src.database import SessionLocal
except ImportError:
    from src.core.config import SessionLocal

from src.models.stock import Ticker, DailyPrice


def main():
    # 1. Connect to DB and fetch historical data
    symbol = 'FPT'  # You can change this to 'AAPL' or target ticker
    print(f"Connecting to database to fetch data for {symbol}...")
    
    with SessionLocal() as db:
        # Fetch the ticker
        stmt_ticker = select(Ticker).where(Ticker.symbol == symbol)
        ticker = db.scalars(stmt_ticker).first()
        
        if not ticker:
            print(f"Error: Ticker '{symbol}' not found in the database.")
            return
        
        # Fetch daily prices strictly ordered by date ascending
        stmt_prices = (
            select(DailyPrice)
            .where(DailyPrice.ticker_id == ticker.id)
            .order_by(DailyPrice.date.asc())
        )
        
        prices_objs = db.scalars(stmt_prices).all()
        
        if not prices_objs:
            print(f"Error: No historical prices found for '{symbol}'.")
            return

    # Convert ORM objects to a Pandas DataFrame
    data = [{
        'Date': p.date,
        'Open': p.open,
        'High': p.high,
        'Low': p.low,
        'Close': p.close,
        'Volume': p.volume
    } for p in prices_objs]
    
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    
    print(f"Loaded {len(df)} rows. Starting Feature Engineering...")
    
    # 2. Feature Engineering
    # Calculate 10-day Simple Moving Average
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    
    # Calculate Daily Return (percentage change of Close price)
    df['Daily_Return'] = df['Close'].pct_change()
    
    # 3. Target Variable
    # 1 if tomorrow's Close is strictly higher than today's Close, else 0
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # Drop rows with NaN values created by rolling, pct_change, and shift
    df.dropna(inplace=True)
    
    print(f"Data ready for training: {len(df)} samples.")
    
    # 4. Select features
    features = ['Close', 'SMA_10', 'Daily_Return']
    X = df[features]
    y = df['Target']
    
    # Split the dataset (time-series aware: shuffle=False)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    # 5. Train a basic Logistic Regression model
    print("Training LogisticRegression model...")
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    # 6. Save the trained model
    save_dir = os.path.join("src", "ml", "saved_models")
    os.makedirs(save_dir, exist_ok=True)  # Create directories if they don't exist
    
    model_path = os.path.join(save_dir, "lightweight_model.pkl")
    joblib.dump(model, model_path)
    
    # 7. Print success messages
    print("-" * 40)
    print(f"✅ Model training complete for {symbol}!")
    print(f"📈 Accuracy Score: {acc * 100:.2f}%")
    print(f"💾 Model successfully saved to: {model_path}")
    print("-" * 40)


if __name__ == "__main__":
    main()
