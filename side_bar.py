import streamlit as st
import stTools as tools
import side_bar_components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn

def load_sidebar() -> None:
    tools.create_side_bar_width()
    st.sidebar.title("Control Panel")

    if "load_portfolio" not in st.session_state:
        st.session_state["load_portfolio"] = False

    if "run_simulation" not in st.session_state:
        st.session_state["run_simulation"] = False

    portfo_tab, model_tab, pred_tab, geo_tab = st.sidebar.tabs(
        ["📈 Create Portfolio", " Build Risk Model", "Prediction", "🌍 Global Risk Intel"]
    )

    # Portfolio tab
    portfo_tab.title("Portfolio Building")
    side_bar_components.load_sidebar_dropdown_stocks(portfo_tab)
    side_bar_components.load_sidebar_stocks(portfo_tab,
                                            st.session_state.no_investment)
    st.session_state["load_portfolio"] = portfo_tab.button("Load Portfolio",
                                                           key="side_bar_load_portfolio",
                                                           on_click=tools.click_button_port)

   # portfo_tab.markdown("""You can create a portfolio with a maximum of :green[10] investments.""")

    # Model tab
    model_tab.title("Risk Model Building")
    side_bar_components.load_sidebar_risk_model(model_tab)
    st.session_state["run_simulation"] = model_tab.button("Run Simulation",
                                                         key="main_page_run_simulation",
                                                         on_click=tools.click_button_sim)

    # model_tab.markdown(""" :green[VaR (Value at Risk)]: Think of VaR as a safety net, indicating the maximum potential loss within a confidence level.""")

    # Prediction Tab
    pred_tab.title("Stock Prediction")

    # ── Category → stock dropdown (mirrors portfolio tab style) ──
    from stTools import STOCK_CATEGORIES
    pred_cat_names = list(STOCK_CATEGORIES.keys())

    pred_tab.markdown("**Sector**")
    pred_category = pred_tab.radio(
        "Prediction sector",
        options=pred_cat_names,
        horizontal=False,
        label_visibility="collapsed",
        key="pred_category_radio",
    )

    pred_stocks_in_cat = STOCK_CATEGORIES[pred_category]
    pred_stock_options = [f"{t} — {n}" for t, n in pred_stocks_in_cat.items()]

    pred_tab.markdown("**Select Stock**")
    pred_selected_label = pred_tab.selectbox(
        "Stock",
        options=pred_stock_options,
        key="pred_stock_select",
        label_visibility="collapsed",
    )

    stock_ticker = pred_selected_label.split(" — ")[0] if pred_selected_label else ""

    # Also allow manual override
    manual = pred_tab.text_input(
        "Or type ticker manually",
        value="",
        placeholder="e.g. RELIANCE.NS",
        key="pred_manual_ticker",
    )
    if manual.strip():
        stock_ticker = manual.strip().upper()

    # Store in session state for the main page to pick up
    st.session_state["pred_stock_ticker"] = stock_ticker

    pred_tab.markdown(
        f"<p style='font-family:Space Mono,monospace;font-size:11px;"
        f"letter-spacing:1px;color:#0891b2;margin:4px 0 10px;'>"
        f"▶ {stock_ticker}</p>",
        unsafe_allow_html=True,
    )

    if pred_tab.button("▶ TRAIN MODEL AND PREDICT", key="pred_run_button",
                       on_click=tools.click_button_single_stock):
        predictions, df_predictions = train_predict_stock(stock_ticker)
        if predictions is not None and df_predictions is not None:
            with st.expander(f"📈 Prediction — {stock_ticker}", expanded=True):
                st.write("##### Predicted Prices (Next 15 days)")
                st.dataframe(df_predictions, use_container_width=True)
                fig = plot_prediction_graph(df_predictions)
                st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Geopolitical Risk Intel Tab
    # ------------------------------------------------------------------
    geo_tab.title("🌍 Global Risk Intel")
    geo_tab.markdown("Analyze how geopolitical events and macro trends are affecting markets.")

    geo_tab.subheader("News Sources")
    if "geo_news_sources" not in st.session_state:
        st.session_state["geo_news_sources"] = ["BBC World", "Reuters"]
    st.session_state["geo_news_sources"] = geo_tab.multiselect(
        "Select news sources",
        options=["BBC World", "Reuters", "Al Jazeera"],
        default=st.session_state["geo_news_sources"],
        key="geo_news_sources_select",
    )

    geo_tab.subheader("Country Focus")
    country_options = {
        "United States": "US",
        "China":         "CN",
        "India":         "IN",
        "Eurozone":      "EUU",
        "Brazil":        "BR",
    }
    if "geo_selected_countries" not in st.session_state:
        st.session_state["geo_selected_countries"] = ["United States", "China"]
    selected_countries = geo_tab.multiselect(
        "Countries for macro data",
        options=list(country_options.keys()),
        default=st.session_state["geo_selected_countries"],
        key="geo_country_select",
    )
    st.session_state["geo_selected_countries"] = selected_countries
    st.session_state["geo_country_codes"] = [country_options[c] for c in selected_countries]

    geo_tab.subheader("Performance Window")
    if "geo_period" not in st.session_state:
        st.session_state["geo_period"] = "3mo"
    st.session_state["geo_period"] = geo_tab.selectbox(
        "Asset return window",
        options=["1mo", "3mo", "6mo", "1y"],
        index=["1mo", "3mo", "6mo", "1y"].index(st.session_state["geo_period"]),
        key="geo_period_select",
    )

    st.session_state["load_geo"] = geo_tab.button(
        "Analyze Global Risk",
        key="geo_analyze_button",
        on_click=tools.click_button_geo,
    )


class LSTMModel(nn.Module):
    """Stacked LSTM model matching the project architecture: 100 → 75 → 50 units."""
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size=1, hidden_size=100, batch_first=True)
        self.dropout1 = nn.Dropout(0.3)
        self.lstm2 = nn.LSTM(input_size=100, hidden_size=75, batch_first=True)
        self.dropout2 = nn.Dropout(0.3)
        self.lstm3 = nn.LSTM(input_size=75, hidden_size=50, batch_first=True)
        self.dropout3 = nn.Dropout(0.3)
        self.fc = nn.Linear(50, 1)

    def forward(self, x):
        out, _ = self.lstm1(x)
        out = self.dropout1(out)
        out, _ = self.lstm2(out)
        out = self.dropout2(out)
        out, _ = self.lstm3(out)
        out = self.dropout3(out)
        out = self.fc(out[:, -1, :])  # Take last timestep output
        return out


def train_predict_stock(ticker: str):
    # Fetch historical stock data
    data = yf.download(ticker, period="1y", interval="1d", progress=False)

    if data.empty or len(data) < 61:
        st.error(
            f"Could not fetch enough data for **{ticker.upper()}**. "
            "Please check the ticker symbol and try again. "
            "(Minimum 61 trading days of history required.)"
        )
        return None, None

    data = data[['Close']].dropna()

    # Normalize the data (scaling between 0 and 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    # Prepare training sequences (60-day lookback)
    time_step = 60
    X_train, y_train = [], []
    for i in range(time_step, len(scaled_data)):
        X_train.append(scaled_data[i - time_step:i, 0])
        y_train.append(scaled_data[i, 0])

    X_tensor = torch.tensor(np.array(X_train), dtype=torch.float32).unsqueeze(-1)  # (N, 60, 1)
    y_tensor = torch.tensor(np.array(y_train), dtype=torch.float32).unsqueeze(-1)  # (N, 1)

    # Build LSTM model
    model = LSTMModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    # Train for 10 epochs as per project design
    model.train()
    for _ in range(10):
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()

    # Predict next 15 days iteratively
    model.eval()
    current_sequence = scaled_data[-time_step:].reshape(1, time_step, 1)
    predictions = []

    with torch.no_grad():
        for _ in range(15):
            input_tensor = torch.tensor(current_sequence, dtype=torch.float32)
            pred = model(input_tensor).item()
            predictions.append(pred)
            # Shift window forward by appending new prediction
            current_sequence = np.append(current_sequence[:, 1:, :], [[[pred]]], axis=1)

    # Inverse transform to original price scale
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

    # Create prediction dataframe
    future_dates = pd.date_range(start=data.index[-1], periods=16, freq='D')[1:]
    future_dates = future_dates.strftime('%Y-%m-%d')
    df_predictions = pd.DataFrame(predictions, columns=['Predicted Price'], index=future_dates)

    return predictions, df_predictions

def plot_prediction_graph(df_predictions):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_predictions.index, y=df_predictions['Predicted Price'],
                             mode='lines+markers', name='Predicted Price'))
    fig.update_layout(title="Stock Price Prediction for Next 15 Days",
                      xaxis_title="Date",
                      yaxis_title="Price (USD)",
                      hovermode="x unified")
    return fig
