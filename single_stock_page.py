"""
Single-stock deep-analysis page.
Shows: price metrics, LSTM prediction, technical signals, risk profile.
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn


# ── helpers ──────────────────────────────────────────────────────────────────

def _section(icon: str, label: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:1.4rem 0 .7rem;">
            <span style="font-size:16px;">{icon}</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;
                         letter-spacing:2px;color:#94a3b8;font-weight:700;">{label}</span>
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _badge(label: str, kind: str = "cyan") -> str:
    colors = {
        "green":  ("rgba(5,150,105,.12)",  "#059669"),
        "red":    ("rgba(220,38,38,.10)",   "#dc2626"),
        "amber":  ("rgba(217,119,6,.12)",   "#d97706"),
        "cyan":   ("rgba(8,145,178,.10)",   "#0891b2"),
        "violet": ("rgba(124,58,237,.10)",  "#7c3aed"),
    }
    bg, fg = colors.get(kind, colors["cyan"])
    return (
        f"<span style='font-family:Space Mono,monospace;font-size:10px;"
        f"font-weight:700;letter-spacing:.5px;padding:3px 9px;border-radius:5px;"
        f"background:{bg};color:{fg};'>{label}</span>"
    )


def _metric_card(title: str, value: str, sub: str = "", color: str = "#0f172a") -> str:
    return f"""
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;
                padding:18px 20px;box-shadow:0 1px 4px rgba(15,23,42,.06);">
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:1.5px;
                    color:#94a3b8;text-transform:uppercase;margin-bottom:8px;">{title}</div>
        <div style="font-family:'Space Mono',monospace;font-size:26px;font-weight:700;
                    color:{color};line-height:1;">{value}</div>
        {"<div style='font-size:12px;color:#94a3b8;margin-top:4px;'>"+sub+"</div>" if sub else ""}
    </div>"""


# ── LSTM (same architecture as side_bar.py) ──────────────────────────────────

class _LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm1   = nn.LSTM(1, 100, batch_first=True)
        self.drop1   = nn.Dropout(0.3)
        self.lstm2   = nn.LSTM(100, 75, batch_first=True)
        self.drop2   = nn.Dropout(0.3)
        self.lstm3   = nn.LSTM(75, 50, batch_first=True)
        self.drop3   = nn.Dropout(0.3)
        self.fc      = nn.Linear(50, 1)

    def forward(self, x):
        o, _ = self.lstm1(x);  o = self.drop1(o)
        o, _ = self.lstm2(o);  o = self.drop2(o)
        o, _ = self.lstm3(o);  o = self.drop3(o)
        return self.fc(o[:, -1, :])


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def _run_lstm(close_series: pd.Series, horizon: int = 15):
    data = close_series.dropna().values.reshape(-1, 1)
    if len(data) < 61:
        return None, None
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    step   = 60
    X, y   = [], []
    for i in range(step, len(scaled)):
        X.append(scaled[i - step:i, 0])
        y.append(scaled[i, 0])
    Xt = torch.tensor(np.array(X), dtype=torch.float32).unsqueeze(-1)
    yt = torch.tensor(np.array(y), dtype=torch.float32).unsqueeze(-1)
    model = _LSTM()
    opt   = torch.optim.Adam(model.parameters(), lr=0.001)
    crit  = nn.MSELoss()
    model.train()
    for _ in range(10):
        opt.zero_grad()
        loss = crit(model(Xt), yt)
        loss.backward()
        opt.step()
    model.eval()
    seq = scaled[-step:].reshape(1, step, 1)
    preds = []
    with torch.no_grad():
        for _ in range(horizon):
            inp  = torch.tensor(seq, dtype=torch.float32)
            p    = model(inp).item()
            preds.append(p)
            seq  = np.append(seq[:, 1:, :], [[[p]]], axis=1)
    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    return preds, scaler


def _compute_technicals(df: pd.DataFrame) -> dict:
    close = df["Close"].squeeze()
    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = round(float((100 - 100 / (1 + rs)).iloc[-1]), 1)
    # SMAs
    sma50  = round(float(close.rolling(50).mean().iloc[-1]), 2)
    sma200 = round(float(close.rolling(200).mean().iloc[-1]), 2) if len(close) >= 200 else None
    # MACD
    ema12  = close.ewm(span=12).mean()
    ema26  = close.ewm(span=26).mean()
    macd   = round(float((ema12 - ema26).iloc[-1]), 2)
    # Bollinger
    sma20  = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    bb_up  = round(float((sma20 + 2 * std20).iloc[-1]), 2)
    bb_lo  = round(float((sma20 - 2 * std20).iloc[-1]), 2)
    # Volatility (ann.)
    vol    = round(float(close.pct_change().std() * np.sqrt(252) * 100), 1)
    # Current price
    price  = round(float(close.iloc[-1]), 2)
    hi52   = round(float(close.rolling(252).max().iloc[-1]), 2)
    lo52   = round(float(close.rolling(252).min().iloc[-1]), 2)
    return dict(rsi=rsi, sma50=sma50, sma200=sma200, macd=macd,
                bb_up=bb_up, bb_lo=bb_lo, vol=vol,
                price=price, hi52=hi52, lo52=lo52)


# ── main page ─────────────────────────────────────────────────────────────────

def load_page() -> None:
    ticker = st.session_state.get("pred_stock_ticker", "")

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-left:5px solid #0891b2;
                    border-radius:14px;padding:18px 24px;margin-bottom:18px;
                    box-shadow:0 1px 4px rgba(15,23,42,.06);">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                <span style="font-size:24px;">📊</span>
                <span style="font-family:'Space Mono',monospace;font-size:18px;
                             font-weight:700;letter-spacing:1px;color:#0f172a;">
                    SINGLE STOCK ANALYSIS
                </span>
                <span style="font-family:'Space Mono',monospace;font-size:14px;
                             color:#0891b2;font-weight:700;background:rgba(8,145,178,.08);
                             padding:3px 10px;border-radius:6px;">{ticker or "—"}</span>
            </div>
            <p style="color:#475569;font-size:13px;margin:0;">
                LSTM price prediction · technical indicators · risk profile
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not ticker:
        st.info("Select a stock from the **Prediction** tab in the sidebar, then click **▶ TRAIN MODEL AND PREDICT**.")
        return

    # ── Fetch data ────────────────────────────────────────────────────────────
    with st.spinner(f"Loading market data for {ticker}…"):
        df = _fetch_history(ticker, period="2y")

    if df.empty or len(df) < 61:
        st.error(f"Not enough data for **{ticker}**. Check the ticker symbol.")
        return

    close = df["Close"].squeeze()
    tech  = _compute_technicals(df)

    # ── Price metric cards ────────────────────────────────────────────────────
    _section("💰", "PRICE SNAPSHOT")

    price     = tech["price"]
    prev      = round(float(close.iloc[-2]), 2)
    change    = round(price - prev, 2)
    pct       = round(change / prev * 100, 2)
    chg_color = "#059669" if change >= 0 else "#dc2626"
    chg_arrow = "▲" if change >= 0 else "▼"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_metric_card("Current Price", f"${price:,.2f}",
                    f"<span style='color:{chg_color};font-weight:700;font-family:Space Mono,monospace;'>"
                    f"{chg_arrow} {change:+.2f} ({pct:+.2f}%)</span> today", chg_color),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card("52-Week High", f"${tech['hi52']:,.2f}", "Annual peak"), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card("52-Week Low",  f"${tech['lo52']:,.2f}", "Annual trough"), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card("Ann. Volatility", f"{tech['vol']}%",
                    "Higher = more risk", "#d97706"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Price history chart ───────────────────────────────────────────────────
    _section("📈", "PRICE HISTORY")

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=close.index, y=close.values,
        mode="lines", name="Close",
        line=dict(color="#0891b2", width=2),
        fill="tozeroy",
        fillcolor="rgba(8,145,178,.06)",
    ))
    # SMA overlays
    fig_hist.add_trace(go.Scatter(
        x=close.index, y=close.rolling(50).mean().values,
        mode="lines", name="SMA 50",
        line=dict(color="#7c3aed", width=1.2, dash="dot"),
    ))
    if len(close) >= 200:
        fig_hist.add_trace(go.Scatter(
            x=close.index, y=close.rolling(200).mean().values,
            mode="lines", name="SMA 200",
            line=dict(color="#d97706", width=1.2, dash="dash"),
        ))
    fig_hist.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(color="#475569", family="DM Sans, sans-serif"),
        legend=dict(orientation="h", y=1.06, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11),
                   title="Price"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    # ── LSTM Prediction ───────────────────────────────────────────────────────
    _section("🤖", "LSTM PRICE PREDICTION  (NEXT 15 DAYS)")

    with st.spinner("Training LSTM model…"):
        preds, _ = _run_lstm(close, horizon=15)

    if preds is None:
        st.warning("Not enough historical data to run the LSTM model (need ≥ 61 days).")
    else:
        future_dates = pd.date_range(start=close.index[-1], periods=16, freq="B")[1:]
        pred_df = pd.DataFrame({"Date": future_dates, "Predicted Price": preds.round(2)})

        # build confidence bands ±2%
        low_band  = preds * 0.98
        high_band = preds * 1.02

        col_chart, col_table = st.columns([3, 2])

        with col_chart:
            last_n = 30
            hist_x = close.index[-last_n:]
            hist_y = close.values[-last_n:]

            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=hist_x, y=hist_y,
                mode="lines", name="Historical",
                line=dict(color="#94a3b8", width=1.5),
            ))
            fig_pred.add_trace(go.Scatter(
                x=future_dates, y=high_band,
                mode="lines", name="Upper Band",
                line=dict(color="rgba(8,145,178,.3)", width=0),
                showlegend=False,
            ))
            fig_pred.add_trace(go.Scatter(
                x=future_dates, y=low_band,
                mode="lines", name="Confidence Band",
                fill="tonexty",
                fillcolor="rgba(8,145,178,.08)",
                line=dict(color="rgba(8,145,178,.3)", width=0),
            ))
            fig_pred.add_trace(go.Scatter(
                x=future_dates, y=preds,
                mode="lines+markers", name="Predicted",
                line=dict(color="#0891b2", width=2.5, dash="dot"),
                marker=dict(size=5, color="#0891b2"),
            ))
            # connector
            fig_pred.add_trace(go.Scatter(
                x=[close.index[-1], future_dates[0]],
                y=[float(close.iloc[-1]), preds[0]],
                mode="lines", showlegend=False,
                line=dict(color="#0891b2", width=1.5, dash="dot"),
            ))
            fig_pred.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                font=dict(color="#475569", family="DM Sans, sans-serif"),
                legend=dict(orientation="h", y=1.06, font=dict(size=11),
                            bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
                yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
                hovermode="x unified",
            )
            st.plotly_chart(fig_pred, use_container_width=True)

        with col_table:
            st.markdown(
                "<p style='font-family:Space Mono,monospace;font-size:10px;"
                "letter-spacing:1.5px;color:#94a3b8;margin-bottom:6px;'>FORECAST TABLE</p>",
                unsafe_allow_html=True,
            )
            display_df = pred_df.copy()
            display_df["Date"] = display_df["Date"].dt.strftime("%b %d")
            display_df["Low"]  = (preds * 0.98).round(2)
            display_df["High"] = (preds * 1.02).round(2)
            display_df["Chg"] = (preds - float(close.iloc[-1])).round(2)
            display_df = display_df.rename(columns={"Predicted Price": "Target"})
            st.dataframe(
                display_df[["Date", "Low", "Target", "High"]].style
                    .format({"Low": "${:.2f}", "Target": "${:.2f}", "High": "${:.2f}"}),
                use_container_width=True,
                hide_index=True,
                height=300,
            )

    st.divider()

    # ── Technical Signals + Risk Profile ─────────────────────────────────────
    col_tech, col_risk = st.columns(2)

    with col_tech:
        _section("⚙️", "TECHNICAL SIGNALS")

        rsi = tech["rsi"]
        rsi_badge  = _badge("OVERBOUGHT", "red") if rsi > 70 else (_badge("OVERSOLD", "green") if rsi < 30 else _badge("NEUTRAL", "amber"))
        macd_badge = _badge("BULLISH", "green") if tech["macd"] > 0 else _badge("BEARISH", "red")
        sma50_badge  = _badge("ABOVE", "green") if price > tech["sma50"]  else _badge("BELOW", "red")
        sma200_badge = (_badge("ABOVE", "green") if price > tech["sma200"] else _badge("BELOW", "red")) if tech["sma200"] else _badge("N/A", "cyan")
        bb_badge = _badge("WITHIN BANDS", "cyan") if tech["bb_lo"] < price < tech["bb_up"] else _badge("OUTSIDE BANDS", "amber")

        rows = [
            ("RSI (14)",          f"{rsi}",                          rsi_badge),
            ("MACD",              f"{tech['macd']:+.2f}",            macd_badge),
            ("SMA 50",            f"${tech['sma50']:,.2f}",          sma50_badge),
            ("SMA 200",           f"${tech['sma200']:,.2f}" if tech["sma200"] else "—", sma200_badge),
            ("Bollinger Upper",   f"${tech['bb_up']:,.2f}",          ""),
            ("Bollinger Lower",   f"${tech['bb_lo']:,.2f}",          bb_badge),
        ]

        table_rows = "".join(
            f"""<div style='display:flex;align-items:center;justify-content:space-between;
                            padding:9px 0;border-bottom:1px solid #f1f5f9;'>
                    <span style='font-size:13px;color:#334155;font-weight:500;'>{name}</span>
                    <div style='display:flex;align-items:center;gap:8px;'>
                        <span style='font-family:Space Mono,monospace;font-size:12px;
                                     color:#475569;'>{val}</span>
                        {badge}
                    </div>
                </div>"""
            for name, val, badge in rows
        )
        st.markdown(
            f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
            f"padding:16px 20px;box-shadow:0 1px 4px rgba(15,23,42,.05);'>{table_rows}</div>",
            unsafe_allow_html=True,
        )

        # Overall signal
        bullish = sum([
            price > tech["sma50"],
            price > (tech["sma200"] or 0),
            tech["macd"] > 0,
            30 < rsi < 70,
            tech["bb_lo"] < price < tech["bb_up"],
        ])
        sig_color = "#059669" if bullish >= 4 else ("#dc2626" if bullish <= 1 else "#d97706")
        sig_label = "BUY" if bullish >= 4 else ("SELL" if bullish <= 1 else "HOLD")
        st.markdown(
            f"""<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                            padding:16px 20px;margin-top:10px;
                            box-shadow:0 1px 4px rgba(15,23,42,.05);
                            display:flex;align-items:center;gap:16px;'>
                    <span style='font-family:Space Mono,monospace;font-size:36px;
                                 font-weight:700;color:{sig_color};'>{sig_label}</span>
                    <div>
                        <div style='font-size:12px;color:#475569;'>Overall Signal</div>
                        <div style='font-size:12px;color:#94a3b8;margin-top:2px;'>
                            {bullish}/5 indicators positive
                        </div>
                    </div>
                </div>""",
            unsafe_allow_html=True,
        )

    with col_risk:
        _section("🛡️", "RISK PROFILE")

        vol = tech["vol"]
        risk_score = min(100, int(vol * 2.5))
        risk_label = "LOW" if risk_score < 30 else ("HIGH" if risk_score > 65 else "MODERATE")
        risk_color = "#059669" if risk_score < 30 else ("#dc2626" if risk_score > 65 else "#d97706")

        # Risk meter (10 bars)
        filled = round(risk_score / 10)
        bars   = "".join(
            f"<div style='flex:1;height:8px;border-radius:4px;"
            f"background:{'#dc2626' if i < filled and risk_score > 65 else '#d97706' if i < filled and risk_score > 30 else '#059669' if i < filled else '#e2e8f0'};'></div>"
            for i in range(10)
        )

        # Max drawdown
        roll_max  = close.cummax()
        drawdowns = (close - roll_max) / roll_max * 100
        max_dd    = round(float(drawdowns.min()), 1)

        # Annualised return
        ann_ret = round(float(((close.iloc[-1] / close.iloc[0]) ** (252 / len(close)) - 1) * 100), 1)

        st.markdown(
            f"""
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                        padding:20px;box-shadow:0 1px 4px rgba(15,23,42,.05);'>
                <div style='font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;
                            color:#94a3b8;margin-bottom:12px;'>RISK SCORE</div>
                <div style='display:flex;align-items:flex-end;gap:12px;margin-bottom:10px;'>
                    <span style='font-family:Space Mono,monospace;font-size:48px;
                                 font-weight:700;color:{risk_color};line-height:1;'>{risk_score}</span>
                    <div>
                        <div style='font-size:13px;color:{risk_color};font-weight:700;'>{risk_label} RISK</div>
                        <div style='font-size:12px;color:#94a3b8;'>out of 100</div>
                    </div>
                </div>
                <div style='display:flex;gap:4px;margin-bottom:6px;'>{bars}</div>
                <div style='display:flex;justify-content:space-between;font-family:Space Mono,monospace;
                            font-size:9px;color:#94a3b8;letter-spacing:1px;margin-bottom:16px;'>
                    <span>LOW</span><span>MODERATE</span><span>HIGH</span>
                </div>
                <div style='display:flex;flex-direction:column;gap:0;'>
                    <div style='display:flex;justify-content:space-between;padding:9px 0;
                                border-bottom:1px solid #f1f5f9;font-size:13px;'>
                        <span style='color:#334155;font-weight:500;'>Ann. Volatility</span>
                        <span style='font-family:Space Mono,monospace;color:#475569;'>{vol}%</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:9px 0;
                                border-bottom:1px solid #f1f5f9;font-size:13px;'>
                        <span style='color:#334155;font-weight:500;'>Max Drawdown</span>
                        <span style='font-family:Space Mono,monospace;color:#dc2626;'>{max_dd}%</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;padding:9px 0;
                                font-size:13px;'>
                        <span style='color:#334155;font-weight:500;'>Ann. Return (2Y)</span>
                        <span style='font-family:Space Mono,monospace;
                                     color:{"#059669" if ann_ret >= 0 else "#dc2626"};'>{ann_ret:+.1f}%</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
