import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Risk signal banner
# ---------------------------------------------------------------------------

def render_risk_signal_banner(risk_signal: dict) -> None:
    """Colored banner showing global risk level, sentiment score, and dominant theme."""
    level = risk_signal.get("risk_level", "Unknown")
    score = risk_signal.get("average_score", 0.0)
    theme = risk_signal.get("dominant_theme", "N/A")
    count = risk_signal.get("headline_count", 0)

    color_map = {
        "Low":     ("#f0fdf4", "#059669", "#bbf7d0"),
        "Medium":  ("#fffbeb", "#d97706", "#fde68a"),
        "High":    ("#fff7ed", "#ea580c", "#fed7aa"),
        "Severe":  ("#fef2f2", "#dc2626", "#fecaca"),
        "Unknown": ("#f8fafc", "#64748b", "#e2e8f0"),
    }
    bg, fg, border_bg = color_map.get(level, color_map["Unknown"])

    icons = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Severe": "🔴", "Unknown": "⚪"}
    icon = icons.get(level, "⚪")

    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {border_bg};
            border-left:5px solid {fg};
            padding:16px 22px;
            border-radius:12px;
            margin-bottom:14px;
            box-shadow:0 1px 4px rgba(15,23,42,.05);
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="font-size:20px;">{icon}</span>
                <span style="font-family:'Space Mono',monospace;font-size:18px;
                             font-weight:700;color:{fg};">
                    GLOBAL RISK: {level.upper()}
                </span>
            </div>
            <div style="display:flex;gap:24px;flex-wrap:wrap;">
                <span style="font-size:13px;color:#475569;">
                    Sentiment Score &nbsp;<b style="font-family:'Space Mono',monospace;color:#0f172a;">{score:.3f}</b>
                </span>
                <span style="font-size:13px;color:#475569;">
                    Dominant Theme &nbsp;<b style="color:#0f172a;">{theme}</b>
                </span>
                <span style="font-size:13px;color:#475569;">
                    Headlines &nbsp;<b style="font-family:'Space Mono',monospace;color:#0f172a;">{count}</b>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# AI Summary box
# ---------------------------------------------------------------------------

def render_ai_summary(summary_text: str) -> None:
    """Renders the AI-generated risk summary in a styled box."""
    # convert **bold** markdown to html
    import re
    html_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", summary_text)
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-radius:12px;
            padding:18px 22px;
            margin-bottom:10px;
            box-shadow:0 1px 4px rgba(15,23,42,.05);
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <div style="width:6px;height:6px;border-radius:50%;
                            background:#7c3aed;animation:none;"></div>
                <span style="font-family:'Space Mono',monospace;font-size:10px;
                             letter-spacing:1.5px;color:#7c3aed;font-weight:700;">
                    AI RISK ANALYSIS ENGINE
                </span>
            </div>
            <p style="color:#334155;font-size:13px;line-height:1.75;margin:0;">
                {html_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# VIX chart
# ---------------------------------------------------------------------------

def render_vix_chart(vix_df: pd.DataFrame) -> None:
    """Plotly line chart of VIX with low / elevated / panic threshold bands."""
    if vix_df.empty:
        st.warning("VIX data unavailable at this time.")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=vix_df.index,
        y=vix_df["VIX"],
        mode="lines",
        name="VIX",
        line=dict(color="#60a5fa", width=2),
    ))

    # Threshold bands
    fig.add_hrect(y0=0,  y1=20, fillcolor="green",  opacity=0.07, line_width=0,
                  annotation_text="Low fear",      annotation_position="top left")
    fig.add_hrect(y0=20, y1=30, fillcolor="yellow", opacity=0.07, line_width=0,
                  annotation_text="Elevated fear", annotation_position="top left")
    fig.add_hrect(y0=30, y1=100, fillcolor="red",   opacity=0.07, line_width=0,
                  annotation_text="Market panic",  annotation_position="top left")

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=20, b=0),
        height=320,
        yaxis_title="VIX Level",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#475569", family="DM Sans, sans-serif"),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Macro ETF heatmap
# ---------------------------------------------------------------------------

def render_macro_etf_heatmap(etf_df: pd.DataFrame) -> None:
    """Plotly heatmap of macro ETF % returns across 1W / 1M / 3M windows."""
    if etf_df.empty:
        st.warning("Macro ETF data unavailable at this time.")
        return

    fig = px.imshow(
        etf_df,
        text_auto=True,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        zmin=-15,
        zmax=15,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=280,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#475569", family="DM Sans, sans-serif"),
        coloraxis_showscale=True,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# News feed table
# ---------------------------------------------------------------------------

def render_news_feed_table(headlines: list, source_name: str = "") -> None:
    """Renders a styled DataFrame of news headlines with sentiment scores."""
    if not headlines or headlines[0].get("source") == "System":
        st.warning(f"No headlines available from {source_name or 'this source'}.")
        return

    rows = []
    for h in headlines:
        title = h.get("title", "")
        score = _score_to_label(h.get("title", ""))
        rows.append({
            "Title": title[:90] + "…" if len(title) > 90 else title,
            "Sentiment": score,
            "Published": h.get("published", "")[:20],
        })

    df = pd.DataFrame(rows)

    def _color_sentiment(val: str) -> str:
        if val == "Positive":
            return "background-color: #f0fdf4; color: #059669; font-weight:700"
        elif val == "Negative":
            return "background-color: #fef2f2; color: #dc2626; font-weight:700"
        return "background-color: #f8fafc; color: #64748b"

    from assets.GeoCollector import GeoCollector
    st.dataframe(
        df.style.map(_color_sentiment, subset=["Sentiment"]),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# Stock Impact Propagation chart + table
# ---------------------------------------------------------------------------

def render_stock_impact_section(impact_data: dict) -> None:
    """
    Renders:
      1. A normalised price-movement overlay chart (trigger + peers)
      2. A returns bar chart coloured green/red
      3. A correlation insight card
    """
    if "error" in impact_data:
        st.warning(f"Could not load impact data: {impact_data['error']}")
        return

    trigger    = impact_data["trigger"]
    sector     = impact_data["sector"]
    normed_df  = impact_data["normed_df"]
    returns    = impact_data["returns"]
    peers      = impact_data["peer_tickers"]

    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-left:5px solid #0891b2;
            border-radius:12px;
            padding:16px 22px;
            margin-bottom:16px;
            box-shadow:0 1px 4px rgba(15,23,42,.05);
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="font-size:20px;">📡</span>
                <span style="font-family:'Space Mono',monospace;font-size:16px;
                             font-weight:700;color:#0f172a;">
                    SECTOR RIPPLE — <span style="color:#0891b2;">{trigger}</span>
                </span>
            </div>
            <div style="display:flex;gap:20px;flex-wrap:wrap;">
                <span style="font-size:13px;color:#475569;">
                    Sector &nbsp;<b style="color:#0f172a;">{sector}</b>
                </span>
                <span style="font-size:13px;color:#475569;">
                    Peer companies tracked &nbsp;
                    <b style="font-family:'Space Mono',monospace;color:#0891b2;">{len(peers)}</b>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_chart, col_bar = st.columns([3, 2])

    with col_chart:
        st.markdown(
            "<p style='font-family:Space Mono,monospace;font-size:11px;"
            "letter-spacing:1px;color:#94a3b8;margin-bottom:6px;'>"
            "NORMALISED PRICE MOVEMENT (BASE = 100)</p>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()

        color_palette = [
            "#58a6ff", "#3fb950", "#f78166", "#d2a8ff",
            "#ffa657", "#79c0ff", "#56d364", "#ff7b72",
        ]

        for idx, col in enumerate(normed_df.columns):
            is_trigger = col == trigger
            fig.add_trace(go.Scatter(
                x=normed_df.index,
                y=normed_df[col],
                mode="lines",
                name=col,
                line=dict(
                    color=color_palette[idx % len(color_palette)],
                    width=3 if is_trigger else 1.5,
                    dash="solid" if is_trigger else "dot",
                ),
                opacity=1.0 if is_trigger else 0.75,
            ))

        fig.update_layout(
            height=340,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#475569", family="DM Sans, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="left", x=0,
                font=dict(size=11, color="#475569"),
                bgcolor="rgba(255,255,255,0)",
            ),
            xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=11)),
            yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0",
                       title="Index (100 = start)", tickfont=dict(size=11)),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_bar:
        st.markdown(
            "<p style='font-family:Space Mono,monospace;font-size:11px;"
            "letter-spacing:1px;color:#94a3b8;margin-bottom:6px;'>% RETURN OVER PERIOD</p>",
            unsafe_allow_html=True,
        )
        if returns:
            tickers = list(returns.keys())
            vals    = list(returns.values())
            colors  = ["#059669" if v >= 0 else "#dc2626" for v in vals]

            bar_fig = go.Figure(go.Bar(
                x=vals,
                y=tickers,
                orientation="h",
                marker_color=colors,
                marker_line_width=0,
                text=[f"{v:+.2f}%" for v in vals],
                textposition="outside",
                textfont=dict(family="Space Mono, monospace", size=11),
            ))
            bar_fig.update_layout(
                height=340,
                margin=dict(l=0, r=70, t=10, b=0),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                font=dict(color="#475569", family="DM Sans, sans-serif"),
                xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0",
                           title="Return (%)", tickfont=dict(size=11)),
                yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0",
                           tickfont=dict(family="Space Mono, monospace", size=11,
                                        color="#0891b2")),
            )
            st.plotly_chart(bar_fig, use_container_width=True)

    # Insight card
    trigger_ret = returns.get(trigger, 0)
    peer_rets   = [returns[t] for t in peers if t in returns]
    if peer_rets:
        avg_peer  = round(sum(peer_rets) / len(peer_rets), 2)
        direction = "declined" if trigger_ret < 0 else "gained"
        peer_dir  = "also fell" if avg_peer < 0 else "rose"
        ret_color = "#dc2626" if trigger_ret < 0 else "#059669"
        avg_color = "#dc2626" if avg_peer < 0 else "#059669"
        insight_html = (
            f"<b style='font-family:Space Mono,monospace;color:#0891b2'>{trigger}</b> "
            f"{direction} "
            f"<b style='font-family:Space Mono,monospace;color:{ret_color}'>{trigger_ret:+.2f}%</b> "
            f"over this period. Sector peers {peer_dir} by an average of "
            f"<b style='font-family:Space Mono,monospace;color:{avg_color}'>{avg_peer:+.2f}%</b>, "
            + ("confirming broad sector pressure." if (trigger_ret < 0 and avg_peer < 0)
               else "showing mixed divergence from the trigger stock.")
        )
    else:
        ret_color = "#dc2626" if trigger_ret < 0 else "#059669"
        insight_html = (
            f"<b style='font-family:Space Mono,monospace;color:#0891b2'>{trigger}</b> returned "
            f"<b style='font-family:Space Mono,monospace;color:{ret_color}'>{trigger_ret:+.2f}%</b> "
            f"over the selected period. No peer data available for comparison."
        )

    st.markdown(
        f"""
        <div style="
            background:#fffbeb;
            border:1px solid #fde68a;
            border-left:4px solid #d97706;
            border-radius:10px;
            padding:14px 20px;
            margin-top:6px;
        ">
            <div style="font-family:'Space Mono',monospace;font-size:10px;
                        letter-spacing:1.5px;color:#d97706;font-weight:700;
                        margin-bottom:8px;">
                💡 IMPACT INSIGHT
            </div>
            <p style="color:#334155;font-size:13px;line-height:1.7;margin:0;">
                {insight_html}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _score_to_label(headline: str) -> str:
    from assets.GeoCollector import GeoCollector
    score = GeoCollector.score_headline_sentiment(headline)
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    return "Neutral"


# ---------------------------------------------------------------------------
# World Bank bar chart
# ---------------------------------------------------------------------------

def render_worldbank_chart(wb_df: pd.DataFrame, label: str) -> None:
    """Plotly bar chart for a World Bank indicator across years."""
    if wb_df.empty:
        st.info(f"World Bank data unavailable for: {label}")
        return

    colors = [
        "#34d399" if v >= 0 else "#f87171"
        for v in wb_df["value"]
    ]

    fig = go.Figure(go.Bar(
        x=wb_df["year"],
        y=wb_df["value"],
        text=wb_df["value"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        marker_color=colors,
    ))
    fig.update_layout(
        title=dict(text=label, font=dict(size=12, color="#475569", family="Space Mono, monospace")),
        xaxis_title="Year",
        yaxis_title="%",
        margin=dict(l=0, r=0, t=44, b=0),
        height=260,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#475569", family="DM Sans, sans-serif"),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickfont=dict(size=10)),
    )
    st.plotly_chart(fig, use_container_width=True)
