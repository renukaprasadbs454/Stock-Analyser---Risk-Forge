import streamlit as st
import side_bar as comp
import stTools as tools
import default_page
import portfolio_page
import model_page
import geopolitical_page
import single_stock_page

st.set_page_config(
    page_title="RiskForge",
    page_icon="🦈",
    layout="wide",
)

tools.remove_white_space()

st.markdown(
    """
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding: 14px 0 14px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    ">
        <div style="display:flex; align-items:center; gap:14px;">
            <span style="font-size:34px; line-height:1;">🦈</span>
            <div>
                <div style="
                    font-family:'Space Mono',monospace;
                    font-size:22px; font-weight:700;
                    letter-spacing:2px; color:#0f172a; line-height:1;
                ">RISK<span style="color:#0891b2">FORGE</span></div>
                <div style="font-size:12px; color:#94a3b8; letter-spacing:1px; margin-top:3px; font-family:'Space Mono',monospace;">
                    PORTFOLIO RISK &amp; MARKET INTELLIGENCE
                </div>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:8px;height:8px;border-radius:50%;background:#059669;
                        box-shadow:0 0 0 3px rgba(5,150,105,.2);"></div>
            <span style="font-family:'Space Mono',monospace;font-size:11px;color:#94a3b8;letter-spacing:1px;">LIVE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

comp.load_sidebar()

if "load_portfolio_check" not in st.session_state:
    st.session_state["load_portfolio_check"] = False

if "run_simulation_check" not in st.session_state:
    st.session_state["run_simulation_check"] = False

if "load_geo_check" not in st.session_state:
    st.session_state["load_geo_check"] = False

if "analyse_single_stock" not in st.session_state:
    st.session_state["analyse_single_stock"] = False

if st.session_state.get("load_geo_check", False):
    geopolitical_page.load_page()

elif st.session_state.get("analyse_single_stock", False):
    single_stock_page.load_page()

elif not st.session_state.load_portfolio_check:
    default_page.load_page()

elif not st.session_state.run_simulation_check and st.session_state.load_portfolio_check:
    portfolio_page.load_page()

elif st.session_state.run_simulation_check:
    model_page.load_page()