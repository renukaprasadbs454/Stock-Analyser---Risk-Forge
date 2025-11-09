import streamlit as st
import yfinance as yf
import stTools as tools

def load_page():
    st.markdown(
        """
        Welcome to :green[RiskForge] — your one-stop solution to evaluate and optimize your investment portfolio with ease! Think of risk management as your financial GPS—it helps you navigate uncertainties and keeps your investments on track.

        Investing is like building a castle—strong foundations ensure it stands the test of time. 
        Our app equips you with cutting-edge tools like :green[Value at Risk (VaR)] and :green[Conditional Value at Risk (CVaR)] to measure and mitigate potential losses, giving you the confidence to make smarter decisions.

        Let's transform uncertainties into opportunities and build a portfolio that thrives under any market condition!
        """
    )

    st.subheader(f"Market Preview")

    market_choice = st.selectbox("Select Market", ["Indian Stock Market", "U.S. Stock Market"], index=0)

    # Define the stock tickers for Indian and U.S. markets
    indian_stocks = {
        "Nifty 50": "^NSEI",
        "Sensex": "^BSESN",
        "Bank Nifty": "^NSEBANK"
    }

    us_stocks = {
        "Dow Jones Industrial": "^DJI",
        "Nasdaq Composite": "^IXIC",
        "S&P 500": "^GSPC"
    }

    # Define the columns for the stock previews
    col_stock1, col_stock_2, col_stock_3 = st.columns(3)

    if market_choice == "Indian Stock Market":
        st.subheader("Market Preview - Indian Stock Market")
        with col_stock1:
            tools.create_candle_stick_plot(stock_ticker_name=indian_stocks["Nifty 50"], stock_name="Nifty 50")
    
        with col_stock_2:
            tools.create_candle_stick_plot(stock_ticker_name=indian_stocks["Sensex"], stock_name="Sensex")
    
        with col_stock_3:
            tools.create_candle_stick_plot(stock_ticker_name=indian_stocks["Bank Nifty"], stock_name="Bank Nifty")

        # Define the columns for the sector views (Indian market sectors)
        col_sector1, col_sector2, col_sector3 = st.columns(3)

        # Technology sector for Indian market
        with col_sector1:
            st.subheader(f"Technology (Indian)")
            stock_list = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"]
            stock_name = ["TCS", "Infosys", "Wipro", "HCL Technologies", "Tech Mahindra"]
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)

        # Banking sector for Indian market
        with col_sector2:
            st.subheader(f"Banking (Indian)")
            stock_list = ["ICICIBANK.NS", "HDFCBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"]
            stock_name = ["ICICI Bank", "HDFC Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank"]
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)

        # Meme Stocks sector for Indian market
        with col_sector3:
            st.subheader(f"Meme Stocks (Indian)")
            stock_list = ["RELIANCE.NS", "TATAMOTORS.NS", "ADANIGREEN.NS", "SUZLON.NS", "VEDL.NS"]
            stock_name = ["Reliance Industries", "Tata Motors", "Adani Green", "Suzlon", "Vedanta"]
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)

    elif market_choice == "U.S. Stock Market":
        st.subheader("Market Preview - U.S. Stock Market")
        with col_stock1:
            tools.create_candle_stick_plot(stock_ticker_name=us_stocks["Dow Jones Industrial"], stock_name="Dow Jones Industrial")
    
        with col_stock_2:
            tools.create_candle_stick_plot(stock_ticker_name=us_stocks["Nasdaq Composite"], stock_name="Nasdaq Composite")
    
        with col_stock_3:
            tools.create_candle_stick_plot(stock_ticker_name=us_stocks["S&P 500"], stock_name="S&P 500")

        # Define the columns for the sector views (U.S. market sectors)
        col_sector1, col_sector2, col_sector3 = st.columns(3)

        # Technology sector for U.S. market
        with col_sector1:
            st.subheader(f"Technology (U.S.)")
            stock_list = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA", "NFLX"]
            stock_name = ["Apple", "Microsoft", "Amazon", "Google", "Meta", "Tesla", "Nvidia", "Netflix"]
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)

        # Banking sector for U.S. market
        with col_sector2:
            st.subheader(f"Banking (U.S.)")
            stock_list = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC']
            stock_name = ['JPMorgan', 'BoA', 'Wells Fargo', 'Goldman Sachs', 'Morgan Stanley', 'Citigroup', 'U.S. Bancorp', 'PNC']
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)

        # Meme Stocks sector for U.S. market
        with col_sector3:
            st.subheader(f"Meme Stocks (U.S.)")
            stock_list = ["GME", "AMC", "BB", "NOK", "RIVN", "SPCE", "F", "T"]
            stock_name = ["GameStop", "AMC Entertainment", "BlackBerry", "Nokia", "Rivian", "Virgin Galactic", "Ford", "AT&T"]
            df_stocks = tools.create_stocks_dataframe(stock_list, stock_name)
            tools.create_dateframe_view(df_stocks)