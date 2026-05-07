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


STOCK_CATEGORIES = {
    "💻 Technology": {
        "AAPL": "Apple", "MSFT": "Microsoft", "GOOG": "Alphabet",
        "NVDA": "NVIDIA", "META": "Meta", "AMZN": "Amazon",
        "ADBE": "Adobe", "INTC": "Intel", "CSCO": "Cisco",
        "ORCL": "Oracle", "IBM": "IBM", "CRM": "Salesforce",
        "AMD": "AMD", "QCOM": "Qualcomm", "TSLA": "Tesla",
        "INFY": "Infosys", "TCS.NS": "TCS", "WIPRO.NS": "Wipro",
        "HCLTECH.NS": "HCL Tech", "TECHM.NS": "Tech Mahindra",
    },
    "🏦 Finance & Payments": {
        "JPM": "JPMorgan Chase", "BAC": "Bank of America", "GS": "Goldman Sachs",
        "V": "Visa", "MA": "Mastercard", "PYPL": "PayPal",
        "MS": "Morgan Stanley", "WFC": "Wells Fargo", "C": "Citigroup",
        "HDFC.NS": "HDFC Bank", "ICICIBANK.NS": "ICICI Bank", "AXISBANK.NS": "Axis Bank",
    },
    "🛒 Consumer & Healthcare": {
        "NFLX": "Netflix", "DIS": "Disney", "PEP": "PepsiCo",
        "KO": "Coca-Cola", "WMT": "Walmart", "COST": "Costco",
        "JNJ": "Johnson & Johnson", "PFE": "Pfizer", "MRK": "Merck",
        "SPOT": "Spotify", "BABA": "Alibaba", "XOM": "ExxonMobil",
    },
}


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


def click_button_geo() -> None:
    st.session_state["load_geo"] = True
    st.session_state["load_geo_check"] = True


def click_button_single_stock() -> None:
    st.session_state["analyse_single_stock"] = True
    st.session_state["load_portfolio_check"] = False
    st.session_state["run_simulation_check"] = False
    st.session_state["load_geo_check"] = False


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
            @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

            /* ══════════════════════════════════════════════
               DESIGN TOKENS  (light palette)
               ══════════════════════════════════════════════ */
            :root {
                --bg:       #f8fafc;
                --bg2:      #f1f5f9;
                --card:     #ffffff;
                --border:   #e2e8f0;
                --border2:  #cbd5e1;
                --text:     #0f172a;
                --text2:    #475569;
                --text3:    #94a3b8;
                --accent:   #0891b2;   /* cyan-600  */
                --accent2:  #7c3aed;   /* violet-600 */
                --green:    #059669;   /* emerald-600 */
                --red:      #dc2626;   /* red-600 */
                --amber:    #d97706;   /* amber-600 */
                --font-mono: 'Space Mono', 'Courier New', monospace;
                --font-body: 'DM Sans', 'Segoe UI', sans-serif;
                --shadow:   0 1px 4px rgba(15,23,42,.06), 0 4px 16px rgba(15,23,42,.04);
                --shadow-hover: 0 2px 8px rgba(15,23,42,.10), 0 8px 24px rgba(15,23,42,.06);
            }

            /* ── Base ── */
            .block-container { padding-top: 1rem !important; max-width: 1400px; }
            html, body, [class*="css"], .stApp {
                font-family: var(--font-body) !important;
                background-color: var(--bg) !important;
                color: var(--text) !important;
            }

            /* ── Hide / neutralise Streamlit chrome ── */
            #MainMenu, footer, [data-testid="stToolbar"],
            [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
                display: none !important;
            }
            header[data-testid="stHeader"] {
                background: #f8fafc !important;
                border-bottom: 1px solid #e2e8f0 !important;
                height: 0 !important;
                min-height: 0 !important;
            }
            /* Force entire app background white/light */
            .stApp, .main, [data-testid="stAppViewContainer"] {
                background-color: #f8fafc !important;
            }
            [data-testid="stMain"] > div {
                background-color: #f8fafc !important;
            }

            /* ── Main headings ── */
            h1 { font-family: var(--font-mono) !important; letter-spacing: -0.5px; color: var(--text) !important; }
            h2, h3 { font-family: var(--font-body) !important; font-weight: 700 !important; color: var(--text) !important; }

            /* ══════════════════════════════════════════════
               SIDEBAR
               ══════════════════════════════════════════════ */
            [data-testid="stSidebar"] {
                background: var(--card) !important;
                border-right: 1px solid var(--border) !important;
            }
            [data-testid="stSidebar"] * { color: var(--text) !important; }
            [data-testid="stSidebar"] .stMarkdown p {
                font-size: 13px;
                color: var(--text2) !important;
            }
            /* sidebar title */
            [data-testid="stSidebar"] h1 {
                font-family: var(--font-mono) !important;
                font-size: 15px !important;
                letter-spacing: 2px;
                color: var(--accent) !important;
                text-transform: uppercase;
                padding-bottom: 8px;
                border-bottom: 2px solid var(--accent);
                margin-bottom: 4px !important;
            }
            [data-testid="stSidebar"][aria-expanded="true"] {
                min-width: 420px;
                max-width: 520px;
            }

            /* ══════════════════════════════════════════════
               TAB STRIP
               ══════════════════════════════════════════════ */
            .stTabs [data-baseweb="tab-list"] {
                background: var(--bg2);
                border-radius: 10px;
                gap: 2px;
                padding: 4px;
                border: 1px solid var(--border);
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 7px;
                color: var(--text2) !important;
                font-family: var(--font-body);
                font-weight: 500;
                font-size: 13px;
                padding: 6px 14px;
                transition: all .15s;
            }
            .stTabs [aria-selected="true"] {
                background: var(--card) !important;
                color: var(--accent) !important;
                box-shadow: var(--shadow) !important;
                font-weight: 600 !important;
            }

            /* ══════════════════════════════════════════════
               METRIC CARDS
               ══════════════════════════════════════════════ */
            [data-testid="stMetric"] {
                background: var(--card) !important;
                border: 1px solid var(--border) !important;
                border-radius: 14px !important;
                padding: 16px 20px !important;
                box-shadow: var(--shadow);
                transition: box-shadow .2s, border-color .2s, transform .15s;
            }
            [data-testid="stMetric"]:hover {
                box-shadow: var(--shadow-hover);
                border-color: var(--accent) !important;
                transform: translateY(-2px);
            }
            [data-testid="stMetricLabel"] {
                font-family: var(--font-mono) !important;
                font-size: 10px !important;
                letter-spacing: 1.5px !important;
                text-transform: uppercase !important;
                color: var(--text3) !important;
            }
            [data-testid="stMetricValue"] {
                font-family: var(--font-mono) !important;
                font-size: 26px !important;
                font-weight: 700 !important;
                color: var(--text) !important;
                line-height: 1.2 !important;
            }
            [data-testid="stMetricDelta"] {
                font-family: var(--font-mono) !important;
                font-size: 12px !important;
                font-weight: 700 !important;
            }

            /* ══════════════════════════════════════════════
               BUTTONS
               ══════════════════════════════════════════════ */
            .stButton > button {
                background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
                color: #fff !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 9px 22px !important;
                font-family: var(--font-mono) !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                letter-spacing: 1px;
                text-transform: uppercase;
                width: 100%;
                transition: opacity .2s, transform .15s, box-shadow .2s !important;
                box-shadow: 0 2px 8px rgba(8,145,178,.25);
            }
            .stButton > button:hover {
                opacity: .88 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 16px rgba(8,145,178,.35) !important;
            }
            .stButton > button:active { transform: translateY(0) !important; }

            /* ══════════════════════════════════════════════
               INPUTS & SELECTS
               ══════════════════════════════════════════════ */
            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div {
                background: var(--bg2) !important;
                border-color: var(--border) !important;
                border-radius: 8px !important;
            }
            [data-baseweb="input"] > div:focus-within,
            [data-baseweb="textarea"] > div:focus-within {
                border-color: var(--accent) !important;
                box-shadow: 0 0 0 3px rgba(8,145,178,.12) !important;
            }
            [data-baseweb="select"] > div {
                background: var(--bg2) !important;
                border-color: var(--border) !important;
                border-radius: 8px !important;
            }
            [data-baseweb="select"] > div:focus-within {
                border-color: var(--accent) !important;
            }
            /* multiselect tags */
            [data-baseweb="tag"] {
                background: rgba(8,145,178,.10) !important;
                border-radius: 5px !important;
                color: var(--accent) !important;
                font-family: var(--font-mono) !important;
                font-size: 11px !important;
                font-weight: 700 !important;
            }
            /* radio buttons */
            [data-testid="stRadio"] label {
                font-size: 13px !important;
                font-weight: 500 !important;
                color: var(--text2) !important;
                padding: 4px 8px;
                border-radius: 6px;
                transition: background .15s;
            }
            [data-testid="stRadio"] label:hover { background: var(--bg2); }

            /* ══════════════════════════════════════════════
               EXPANDERS
               ══════════════════════════════════════════════ */
            [data-testid="stExpander"] {
                background: var(--card) !important;
                border: 1px solid var(--border) !important;
                border-radius: 10px !important;
                box-shadow: var(--shadow);
                margin-bottom: 6px !important;
            }
            [data-testid="stExpander"] summary {
                font-family: var(--font-mono) !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                letter-spacing: .5px;
                color: var(--text) !important;
                padding: 10px 14px !important;
            }
            [data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

            /* ══════════════════════════════════════════════
               DATAFRAME / TABLE
               ══════════════════════════════════════════════ */
            [data-testid="stDataFrame"] {
                border: 1px solid var(--border) !important;
                border-radius: 10px !important;
                overflow: hidden;
                box-shadow: var(--shadow);
            }
            [data-testid="stDataFrame"] thead tr th {
                background: var(--bg2) !important;
                color: var(--text3) !important;
                font-family: var(--font-mono) !important;
                font-size: 10px !important;
                font-weight: 700 !important;
                letter-spacing: 1.5px !important;
                text-transform: uppercase !important;
                border-bottom: 1px solid var(--border) !important;
            }
            [data-testid="stDataFrame"] tbody tr:hover td {
                background: rgba(8,145,178,.04) !important;
            }

            /* ══════════════════════════════════════════════
               PLOTLY CHARTS — force light bg
               ══════════════════════════════════════════════ */
            .stPlotlyChart { border-radius: 12px; overflow: hidden; }
            .js-plotly-plot .plotly { border-radius: 12px; }

            /* ══════════════════════════════════════════════
               SPINNER / ALERTS
               ══════════════════════════════════════════════ */
            .stSpinner > div { border-top-color: var(--accent) !important; }
            [data-testid="stAlert"] {
                border-radius: 10px !important;
                border-left-width: 4px !important;
            }

            /* ══════════════════════════════════════════════
               DIVIDER
               ══════════════════════════════════════════════ */
            hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

            /* ══════════════════════════════════════════════
               DROPDOWN POPOVER (force light bg)
               ══════════════════════════════════════════════ */
            [data-baseweb="popover"] ul,
            [data-baseweb="menu"],
            [role="listbox"] {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 10px !important;
                box-shadow: 0 4px 20px rgba(15,23,42,.12) !important;
            }
            [role="option"], [data-baseweb="menu-item"] {
                color: #0f172a !important;
                font-size: 13px !important;
            }
            [role="option"]:hover, [data-baseweb="menu-item"]:hover,
            [aria-selected="true"] {
                background: #f1f5f9 !important;
                color: #0891b2 !important;
            }

            /* ══════════════════════════════════════════════
               RADIO  (horizontal pill style)
               ══════════════════════════════════════════════ */
            [data-testid="stRadio"] > div {
                gap: 6px !important;
                flex-wrap: wrap;
            }
            [data-testid="stRadio"] label {
                background: var(--bg2);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 13px !important;
                font-weight: 500 !important;
                color: var(--text2) !important;
                transition: all .15s;
                cursor: pointer;
            }
            [data-testid="stRadio"] label:has(input:checked) {
                background: var(--card);
                border-color: var(--accent);
                color: var(--accent) !important;
                font-weight: 600 !important;
                box-shadow: var(--shadow);
            }

            /* ══════════════════════════════════════════════
               INFO / ALERT BOXES
               ══════════════════════════════════════════════ */
            [data-testid="stAlert"] {
                border-radius: 10px !important;
                border-left-width: 4px !important;
            }
            [data-testid="stAlert"][data-baseweb="notification"] {
                background: #f0f9ff !important;
                border-color: #0891b2 !important;
            }

            /* ══════════════════════════════════════════════
               SCROLLBAR
               ══════════════════════════════════════════════ */
            ::-webkit-scrollbar { width: 5px; height: 5px; }
            ::-webkit-scrollbar-track { background: var(--bg2); }
            ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: var(--text3); }

            /* ══════════════════════════════════════════════
               SECTION TITLE helper class  (use via st.markdown)
               ══════════════════════════════════════════════ */
            .rf-section-title {
                font-family: var(--font-mono);
                font-size: 11px;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: var(--text3);
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 1.2rem 0 .8rem;
            }
            .rf-section-title::after {
                content: '';
                flex: 1;
                height: 1px;
                background: var(--border);
            }

            /* ══════════════════════════════════════════════
               CARD helper  (use via st.markdown unsafe html)
               ══════════════════════════════════════════════ */
            .rf-card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 20px 24px;
                box-shadow: var(--shadow);
                margin-bottom: 12px;
            }
            .rf-card:hover { box-shadow: var(--shadow-hover); }

            /* BADGE */
            .rf-badge {
                font-family: var(--font-mono);
                font-size: 10px;
                font-weight: 700;
                letter-spacing: .5px;
                padding: 3px 9px;
                border-radius: 5px;
                display: inline-block;
            }
            .rf-badge-green  { background: rgba(5,150,105,.12);  color: var(--green); }
            .rf-badge-red    { background: rgba(220,38,38,.10);   color: var(--red);   }
            .rf-badge-amber  { background: rgba(217,119,6,.12);   color: var(--amber); }
            .rf-badge-cyan   { background: rgba(8,145,178,.10);   color: var(--accent);}

            /* SIGNAL ROW */
            .rf-signal-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 9px 0;
                border-bottom: 1px solid var(--border);
                font-size: 13px;
            }
            .rf-signal-row:last-child { border-bottom: none; }
            .rf-signal-name  { color: var(--text); font-weight: 500; }
            .rf-signal-val   { font-family: var(--font-mono); font-size: 12px; color: var(--text2); }

            /* LARGE MONO NUMBER */
            .rf-big-number {
                font-family: var(--font-mono);
                font-size: 36px;
                font-weight: 700;
                line-height: 1;
                color: var(--text);
            }
            .rf-big-number.green { color: var(--green); }
            .rf-big-number.red   { color: var(--red);   }
            .rf-big-number.cyan  { color: var(--accent); }
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
            margin=dict(l=0, r=0, t=4, b=0),
            height=220,
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#475569", family="DM Sans, sans-serif", size=11),
            xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
            yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
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

                # round value to 2 digits
                pct_change_value = round((stock_data.iloc[-1]['Close'] - stock_data.iloc[0]['Open'])
                                         / stock_data.iloc[0]['Open'] * 100, 2)
                pct_change.append(pct_change_value)
                all_price.append(stock_data['Close'].tolist())
            else:
                # If no data available, use default values
                close_price.append(0.0)
                daily_change.append(0.0)
                pct_change.append(0.0)
                all_price.append([])
        except Exception as e:
            st.error(f"Error fetching data for {stock_ticker}: {str(e)}")
            close_price.append(0.0)
            daily_change.append(0.0)
            pct_change.append(0.0)
            all_price.append([])

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
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

    return None


def create_line_chart(portfolio_df: pd.DataFrame) -> None:
    fig = px.line(portfolio_df)
    fig.update_layout(xaxis_rangeslider_visible=False,
                      margin=dict(l=20, r=20, t=20, b=20),
                      showlegend=False,
                      xaxis_title="Day(s) since purchase",
                      yaxis_title="Portfolio Value ($)")
    st.plotly_chart(fig, use_container_width=True)