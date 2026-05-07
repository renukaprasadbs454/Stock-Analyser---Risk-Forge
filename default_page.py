import streamlit as st
import stTools as tools


def _section(icon: str, label: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:1.4rem 0 .75rem;">
            <span style="font-size:15px;">{icon}</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;
                         letter-spacing:2px;color:#94a3b8;font-weight:700;">{label}</span>
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _col_label(text: str) -> None:
    st.markdown(
        f"<p style='font-family:Space Mono,monospace;font-size:10px;letter-spacing:1.5px;"
        f"color:#94a3b8;font-weight:700;margin-bottom:6px;text-transform:uppercase;'>{text}</p>",
        unsafe_allow_html=True,
    )


def load_page():
    # ── Two analysis mode cards ──────────────────────────────────────────────
    _section("🎯", "SELECT ANALYSIS MODE")

    col_port, col_single = st.columns(2)

    with col_port:
        st.markdown(
            """
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:16px;
                        padding:22px 22px 18px;box-shadow:0 1px 6px rgba(15,23,42,.07);
                        border-top:4px solid #0891b2;min-height:140px;'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
                    <span style='font-size:24px;'>📂</span>
                    <span style='font-family:Space Mono,monospace;font-size:13px;font-weight:700;
                                 color:#0f172a;letter-spacing:.5px;'>ANALYSE PORTFOLIO</span>
                </div>
                <p style='font-size:13px;color:#475569;line-height:1.65;margin:0;'>
                    Build a multi-stock portfolio, run <b>Monte Carlo</b> simulations,
                    and compute <b>VaR</b> &amp; <b>CVaR</b> risk metrics across your holdings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("▶ BUILD PORTFOLIO", key="mode_portfolio_btn", use_container_width=True):
            st.info("Use the **📈 Create Portfolio** tab in the sidebar → select stocks → click **Load Portfolio**.")

    with col_single:
        st.markdown(
            """
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:16px;
                        padding:22px 22px 18px;box-shadow:0 1px 6px rgba(15,23,42,.07);
                        border-top:4px solid #7c3aed;min-height:140px;'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
                    <span style='font-size:24px;'>🔬</span>
                    <span style='font-family:Space Mono,monospace;font-size:13px;font-weight:700;
                                 color:#0f172a;letter-spacing:.5px;'>ANALYSE SINGLE STOCK</span>
                </div>
                <p style='font-size:13px;color:#475569;line-height:1.65;margin:0;'>
                    Deep-dive into one stock — <b>LSTM price prediction</b>, technical signals
                    (RSI, MACD, Bollinger Bands), and a full risk score.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("▶ PICK A STOCK", key="mode_single_btn", use_container_width=True):
            st.info("Use the **Prediction** tab in the sidebar → choose sector & stock → click **▶ TRAIN MODEL AND PREDICT**.")

    st.divider()

    # ── Market selector ───────────────────────────────────────────────────────
    _section("🌐", "MARKET PREVIEW")

    market_choice = st.radio(
        "Market",
        options=["🇮🇳 Indian Markets", "🇺🇸 U.S. Markets"],
        horizontal=True,
        label_visibility="collapsed",
        key="market_preview_choice",
    )

    is_india = "Indian" in market_choice

    # Index definitions
    indian_indices = {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "Bank Nifty": "^NSEBANK"}
    us_indices     = {"Dow Jones": "^DJI",  "NASDAQ":  "^IXIC",  "S&P 500":   "^GSPC"}

    indices = indian_indices if is_india else us_indices

    # ── Index charts ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    idx_cols = st.columns(3)
    for col, (name, ticker) in zip(idx_cols, indices.items()):
        with col:
            _col_label(name)
            tools.create_candle_stick_plot(stock_ticker_name=ticker, stock_name=name)

    st.divider()

    # ── Sector stock tables ───────────────────────────────────────────────────
    if is_india:
        _section("🏭", "SECTOR BREAKDOWN  —  INDIA")
        sectors = {
            "💻 Technology": {
                "tickers": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
                "names":   ["TCS", "Infosys", "Wipro", "HCL Tech", "Tech Mahindra"],
            },
            "🏦 Banking": {
                "tickers": ["ICICIBANK.NS", "HDFCBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
                "names":   ["ICICI Bank", "HDFC Bank", "SBI", "Axis Bank", "Kotak Bank"],
            },
            "📈 Large Caps": {
                "tickers": ["RELIANCE.NS", "TATAMOTORS.NS", "ADANIGREEN.NS", "SUZLON.NS", "VEDL.NS"],
                "names":   ["Reliance", "Tata Motors", "Adani Green", "Suzlon", "Vedanta"],
            },
        }
    else:
        _section("🏭", "SECTOR BREAKDOWN  —  U.S.")
        sectors = {
            "💻 Technology": {
                "tickers": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA", "NFLX"],
                "names":   ["Apple", "Microsoft", "Amazon", "Google", "Meta", "Tesla", "Nvidia", "Netflix"],
            },
            "🏦 Banking": {
                "tickers": ["JPM", "BAC", "WFC", "GS", "MS", "C", "USB", "PNC"],
                "names":   ["JPMorgan", "BofA", "Wells Fargo", "Goldman", "Morgan Stanley", "Citi", "US Bancorp", "PNC"],
            },
            "📈 High Volatility": {
                "tickers": ["GME", "AMC", "BB", "NOK", "RIVN", "SPCE", "F", "T"],
                "names":   ["GameStop", "AMC", "BlackBerry", "Nokia", "Rivian", "Virgin Galactic", "Ford", "AT&T"],
            },
        }

    sec_cols = st.columns(3)
    for col, (sec_name, sec_data) in zip(sec_cols, sectors.items()):
        with col:
            st.markdown(
                f"<p style='font-family:Space Mono,monospace;font-size:11px;font-weight:700;"
                f"color:#0f172a;letter-spacing:.5px;margin-bottom:8px;'>{sec_name}</p>",
                unsafe_allow_html=True,
            )
            df = tools.create_stocks_dataframe(sec_data["tickers"], sec_data["names"])
            tools.create_dateframe_view(df)
