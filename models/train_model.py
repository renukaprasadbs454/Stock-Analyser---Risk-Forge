import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
import streamlit as st

def train_lstm_model(stock_ticker: str):
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Fetch historical data with error handling
    try:
        data = yf.download(stock_ticker, start="2015-01-01", end="2024-01-01")
        
        if len(data) == 0:
            st.error(f"No data found for stock ticker: {stock_ticker}")
            return None
        
        df = data[['Close']].copy()
    except Exception as e:
        st.error(f"Error fetching data for {stock_ticker}: {e}")
        return None

    # Preprocess data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df)

    # Prepare training data
    X_train, y_train = [], []
    for i in range(60, len(scaled_data)):
        X_train.append(scaled_data[i-60:i, 0])
        y_train.append(scaled_data[i, 0])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Build LSTM model with improved architecture
    model = Sequential([
        LSTM(units=100, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.3),
        LSTM(units=75, return_sequences=True),
        Dropout(0.3),
        LSTM(units=50),
        Dropout(0.3),
        Dense(units=1)
    ])

    # Compile with learning rate scheduling
    initial_learning_rate = 0.001
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate,
        decay_steps=100,
        decay_rate=0.9,
        staircase=True
    )
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
    
    model.compile(optimizer=optimizer, loss='mean_squared_error')

    # Early stopping and model checkpoint
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='loss', 
        patience=5, 
        restore_best_weights=True
    )
    model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
        f"models/lstm_model_{stock_ticker}.h5", 
        save_best_only=True
    )

    # Train the model
    history = model.fit(
        X_train, y_train, 
        epochs=50, 
        batch_size=32, 
        verbose=1,
        callbacks=[early_stopping, model_checkpoint]
    )

    # Save model performance metrics
    performance = {
        'final_loss': history.history['loss'][-1],
        'total_epochs': len(history.history['loss'])
    }

    # Save scaler for future use
    import joblib
    joblib.dump(scaler, f"models/scaler_{stock_ticker}.joblib")

    return scaler, performance

def main():
    st.title("Advanced Stock Price Prediction Model Trainer")
    
    # Stock ticker input
    stock_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, GOOGL, MSFT)", "AAPL")
    
    # Stock list suggestion
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]
    st.write("Quick pick popular stocks:", " | ".join(popular_stocks))

    # Train button
    if st.button('Train Model'):
        if stock_ticker:
            st.info(f"Training LSTM model for {stock_ticker}...")
            
            # Progress bar
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
            
            # Train model
            result = train_lstm_model(stock_ticker)
            
            if result:
                scaler, performance = result
                st.success(f"Model for {stock_ticker} trained successfully!")
                
                # Display model performance
                st.write("### Model Training Performance")
                st.write(f"Final Loss: {performance['final_loss']:.4f}")
                st.write(f"Total Epochs Trained: {performance['total_epochs']}")
                
                # Suggestion for model use
                st.info("Model saved and ready for predictions in the main application.")
            else:
                st.error("Model training failed. Check the stock ticker and data availability.")

if __name__ == "__main__":
    main()