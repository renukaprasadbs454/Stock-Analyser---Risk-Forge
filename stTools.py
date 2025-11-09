import datetime
import streamlit as st
import yfinance
import datetime as dt
from assets.Collector import InfoCollector
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
from assets import Portfolio
from assets import Stock
import plotly.express as px
import json
import os






def create_state_variable(key: str, default_value: any) -> None:
    if key not in st.session_state:
        st.session_state[key] = default_value


def create_stock_text_input(
        state_variable: str,
        default_value: str,
        present_text: str,
        key: str
) -> None:
    create_state_variable(state_variable, default_value)

    st.session_state[state_variable] = st.text_input(present_text,
                                                     key=key,
                                                     value=st.session_state[state_variable])


def create_date_input(
        state_variable: str,
        present_text: str,
        default_value: str,
        key: str
) -> None:
    create_state_variable(state_variable, default_value)

    st.session_state[state_variable] = st.date_input(present_text,
                                                     value=st.session_state[state_variable],
                                                     key=key)


def get_stock_demo_data(no_stocks: int) -> list:
    stock_name_list = [
        'AAPL', 'TSLA', 'GOOG', 'MSFT', 'AMZN', 'META', 'NVDA', 'PYPL',
        'NFLX', 'ADBE', 'INTC', 'CSCO', 'ORCL', 'IBM', 'QCOM', 'TXN',
        'AMD', 'SPOT', 'BABA', 'DIS', 'PEP', 'KO', 'V', 'MA', 'WMT',
        'T', 'CRM', 'COST', 'XOM', 'JNJ'
    ]
    return stock_name_list[:no_stocks]




def click_button_sim() -> None:
    st.session_state["run_simulation"] = True
    st.session_state["run_simulation_check"] = True


def click_button_port() -> None:
    st.session_state["load_portfolio"] = True
    st.session_state["load_portfolio_check"] = True
    st.session_state["run_simulation_check"] = False


def preview_stock(
        session_state_name: str,
        start_date: datetime.datetime
) -> None:
    stock_data = yfinance.download(st.session_state[session_state_name],
                                   start=start_date,
                                   end=dt.datetime.now())
    stock_data = stock_data[['Close']]

    color = None

    # get price difference of close
    #diff_price = stock_data.iloc[-1]['Close'] - stock_data.iloc[0]['Close']
    if not stock_data.empty:
        last_close = stock_data['Close'].iloc[-1].item()  # Ensure float
        first_close = stock_data['Close'].iloc[0].item()  # Ensure float
        diff_price = last_close - first_close
    else:
        last_close = first_close = diff_price = 0  # Handle empty data case

    color = None
    if diff_price > 0.0:
        color = '#00fa119e'
    elif diff_price < 0.0:
        color = '#fa00009e'

# Change index for plotting
    stock_data['day(s) since buy'] = range(0, len(stock_data))

# Use scalar values in f-strings
    create_metric_card(label=st.session_state[session_state_name],
                    value=f"{last_close:.2f}",
                    delta=f"{diff_price:.2f}")

    st.area_chart(stock_data, use_container_width=True,
                height=250, width=250, color=color, x='day(s) since buy')



def format_currency(number: float) -> str:
    formatted_number = "${:,.2f}".format(number)
    return formatted_number


def create_side_bar_width() -> None:
    st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 450px;
           max-width: 600px;
       }
       """,
        unsafe_allow_html=True,
    )


def remove_white_space():
    st.markdown("""
            <style>
                   .block-container {
                        padding-top: 1rem;
                    }
            </style>
            """, unsafe_allow_html=True)


def get_current_date() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d')


def create_candle_stick_plot(stock_ticker_name: str, stock_name: str) -> None:
    try:
        # Retrieve stock object and historical data
        stock = InfoCollector.get_ticker(stock_ticker_name)
        
        # For market indices, use 1-day interval instead of 5-minute
        if stock_ticker_name.startswith('^'):
            # For indices, get 1 month of daily data
            stock_data = stock.history(period="1mo", interval="1d")
        else:
            # For regular stocks, get 5-minute data for the last day
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=1)
            stock_data = stock.history(interval="5m", start=start_date, end=end_date)
            
        if stock_data.empty:
            st.warning(f"No data available for {stock_name}. The market might be closed.")
            return
            
        stock_data_template = stock_data.copy()

        # Validate and preprocess stock data
        if stock_data is None or stock_data.empty:
            st.error(f"No data available for {stock_name}. Please try again later.")
            return

        stock_data = stock_data[['Open', 'High', 'Low', 'Close']]
        if stock_data.empty:
            st.error(f"Insufficient data to create candlestick chart for {stock_name}.")
            return

        # Calculate prices
        open_price = stock_data.iloc[0]['Open']
        close_price_data = InfoCollector.get_history(stock, period="1d")
        close_price = close_price_data["Close"].iloc[-1] if not close_price_data.empty else None

        if close_price is None:
            st.error("Failed to retrieve close price. Please try again later.")
            return

        diff_price = close_price - open_price

        # Create metric card
        create_metric_card(
            label=f"{stock_name}",
            value=f"{close_price: .2f}",
            delta=f"{diff_price: .2f}"
        )

        # Ensure the index alignment for plotting
        stock_data_template = stock_data_template[['Open', 'High', 'Low', 'Close']]
        if not stock_data_template.index.equals(stock_data.index):
            stock_data_template = stock_data_template.reindex(stock_data.index)

        # Candlestick chart
        candlestick_chart = go.Figure(
            data=[
                go.Candlestick(
                    x=stock_data_template.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close']
                )
            ]
        )

        # Chart layout updates
        candlestick_chart.update_layout(
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=400  # Adjust the height dynamically if needed
        )
        
        # Render the chart
        st.plotly_chart(candlestick_chart, use_container_width=True)
    except Exception as e:
        # Log or display error for debugging
        st.error(f"An error occurred while generating the candlestick chart: {str(e)}")



def create_stocks_dataframe(stock_ticker_list: list, stock_name: list) -> pd.DataFrame:
    close_price = []
    daily_change = []
    pct_change = []
    all_price = []
    for stock_ticker in stock_ticker_list:
        try:
            stock = InfoCollector.get_ticker(stock_ticker)
            # Use 1d interval instead of 5m for more reliable data
            stock_data = InfoCollector.get_history(stock, period="1d", interval='1d')
            
            if not stock_data.empty:
                # round value to 2 digits
                close_price_value = round(stock_data.iloc[-1]['Close'], 2)
                close_price.append(close_price_value)

                # round value to 2 digits
                daily_change_value = round(stock_data.iloc[-1]['Close'] - stock_data.iloc[0]['Open'], 2)
                daily_change.append(daily_change_value)
            else:
                # If no data available, use default values
                close_price.append(0.0)
                daily_change.append(0.0)
        except Exception as e:
            st.error(f"Error fetching data for {stock_ticker}: {str(e)}")
            close_price.append(0.0)
            daily_change.append(0.0)

        # round value to 2 digits
        pct_change_value = round((stock_data.iloc[-1]['Close'] - stock_data.iloc[0]['Open'])
                                 / stock_data.iloc[0]['Open'] * 100, 2)
        pct_change.append(pct_change_value)

        all_price.append(stock_data['Close'].tolist())

    df_stocks = pd.DataFrame(
        {
            "stock_tickers": stock_ticker_list,
            "stock_name": stock_name,
            "close_price": close_price,
            "daily_change": daily_change,
            "pct_change": pct_change,
            "views_history": all_price
        }
    )
    return df_stocks


def win_highlight(val: str) -> str:
    color = None
    val = str(val)
    val = val.replace(',', '')

    if float(val) >= 0.0:
        color = '#00fa119e'
    elif float(val) < 0.0:
        color = '#fa00009e'
    return f'background-color: {color}'


def create_dateframe_view(df: pd.DataFrame) -> None:
    df['close_price'] = df['close_price'].apply(lambda x: f'{x:,.2f}')
    df['daily_change'] = df['daily_change'].apply(lambda x: f'{x:,.2f}')
    df['pct_change'] = df['pct_change'].apply(lambda x: f'{x:,.2f}')

    st.dataframe(
        df.style.map(win_highlight,
                     subset=['daily_change', 'pct_change']),
        column_config={
            "stock_tickers": "Tickers",
            "stock_name": "Stock",
            "close_price": "Price ($)",
            "daily_change": "Price Change ($)",  # if positive, green, if negative, red
            "pct_change": "% Change",  # if positive, green, if negative, red
            "views_history": st.column_config.LineChartColumn(
                "daily trend"),
        },
        hide_index=True,
        width=620,
    )


def build_portfolio(no_stocks: int) -> Portfolio.Portfolio:
    # build portfolio using portfolio class
    my_portfolio = Portfolio.Portfolio()
    for i in range(no_stocks):
        stock = Stock.Stock(stock_name=st.session_state[f"stock_{i + 1}_name"])
        stock.add_buy_action(quantity=int(st.session_state[f"stock_{i + 1}_share"]),
                             purchase_date=st.session_state[f"stock_{i + 1}_purchase_date"])
        my_portfolio.add_stock(stock=stock)
    return my_portfolio


def get_metric_bg_color() -> str:
    return "#282C35"


def create_metric_card(label: str, value: str, delta: str) -> None:
    st.metric(label=label,
              value=value,
              delta=delta)

    background_color = get_metric_bg_color()
    style_metric_cards(background_color=background_color)




def create_pie_chart(key_values: dict, save_to: str = None, chart_key: str = None) -> str:
    """
    Creates a pie chart using Plotly.

    Parameters:
    - key_values (dict): A dictionary with labels as keys and values as the corresponding values for the pie chart.
    - save_to (str): Path to save the chart as an image. If None, the chart is not saved.
    - chart_key (str): Unique key for Streamlit to avoid duplicate element IDs.

    Returns:
    - str: Path to the saved image file if saved, otherwise None.
    """
    labels = list(key_values.keys())
    values = list(key_values.values())

    # Create a pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            insidetextorientation='radial'
        )
    ])

    # Update layout for better visualization
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )

    # Save the chart to a file if `save_to` is specified
    if save_to:
        # Ensure the save directory exists
        os.makedirs(os.path.dirname(save_to), exist_ok=True)

        # Save the chart as a static image
        try:
            fig.write_image(save_to, format="png")
            return save_to
        except Exception as e:
            print(f"Error saving pie chart: {e}")

    # Display the chart in Streamlit with a unique key
    st.plotly_chart(fig, use_container_width=True, use_container_height=True, key=chart_key)

    return None


def create_line_chart(portfolio_df: pd.DataFrame) -> None:
    fig = px.line(portfolio_df)
    fig.update_layout(xaxis_rangeslider_visible=False,
                      margin=dict(l=20, r=20, t=20, b=20),
                      showlegend=False,
                      xaxis_title="Day(s) since purchase",
                      yaxis_title="Portfolio Value ($)")
    st.plotly_chart(fig, use_container_width=True, use_container_height=True)