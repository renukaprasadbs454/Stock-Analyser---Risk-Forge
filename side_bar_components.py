import streamlit as st
import stTools as tools
import datetime as dt
import random


def load_sidebar_dropdown_stocks(port_tab) -> None:
    """Category → stock multi-select portfolio builder."""

    category_names = list(tools.STOCK_CATEGORIES.keys())

    port_tab.markdown("**Step 1 — Choose a Sector**")
    selected_category = port_tab.radio(
        "Sector",
        options=category_names,
        horizontal=False,
        label_visibility="collapsed",
        key="portfolio_category_radio",
    )

    stocks_in_cat = tools.STOCK_CATEGORIES[selected_category]
    stock_options = [f"{ticker} — {name}" for ticker, name in stocks_in_cat.items()]

    port_tab.markdown("**Step 2 — Pick Stocks**")
    selected_labels = port_tab.multiselect(
        "Stocks",
        options=stock_options,
        default=stock_options[:3],
        key="portfolio_stock_multiselect",
        label_visibility="collapsed",
        placeholder="Search and select stocks…",
    )

    selected_tickers = [label.split(" — ")[0] for label in selected_labels]

    # Cap at 10 for the portfolio
    if len(selected_tickers) > 10:
        port_tab.warning("Maximum 10 stocks allowed. Only the first 10 will be used.")
        selected_tickers = selected_tickers[:10]

    # Write into session state so the rest of the app can find them
    st.session_state["no_investment"] = max(len(selected_tickers), 1)
    st.session_state["selected_tickers"] = selected_tickers

    # Seed individual stock session-state keys
    for i, ticker in enumerate(selected_tickers):
        key_name  = f"stock_{i + 1}_name"
        key_share = f"stock_{i + 1}_share"
        key_date  = f"stock_{i + 1}_purchase_date"
        if key_name not in st.session_state:
            st.session_state[key_name] = ticker
        if key_share not in st.session_state:
            st.session_state[key_share] = str(random.randrange(10, 100, 10))
        if key_date not in st.session_state:
            delta = dt.timedelta(days=random.randrange(3, 120))
            st.session_state[key_date] = (dt.datetime.now() - delta).date()


def load_sidebar_stocks(port_tab, no_investment: int) -> None:
    """Render share-count + date inputs for each selected stock."""
    selected_tickers = st.session_state.get("selected_tickers", [])
    if not selected_tickers:
        return

    port_tab.markdown("**Step 3 — Set Quantities & Dates**")

    for i, ticker in enumerate(selected_tickers):
        with port_tab.expander(f"{ticker}", expanded=False):
            col_s, col_d = st.columns(2)
            with col_s:
                key_share = f"stock_{i + 1}_share"
                st.session_state[key_share] = st.text_input(
                    "Shares",
                    value=st.session_state.get(key_share, "10"),
                    key=f"sb_share_{i}",
                )
            with col_d:
                key_date = f"stock_{i + 1}_purchase_date"
                default_date = st.session_state.get(key_date, dt.date.today() - dt.timedelta(days=30))
                if isinstance(default_date, dt.datetime):
                    default_date = default_date.date()
                st.session_state[key_date] = st.date_input(
                    "Purchase Date",
                    value=default_date,
                    key=f"sb_date_{i}",
                )
            # Keep name in sync (may have changed via radio)
            st.session_state[f"stock_{i + 1}_name"] = ticker


def load_sidebar_risk_model(risk_tab) -> None:
    col_monte1, col_monte2 = risk_tab.columns(2)

    with col_monte1:
        tools.create_date_input(state_variable="start_date",
                                present_text="History Start Date",
                                default_value=dt.datetime.now() - dt.timedelta(days=365),
                                key="side_bar_start_date")

        tools.create_stock_text_input(state_variable="no_simulations",
                                      default_value=str(100),
                                      present_text="No. of Simulations",
                                      key="main_no_simulations")

        tools.create_stock_text_input(state_variable="VaR_alpha",
                                      default_value=str(0.05),
                                      present_text="VaR Alpha",
                                      key="side_bar_VaR_alpha")
    with col_monte2:
        tools.create_date_input(state_variable="end_date",
                                present_text="History End Date",
                                default_value=dt.datetime.now(),
                                key="side_bar_end_date")

        tools.create_stock_text_input(state_variable="no_days",
                                      default_value=str(100),
                                      present_text="No. of Days",
                                      key="main_no_days")

        tools.create_stock_text_input(state_variable="cVaR_alpha",
                                      default_value=str(0.05),
                                      present_text="cVaR Alpha",
                                      key="side_bar_cVaR_alpha")
