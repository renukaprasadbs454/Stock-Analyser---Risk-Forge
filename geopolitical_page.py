import streamlit as st
import geopolitical_page_components as geo_comp
from assets.GeoCollector import GeoCollector, SECTOR_PEERS


def _section(icon: str, label: str) -> None:
    """Render a refer.html–style section title divider."""
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;
                    margin:1.4rem 0 .7rem;">
            <span style="font-size:16px;">{icon}</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;
                         letter-spacing:2px;color:#94a3b8;font-weight:700;">
                {label}
            </span>
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_page() -> None:
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background:#ffffff;
            border:1px solid #e2e8f0;
            border-left:5px solid #0891b2;
            border-radius:14px;
            padding:20px 28px;
            margin-bottom:20px;
            box-shadow:0 1px 4px rgba(15,23,42,.06);
        ">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
                <span style="font-size:28px;">🌍</span>
                <span style="font-family:'Space Mono',monospace;font-size:20px;
                             font-weight:700;letter-spacing:1px;color:#0f172a;">
                    GLOBAL RISK INTELLIGENCE
                </span>
            </div>
            <p style="color:#475569;margin:0;font-size:13px;line-height:1.6;">
                Monitor how <b style="color:#0891b2;">geopolitical events, elections, budgets, and macro policy</b>
                are affecting market sentiment and asset prices in real time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Read sidebar selections
    selected_sources = st.session_state.get("geo_news_sources",  ["BBC World", "Reuters"])
    country_codes    = st.session_state.get("geo_country_codes", ["US", "CN"])
    period           = st.session_state.get("geo_period",         "3mo")

    # ── Step 1: Fetch news & compute risk signal ──────────────────────────────
    with st.spinner("Fetching live news & computing risk signal..."):
        all_headlines = []
        source_map = {name: url for name, url in GeoCollector.RSS_FEEDS.items()
                      if name in selected_sources}

        for source_name, url in source_map.items():
            headlines = GeoCollector.fetch_rss_headlines(url, max_items=8)
            for h in headlines:
                h["source"] = source_name
            all_headlines.extend(headlines)

        if not all_headlines:
            all_headlines = [{"title": "No news available", "source": "System",
                              "link": "", "published": "", "summary": ""}]

        risk_signal = GeoCollector.compute_risk_signal(all_headlines)

    # ── Step 2: Fetch macro ETF data ──────────────────────────────────────────
    with st.spinner("Loading macro asset data..."):
        etf_df = GeoCollector.fetch_macro_etf_data(period=period)

    # ── Risk banner + AI summary ──────────────────────────────────────────────
    geo_comp.render_risk_signal_banner(risk_signal)

    _section("🧠", "TODAY'S RISK SUMMARY")
    ai_text = GeoCollector.generate_ai_summary(risk_signal, etf_df)
    geo_comp.render_ai_summary(ai_text)

    st.divider()

    # ── Row 1: VIX | Macro ETF heatmap ───────────────────────────────────────
    _section("📉", "MARKET FEAR INDEX  ·  MACRO ASSET RETURNS")
    col_vix, col_heat = st.columns(2)

    with col_vix:
        st.markdown(
            "<p style='font-family:Space Mono,monospace;font-size:11px;"
            "letter-spacing:1.5px;color:#94a3b8;margin-bottom:6px;'>VIX — 6 MONTH</p>",
            unsafe_allow_html=True,
        )
        with st.spinner("Loading VIX data..."):
            vix_df = GeoCollector.fetch_vix_history(period="6mo")
        geo_comp.render_vix_chart(vix_df)

    with col_heat:
        st.markdown(
            "<p style='font-family:Space Mono,monospace;font-size:11px;"
            "letter-spacing:1.5px;color:#94a3b8;margin-bottom:6px;'>MACRO ETF RETURNS</p>",
            unsafe_allow_html=True,
        )
        geo_comp.render_macro_etf_heatmap(etf_df)

    st.divider()

    # ── Row 2: World Bank macro data ─────────────────────────────────────────
    _section("🏛️", "MACROECONOMIC CONTEXT  (WORLD BANK)")

    country_label_map = {
        "US":  "United States", "CN": "China", "IN": "India",
        "EUU": "Eurozone",      "BR": "Brazil", "RU": "Russia",
    }

    wb_cols = st.columns(max(min(len(country_codes), 3), 1))

    with st.spinner("Fetching World Bank macro data..."):
        for idx, code in enumerate(country_codes[:3]):
            label = country_label_map.get(code, code)
            with wb_cols[idx]:
                st.markdown(
                    f"<p style='font-family:Space Mono,monospace;font-size:11px;"
                    f"letter-spacing:1px;color:#475569;font-weight:700;margin-bottom:4px;'>{label.upper()}</p>",
                    unsafe_allow_html=True,
                )
                gdp_df = GeoCollector.fetch_worldbank_indicator(code, "NY.GDP.MKTP.KD.ZG")
                geo_comp.render_worldbank_chart(gdp_df, f"GDP Growth (%) — {label}")

    st.divider()

    # ── Row 3: Stock Impact Propagation Analyzer ──────────────────────────────
    _section("📡", "STOCK IMPACT PROPAGATION ANALYZER")
    st.markdown(
        "<p style='color:#475569;font-size:13px;margin:-4px 0 12px;'>"
        "Select a trigger stock — see how a geopolitical event ripples through its entire sector peer group."
        "</p>",
        unsafe_allow_html=True,
    )

    available_triggers = sorted(SECTOR_PEERS.keys())
    col_sel, col_per, col_btn = st.columns([2, 1, 1])
    with col_sel:
        trigger_stock = st.selectbox(
            "Trigger Stock",
            options=available_triggers,
            index=available_triggers.index("INFY") if "INFY" in available_triggers else 0,
            key="geo_trigger_stock",
        )
    with col_per:
        impact_period = st.selectbox(
            "Look-back Window",
            options=["1mo", "3mo", "6mo", "1y"],
            index=1,
            key="geo_impact_period",
        )
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_impact = st.button("▶ ANALYZE IMPACT", key="geo_impact_btn")

    if run_impact:
        with st.spinner(f"Fetching price data for {trigger_stock} and its sector peers…"):
            impact_data = GeoCollector.fetch_stock_impact_data(trigger_stock, period=impact_period)
        geo_comp.render_stock_impact_section(impact_data)
    else:
        st.markdown(
            """
            <div style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:10px;
                        padding:20px 24px;text-align:center;color:#94a3b8;font-size:13px;">
                Select a stock above and click <b style="color:#0891b2;">▶ ANALYZE IMPACT</b>
                to visualise the sector ripple effect.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Row 4: Live news feed ─────────────────────────────────────────────────
    _section("📰", "LIVE GEOPOLITICAL NEWS FEED")

    for source_name in selected_sources:
        source_headlines = [h for h in all_headlines if h.get("source") == source_name]
        if source_headlines:
            with st.expander(f"📰  {source_name}", expanded=(source_name == selected_sources[0])):
                geo_comp.render_news_feed_table(source_headlines, source_name)
