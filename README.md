# 🦈 RiskForge — Portfolio Risk & Market Intelligence

> A Streamlit web app for portfolio risk assessment, stock price prediction (LSTM), geopolitical market intelligence, and sector impact analysis.

---

## What does it do?

| Feature | Description |
|---|---|
| **Analyse Portfolio** | Build a multi-stock portfolio, run Monte Carlo simulations, compute VaR & CVaR |
| **Analyse Single Stock** | LSTM price prediction (15-day), technical signals (RSI, MACD, Bollinger), risk score |
| **Global Risk Intel** | Live geopolitical news, VIX fear index, macro ETF heatmap, World Bank data |
| **Stock Impact Propagation** | See how a geopolitical event affecting one stock (e.g. Infosys) ripples through its sector peers |
| **Market Preview** | Live candlestick charts and sector tables for Indian & U.S. markets |

---

## Fresh Setup — Step by Step (no coding experience needed)

Follow every step in order. Each step has a ✅ to confirm it worked before moving on.

---

### Step 1 — Install Python

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.11.x"** button (use 3.11, not 3.12+ to avoid compatibility issues)
3. Run the downloaded installer
4. **IMPORTANT:** On the first screen, tick the box that says **"Add Python to PATH"** before clicking Install
5. Click **Install Now** and wait for it to finish

✅ **Check:** Open a terminal (search "Command Prompt" on Windows) and type:
```
python --version
```
You should see something like `Python 3.11.9`. If you see an error, restart your computer and try again.

---

### Step 2 — Download this project

**Option A — If you have Git installed:**
```
git clone https://github.com/Renukaprasadbs454/mini-project-RF.git
cd mini-project-RF
```

**Option B — Download as ZIP (no Git needed):**
1. Go to the GitHub page for this project
2. Click the green **"Code"** button → **"Download ZIP"**
3. Extract (unzip) the downloaded file somewhere easy to find, like your Desktop
4. Open that folder

✅ **Check:** You should see files like `main_page.py`, `requirements.txt`, `run_project.bat` inside the folder.

---

### Step 3 — Open a terminal inside the project folder

**Windows:**
1. Open the project folder in File Explorer
2. Click the address bar at the top (where it shows the folder path)
3. Type `cmd` and press Enter — a black terminal window opens inside the folder

**Mac / Linux:**
1. Open Terminal
2. Type `cd ` (with a space), then drag the project folder into the terminal window and press Enter

✅ **Check:** The terminal prompt should show the project folder name, something like `C:\Users\YourName\Desktop\mini-project-RF>`

---

### Step 4 — Create a virtual environment

A virtual environment keeps this project's packages separate from anything else on your computer.

```
python -m venv venv
```

Wait a few seconds. You will see a new folder called `venv` appear in the project.

✅ **Check:** Type `dir venv` (Windows) or `ls venv` (Mac/Linux). You should see folders like `Scripts` or `bin`.

---

### Step 5 — Activate the virtual environment

**Windows:**
```
venv\Scripts\activate
```

**Mac / Linux:**
```
source venv/bin/activate
```

✅ **Check:** Your terminal prompt should now start with `(venv)` — like `(venv) C:\...\mini-project-RF>`. This means the virtual environment is active.

> Every time you close the terminal and come back, you need to repeat Step 5 before running the app.

---

### Step 6 — Install dependencies

```
pip install -r requirements.txt
```

This downloads all the required packages. It will take 2–5 minutes depending on your internet speed. You will see a lot of text scrolling — that is normal.

✅ **Check:** When it finishes, the last line should say something like `Successfully installed ...`. If you see a red error, see the Troubleshooting section below.

---

### Step 7 — Run the app

```
streamlit run main_page.py
```

✅ **Check:** Your browser should automatically open to `http://localhost:8501` and show the RiskForge app. If it doesn't open automatically, copy that address and paste it into your browser.

---

### Quick-start for next time (Windows)

After the first setup, you can just double-click **`run_project.bat`** in the project folder — it activates the virtual environment and launches the app automatically.

---

## How to use the app

### Homepage — Market Preview
When the app opens you will see two big cards:

- **ANALYSE PORTFOLIO** — click this if you want to build a basket of stocks and assess the combined risk
- **ANALYSE SINGLE STOCK** — click this to predict prices and get a risk score for one specific stock

Below the cards is a live **Market Preview** showing Nifty 50 / Sensex / Bank Nifty (or Dow Jones / NASDAQ / S&P 500 for U.S. markets).

### Building a Portfolio
1. In the left sidebar, click the **📈 Create Portfolio** tab
2. Choose a **Sector** (Technology, Finance, Consumer)
3. Select your stocks from the dropdown (up to 10)
4. Expand each stock to set the number of shares and purchase date
5. Click **Load Portfolio** — the main area shows your portfolio details
6. Switch to the **Build Risk Model** tab, set your parameters, and click **Run Simulation** to see VaR, CVaR, and Monte Carlo paths

### Single Stock Analysis
1. In the left sidebar, click the **Prediction** tab
2. Choose a sector, then pick a stock from the dropdown
3. Click **▶ TRAIN MODEL AND PREDICT**
4. The main area switches to show:
   - Current price snapshot (52-week high/low, volatility)
   - 2-year price history with SMA overlays
   - LSTM 15-day forecast with confidence bands
   - Technical signals (RSI, MACD, Bollinger, SMA)
   - Risk score meter (0–100)

### Global Risk Intelligence
1. In the sidebar, click the **🌍 Global Risk Intel** tab
2. Choose news sources, countries, and a time window
3. Click **Analyze Global Risk**
4. Scroll down to **Stock Impact Propagation Analyzer** — select any stock (e.g. INFY) and click **▶ ANALYZE IMPACT** to see how that stock's movement ripples through its sector peers

---

## Troubleshooting

### `pip install` fails with an encoding error
Run this first, then retry Step 6:
```
python fix_requirements_encoding.py
pip install -r requirements.txt
```

### `streamlit: command not found`
Make sure the virtual environment is activated (Step 5). The `(venv)` prefix must appear in your terminal.

### The browser opens but shows a blank page
Wait 10–15 seconds and refresh. The app loads data from the internet on first run.

### `torch` takes very long to install
PyTorch is a large package (~700 MB). This is normal — just let it finish.

### Port 8501 already in use
Another instance of the app is already running. Either close it or run on a different port:
```
streamlit run main_page.py --server.port 8502
```

### yfinance returns no data for Indian stocks
Indian stock tickers need the `.NS` suffix (NSE) or `.BO` suffix (BSE). Examples: `INFY.NS`, `TCS.NS`, `RELIANCE.NS`.

---

## Project structure

```
mini-project-RF/
├── main_page.py                  # App entry point & routing
├── default_page.py               # Home / market preview
├── portfolio_page.py             # Portfolio view
├── model_page.py                 # Monte Carlo / risk model
├── single_stock_page.py          # Single stock deep analysis
├── geopolitical_page.py          # Global risk intelligence
├── geopolitical_page_components.py
├── side_bar.py                   # Sidebar tabs & controls
├── side_bar_components.py        # Portfolio / prediction widgets
├── stTools.py                    # Shared utilities & CSS
├── assets/
│   ├── GeoCollector.py           # News, macro, VIX, World Bank data
│   ├── Collector.py              # yfinance wrapper
│   ├── Portfolio.py
│   └── Stock.py
├── models/
│   ├── MonteCarloSimulator.py
│   └── train_model.py
├── .streamlit/
│   └── config.toml               # Theme & server config (light mode)
├── requirements.txt
└── run_project.bat               # Windows one-click launcher
```

---

## Requirements

Python **3.10 or 3.11** recommended (3.12+ may have minor compatibility issues with some packages).

| Package | Version |
|---|---|
| streamlit | ≥ 1.49.0 |
| yfinance | ≥ 0.2.66 |
| pandas | ≥ 2.0.0 |
| numpy | ≥ 1.24.0 |
| plotly | ≥ 5.0.0 |
| scikit-learn | ≥ 1.3.0 |
| torch | ≥ 2.0.0 |
| feedparser | ≥ 6.0.0 |
| requests | ≥ 2.28.0 |
| streamlit-extras | 0.5.0 – 0.6.x |

All of the above are installed automatically via `pip install -r requirements.txt`.

---

## Data sources

All data is fetched live from free public sources — no API keys required.

| Source | What it provides |
|---|---|
| Yahoo Finance (`yfinance`) | Stock prices, indices, VIX |
| RSS feeds (BBC, Reuters, Al Jazeera) | Geopolitical news headlines |
| World Bank API | GDP growth, inflation by country |

---

*Built with Python · Streamlit · PyTorch · Plotly*
