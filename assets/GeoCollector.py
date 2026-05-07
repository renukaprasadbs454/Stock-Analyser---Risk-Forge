import feedparser
import requests
import pandas as pd
import yfinance as yf
import streamlit as st


# ---------------------------------------------------------------------------
# Keyword dictionaries for lightweight NLP-based sentiment scoring
# ---------------------------------------------------------------------------

NEGATIVE_KEYWORDS = {
    "war": -0.9, "conflict": -0.7, "sanction": -0.7, "crisis": -0.8,
    "crash": -0.9, "recession": -0.8, "default": -0.85, "tariff": -0.5,
    "blockade": -0.6, "ban": -0.4, "attack": -0.7, "missile": -0.8,
    "inflation": -0.4, "drought": -0.3, "protest": -0.3, "coup": -0.9,
    "collapse": -0.85, "downgrade": -0.6, "strike": -0.4, "election":  -0.1,
    "tension": -0.5, "risk": -0.3, "threat": -0.6, "shortage": -0.5,
    "debt": -0.4, "deficit": -0.4, "nuclear": -0.7, "invasion": -0.9,
    "terror": -0.8, "earthquake": -0.6, "flood": -0.4, "pandemic": -0.7,
}

POSITIVE_KEYWORDS = {
    "ceasefire": 0.8, "deal": 0.5, "stimulus": 0.6, "growth": 0.5,
    "recovery": 0.6, "rate cut": 0.7, "agreement": 0.5, "trade deal": 0.7,
    "peace": 0.8, "reform": 0.4, "upgrade": 0.5, "surplus": 0.4,
    "aid": 0.3, "boost": 0.4, "rally": 0.5, "rebound": 0.5,
    "alliance": 0.4, "invest": 0.4, "negotiate": 0.3, "resolve": 0.4,
}


# ---------------------------------------------------------------------------
# Sector peer mapping for stock impact propagation
# ---------------------------------------------------------------------------

SECTOR_PEERS = {
    # IT Services — India-centric
    "INFY":        {"sector": "IT Services (India)", "peers": ["TCS.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "MPHASIS.NS"]},
    "TCS.NS":      {"sector": "IT Services (India)", "peers": ["INFY", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"]},
    "WIPRO.NS":    {"sector": "IT Services (India)", "peers": ["INFY", "TCS.NS", "HCLTECH.NS", "MPHASIS.NS"]},
    "HCLTECH.NS":  {"sector": "IT Services (India)", "peers": ["INFY", "TCS.NS", "WIPRO.NS", "TECHM.NS"]},
    "TECHM.NS":    {"sector": "IT Services (India)", "peers": ["INFY", "TCS.NS", "WIPRO.NS", "HCLTECH.NS"]},
    # US Big Tech
    "AAPL":   {"sector": "Big Tech (US)", "peers": ["MSFT", "GOOG", "META", "AMZN"]},
    "MSFT":   {"sector": "Big Tech (US)", "peers": ["AAPL", "GOOG", "META", "AMZN"]},
    "GOOG":   {"sector": "Big Tech (US)", "peers": ["AAPL", "MSFT", "META", "AMZN"]},
    "META":   {"sector": "Big Tech (US)", "peers": ["AAPL", "MSFT", "GOOG", "SNAP"]},
    "AMZN":   {"sector": "Big Tech (US)", "peers": ["AAPL", "MSFT", "GOOG", "SHOP"]},
    # Semiconductors
    "NVDA":   {"sector": "Semiconductors", "peers": ["AMD", "INTC", "QCOM", "AVGO", "MU"]},
    "AMD":    {"sector": "Semiconductors", "peers": ["NVDA", "INTC", "QCOM", "MU"]},
    "INTC":   {"sector": "Semiconductors", "peers": ["NVDA", "AMD", "QCOM", "TXN"]},
    "QCOM":   {"sector": "Semiconductors", "peers": ["NVDA", "AMD", "INTC", "AVGO"]},
    # Banking
    "JPM":    {"sector": "Banking (US)", "peers": ["BAC", "GS", "MS", "WFC", "C"]},
    "BAC":    {"sector": "Banking (US)", "peers": ["JPM", "GS", "MS", "WFC"]},
    "GS":     {"sector": "Banking (US)", "peers": ["JPM", "BAC", "MS", "C"]},
    # EV / Automotive
    "TSLA":   {"sector": "EV / Auto", "peers": ["NIO", "RIVN", "F", "GM"]},
}


class GeoCollector:
    """
    Data collector for geopolitical and macroeconomic market signals.
    Uses only free, no-API-key data sources for the MVP.
    """

    RSS_FEEDS = {
        "BBC World":   "http://feeds.bbci.co.uk/news/world/rss.xml",
        "Reuters":     "https://feeds.reuters.com/reuters/worldNews",
        "Al Jazeera":  "https://www.aljazeera.com/xml/rss/all.xml",
    }

    # Kept small to avoid yfinance lag (user feedback)
    MACRO_TICKERS = {
        "VIX (Fear)": "^VIX",
        "Gold (GLD)":  "GLD",
        "Energy (XLE)": "XLE",
        "Financials (XLF)": "XLF",
    }

    WORLDBANK_INDICATORS = {
        "GDP Growth (%)":   "NY.GDP.MKTP.KD.ZG",
        "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
    }

    # ------------------------------------------------------------------
    # RSS / News
    # ------------------------------------------------------------------

    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_rss_headlines(feed_url: str, max_items: int = 8) -> list:
        """
        Parse an RSS feed and return a list of headline dicts.
        Falls back gracefully if the feed fails or returns nothing.
        """
        try:
            feed = feedparser.parse(feed_url)
            headlines = []
            for entry in feed.entries[:max_items]:
                headlines.append({
                    "title":     entry.get("title", "No title"),
                    "link":      entry.get("link", ""),
                    "published": entry.get("published", "Unknown"),
                    "summary":   entry.get("summary", ""),
                })
            if not headlines:
                return [{"title": "No news available", "source": "System",
                         "link": "", "published": "", "summary": ""}]
            return headlines
        except Exception:
            return [{"title": "No news available", "source": "System",
                     "link": "", "published": "", "summary": ""}]

    # ------------------------------------------------------------------
    # Sentiment scoring
    # ------------------------------------------------------------------

    @staticmethod
    def score_headline_sentiment(headline: str) -> float:
        """
        Lightweight NLP-based keyword scoring model.
        Returns a polarity score in [-1.0, +1.0].
        """
        text = headline.lower()
        score = 0.0
        for kw, weight in NEGATIVE_KEYWORDS.items():
            if kw in text:
                score += weight
        for kw, weight in POSITIVE_KEYWORDS.items():
            if kw in text:
                score += weight
        return max(-1.0, min(1.0, score))

    @staticmethod
    def compute_risk_signal(headlines: list) -> dict:
        """
        Aggregate sentiment across all headlines.
        Returns risk level, average score, dominant theme, and headline count.
        """
        if not headlines or headlines[0].get("source") == "System":
            return {
                "average_score":  0.0,
                "risk_level":     "Unknown",
                "dominant_theme": "Data unavailable",
                "headline_count": 0,
            }

        scores = []
        theme_counts = {
            "Geopolitical Conflict": 0,
            "Economic Stress":       0,
            "Trade & Sanctions":     0,
            "Market Volatility":     0,
        }

        conflict_kw  = {"war", "conflict", "attack", "missile", "invasion", "coup", "terror", "nuclear"}
        economic_kw  = {"recession", "inflation", "debt", "deficit", "default", "collapse", "crisis"}
        trade_kw     = {"tariff", "sanction", "ban", "blockade", "trade", "deal"}
        market_kw    = {"crash", "downgrade", "rally", "stock", "market", "risk"}

        for h in headlines:
            text = h.get("title", "").lower()
            scores.append(GeoCollector.score_headline_sentiment(text))
            if any(kw in text for kw in conflict_kw):
                theme_counts["Geopolitical Conflict"] += 1
            if any(kw in text for kw in economic_kw):
                theme_counts["Economic Stress"] += 1
            if any(kw in text for kw in trade_kw):
                theme_counts["Trade & Sanctions"] += 1
            if any(kw in text for kw in market_kw):
                theme_counts["Market Volatility"] += 1

        avg = sum(scores) / len(scores) if scores else 0.0

        if avg > -0.1:
            level = "Low"
        elif avg > -0.3:
            level = "Medium"
        elif avg > -0.6:
            level = "High"
        else:
            level = "Severe"

        dominant = max(theme_counts, key=theme_counts.get)
        if theme_counts[dominant] == 0:
            dominant = "General News"

        return {
            "average_score":  round(avg, 3),
            "risk_level":     level,
            "dominant_theme": dominant,
            "headline_count": len(scores),
        }

    # ------------------------------------------------------------------
    # Market / macro data via yfinance
    # ------------------------------------------------------------------

    @staticmethod
    @st.cache_data(ttl=1800)
    def fetch_macro_etf_data(period: str = "3mo") -> pd.DataFrame:
        """
        Batch-download macro ETF close prices.
        Returns a DataFrame of % returns for 1W, 1M, 3M windows.
        """
        tickers = list(GeoCollector.MACRO_TICKERS.values())
        try:
            raw = yf.download(tickers, period=period, progress=False, auto_adjust=True)
            if raw.empty:
                return pd.DataFrame()

            closes = raw["Close"] if "Close" in raw else raw
            closes = closes.dropna(how="all")

            results = {}
            for label, ticker in GeoCollector.MACRO_TICKERS.items():
                if ticker not in closes.columns:
                    continue
                col = closes[ticker].dropna()
                if len(col) < 2:
                    continue
                ret_1w = (col.iloc[-1] / col.iloc[max(-6, -len(col))] - 1) * 100
                ret_1m = (col.iloc[-1] / col.iloc[max(-22, -len(col))] - 1) * 100
                ret_3m = (col.iloc[-1] / col.iloc[0] - 1) * 100
                results[label] = {
                    "1W (%)": round(float(ret_1w), 2),
                    "1M (%)": round(float(ret_1m), 2),
                    "3M (%)": round(float(ret_3m), 2),
                }

            return pd.DataFrame(results).T
        except Exception:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=1800)
    def fetch_vix_history(period: str = "6mo") -> pd.DataFrame:
        """Download VIX time-series for trend chart."""
        try:
            vix = yf.download("^VIX", period=period, progress=False, auto_adjust=True)
            if vix.empty:
                return pd.DataFrame()
            return vix[["Close"]].rename(columns={"Close": "VIX"})
        except Exception:
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # World Bank API (free, no key)
    # ------------------------------------------------------------------

    @staticmethod
    @st.cache_data(ttl=86400)
    def fetch_worldbank_indicator(country_code: str, indicator: str, years: int = 6) -> pd.DataFrame:
        """
        Fetch a World Bank indicator for a given country.
        Returns a DataFrame with columns [year, value].
        """
        url = (
            f"https://api.worldbank.org/v2/country/{country_code}"
            f"/indicator/{indicator}?format=json&mrv={years}"
        )
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if len(data) < 2 or not data[1]:
                return pd.DataFrame()
            records = [
                {"year": item["date"], "value": item["value"]}
                for item in data[1]
                if item["value"] is not None
            ]
            df = pd.DataFrame(records).sort_values("year")
            df["value"] = df["value"].round(2)
            return df
        except Exception:
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Stock Impact Propagation (geopolitical ripple effect)
    # ------------------------------------------------------------------

    @staticmethod
    @st.cache_data(ttl=1800)
    def fetch_stock_impact_data(trigger_ticker: str, period: str = "3mo") -> dict:
        """
        Given a trigger stock (e.g. INFY), fetch price history for it and
        all its sector peers. Returns dict with:
          - trigger_ticker, sector, peers_data (DataFrame of normalised prices),
            returns_df (% return for each name)
        """
        peer_info = SECTOR_PEERS.get(trigger_ticker.upper(), None)
        if peer_info is None:
            # Best-effort: just return the trigger alone
            peer_info = {"sector": "Unknown", "peers": []}

        sector = peer_info["sector"]
        all_tickers = [trigger_ticker] + peer_info["peers"]

        try:
            raw = yf.download(all_tickers, period=period, progress=False, auto_adjust=True)
            if raw.empty:
                return {"error": "No data returned from yfinance."}

            closes = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw
            closes = closes.dropna(how="all")

            # If only one ticker, yfinance returns a Series — wrap it
            if isinstance(closes, pd.Series):
                closes = closes.to_frame(name=trigger_ticker)

            # Normalise to 100 at start for visual comparison
            normed = (closes / closes.iloc[0]) * 100

            # % returns
            returns = {}
            for col in closes.columns:
                col_data = closes[col].dropna()
                if len(col_data) >= 2:
                    ret = round((float(col_data.iloc[-1]) / float(col_data.iloc[0]) - 1) * 100, 2)
                    returns[col] = ret

            return {
                "trigger":      trigger_ticker,
                "sector":       sector,
                "normed_df":    normed,
                "returns":      returns,
                "peer_tickers": peer_info["peers"],
            }
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # AI Summary (logic-based, no external LLM needed)
    # ------------------------------------------------------------------

    @staticmethod
    def generate_ai_summary(risk_signal: dict, etf_df: pd.DataFrame) -> str:
        """
        Generates a readable market risk summary based on sentiment signal
        and ETF performance. Uses rule-based logic — no external AI API needed.
        """
        level = risk_signal.get("risk_level", "Unknown")
        theme = risk_signal.get("dominant_theme", "General News")
        score = risk_signal.get("average_score", 0.0)
        count = risk_signal.get("headline_count", 0)

        vix_note = ""
        if not etf_df.empty and "VIX (Fear)" in etf_df.index:
            vix_1m = etf_df.loc["VIX (Fear)", "1M (%)"]
            if vix_1m > 15:
                vix_note = " The VIX fear index has surged over the past month, signaling heightened market uncertainty."
            elif vix_1m < -10:
                vix_note = " The VIX fear index has declined recently, suggesting markets are calmer."

        gold_note = ""
        if not etf_df.empty and "Gold (GLD)" in etf_df.index:
            gold_1m = etf_df.loc["Gold (GLD)", "1M (%)"]
            if gold_1m > 5:
                gold_note = " Gold is rallying — a classic safe-haven signal investors use during uncertainty."
            elif gold_1m < -5:
                gold_note = " Gold has declined, which often indicates reduced safe-haven demand."

        if level == "Low":
            summary = (
                f"Global news sentiment appears relatively stable based on {count} headlines analyzed. "
                f"The dominant theme is **{theme}**, with an overall sentiment score of {score:.2f}. "
                f"Markets are likely trading on fundamentals with limited geopolitical disruption expected."
            )
        elif level == "Medium":
            summary = (
                f"There is a moderate level of concern in global news ({count} headlines analyzed). "
                f"**{theme}** is the dominant theme driving negative sentiment (score: {score:.2f}). "
                f"Investors should watch key indicators closely — some sectors may face short-term pressure."
            )
        elif level == "High":
            summary = (
                f"Global risk signals are elevated. {count} headlines show significant negative sentiment "
                f"around **{theme}** (score: {score:.2f}). "
                f"Defensive sectors (Gold, Energy) and volatility hedges may outperform. "
                f"Portfolio risk management becomes critical in this environment."
            )
        else:  # Severe or Unknown
            summary = (
                f"Severe geopolitical or economic stress detected across {count} news headlines. "
                f"**{theme}** dominates the risk landscape (sentiment score: {score:.2f}). "
                f"Historical data suggests significant market volatility is likely. "
                f"Consider stress-testing your portfolio against tail-risk scenarios."
            )

        return summary + vix_note + gold_note
