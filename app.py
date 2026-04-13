import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from itertools import combinations
from PIL import Image

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
logo = Image.open("let_it_grow_logo.png")

st.set_page_config(
    page_title="Let It Grow",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# SESSION STATE NAVIGATION
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()

# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>
    .stApp, .stApp > header, .main, .block-container {
        background: linear-gradient(180deg, #f4f9ff 0%, #eef6fb 55%, #eef8f1 100%) !important;
    }

    body, .stApp, .stMarkdown, .stMarkdown *, div, p, h1, h2, h3, h4, h5, h6, span, li,
    .stText, .stMetric, .stMetric label, .stMetric div {
        color: #17324d !important;
    }

    .main-title {
        font-size: 3.35rem;
        font-weight: 900;
        margin-bottom: 0.15rem;
        letter-spacing: 0.4px;
        font-family: Georgia, "Times New Roman", serif;
    }

    .main-title-blue {
        color: #0b5cad !important;
        text-shadow: 0 2px 0 rgba(255,255,255,0.55);
    }

    .main-title-green {
        color: #2f8f3a !important;
        text-shadow:
            0 0 8px rgba(47, 143, 58, 0.28),
            0 0 18px rgba(107, 184, 255, 0.18),
            0 2px 0 rgba(255,255,255,0.45);
    }

    .subtitle {
        font-size: 1.08rem;
        color: #2f6b3b !important;
        margin-bottom: 1.2rem;
    }

    .page-panel {
        background: rgba(255,255,255,0.78);
        border: 1px solid #d7e4f2;
        border-radius: 18px;
        padding: 18px 22px;
        box-shadow: 0 6px 18px rgba(11, 92, 173, 0.06);
        margin-bottom: 18px;
        backdrop-filter: blur(4px);
    }

    .home-card {
        background-color: white !important;
        border: 1px solid #d7e4f2 !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        box-shadow: 0 6px 18px rgba(11, 92, 173, 0.08) !important;
        min-height: 250px;
    }

    .home-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .home-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0b5cad !important;
        margin-bottom: 0.45rem;
    }

    .home-text {
        color: #48637d !important;
        font-size: 0.96rem;
        min-height: 90px;
    }

    .soft-rule {
        height: 1px;
        background: linear-gradient(90deg, rgba(11,92,173,0.0), rgba(11,92,173,0.28), rgba(11,92,173,0.0));
        margin: 0.6rem 0 1.1rem 0;
        border: none;
    }

    .stButton > button {
        background: linear-gradient(90deg, #0b5cad, #2f8f3a) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.72rem 1rem !important;
        width: 100% !important;
    }

    .stButton > button *,
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: white !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #094b8d, #26752f) !important;
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(255,255,255,0.95) !important;
        border: 1px solid #d7e4f2 !important;
        border-radius: 14px !important;
        padding: 14px !important;
        box-shadow: 0 4px 12px rgba(11, 92, 173, 0.06) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    textarea {
        background-color: rgba(255,255,255,0.98) !important;
        border: 1px solid #d7e4f2 !important;
        border-radius: 10px !important;
        color: #17324d !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 16px;
        background-color: #edf4fb;
        color: #4b6580 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0b5cad !important;
        color: white !important;
    }

    .streamlit-expanderHeader,
    .streamlit-expanderContent {
        background-color: rgba(255,255,255,0.92) !important;
        color: #17324d !important;
        border: 1px solid #d7e4f2 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="notification"] {
        background: #eef6ff !important;
        border: 1px solid #bfd8f5 !important;
        border-radius: 14px !important;
    }

    /* Slider styling */
    .stSlider [data-baseweb="slider"] > div {
        background: transparent !important;
    }

    .stSlider [data-baseweb="slider"] > div > div,
    .stSlider [data-baseweb="slider"] > div > div > div {
        background: #2f8f3a !important;
    }

    .stSlider [role="slider"] {
        background: #2f8f3a !important;
        border: 2px solid #2f8f3a !important;
        box-shadow: none !important;
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    .stSlider [data-testid="stThumbValue"] {
        color: #17324d !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider [data-testid="stTickBarMin"] *,
    .stSlider [data-testid="stTickBarMax"] * {
        color: #17324d !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        text-shadow: none !important;
        -webkit-text-fill-color: #17324d !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    .stSlider p,
    .stSlider span,
    .stSlider label,
    .stSlider small,
    .stSlider div {
        color: #17324d !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    .stSlider *::selection,
    .stSlider [data-testid="stTickBarMin"]::selection,
    .stSlider [data-testid="stTickBarMax"]::selection,
    .stSlider [data-testid="stTickBarMin"] *::selection,
    .stSlider [data-testid="stTickBarMax"] *::selection {
        background: transparent !important;
        color: #17324d !important;
    }

    .stSlider *::-moz-selection,
    .stSlider [data-testid="stTickBarMin"]::-moz-selection,
    .stSlider [data-testid="stTickBarMax"]::-moz-selection,
    .stSlider [data-testid="stTickBarMin"] *::-moz-selection,
    .stSlider [data-testid="stTickBarMax"] *::-moz-selection {
        background: transparent !important;
        color: #17324d !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():
    prices = pd.read_csv("SP500_Prices.csv")
    esg = pd.read_csv("ESG Values.csv")

    prices.columns = [c.strip() for c in prices.columns]
    esg.columns = [c.strip() for c in esg.columns]

    prices["date"] = pd.to_datetime(prices["date"])
    prices["ticker"] = prices["ticker"].astype(str).str.strip()

    esg = esg.rename(columns={
        "Ticker": "ticker",
        "Environmental": "environmental",
        "Governance": "governance",
        "Social": "social",
        "ESG Score": "esg_score",
        "Environmental Weight": "environmental_weight",
        "Social weight": "social_weight",
        "Governance Weight": "governance_weight",
        "Name": "name"
    })
    esg["ticker"] = esg["ticker"].astype(str).str.strip()

    if "name" in prices.columns:
        prices["name"] = prices["name"].astype(str).str.strip()
        price_name_map = prices[["ticker", "name"]].dropna().drop_duplicates()
    else:
        price_name_map = pd.DataFrame(columns=["ticker", "name"])

    if "name" in esg.columns:
        esg["name"] = esg["name"].astype(str).str.strip()
        esg_name_map = esg[["ticker", "name"]].dropna().drop_duplicates()
    else:
        esg_name_map = pd.DataFrame(columns=["ticker", "name"])

    name_map = pd.concat([price_name_map, esg_name_map], ignore_index=True)
    if not name_map.empty:
        name_map = name_map.dropna(subset=["ticker"]).drop_duplicates(subset=["ticker"], keep="first")
    else:
        name_map = pd.DataFrame({"ticker": prices["ticker"].drop_duplicates()})
        name_map["name"] = name_map["ticker"]

    all_tickers = pd.DataFrame({"ticker": pd.concat([prices["ticker"], esg["ticker"]]).drop_duplicates()})
    name_map = all_tickers.merge(name_map, on="ticker", how="left")
    name_map["name"] = name_map["name"].fillna(name_map["ticker"])

    prices = prices.drop(columns=["name"], errors="ignore").merge(name_map, on="ticker", how="left")
    esg = esg.drop(columns=["name"], errors="ignore").merge(name_map, on="ticker", how="left")

    for col in ["environmental_weight", "social_weight", "governance_weight"]:
        if col not in esg.columns:
            esg[col] = 1 / 3

    esg = esg.dropna(subset=["ticker", "environmental", "social", "governance", "esg_score"])
    esg["esg_mean_score"] = esg["esg_score"] / 3

    return prices, esg, name_map

prices, esg, name_map = load_data()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def esg_rating(score):
    if score >= 8.6:
        return "AAA", "Leader"
    elif score >= 7.1:
        return "AA", "Leader"
    elif score >= 5.7:
        return "A", "Average"
    elif score >= 4.3:
        return "BBB", "Average"
    elif score >= 2.9:
        return "BB", "Laggard"
    elif score >= 1.4:
        return "B", "Laggard"
    else:
        return "CCC", "Laggard"

def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1**2 * sd1**2 +
        (1 - w1)**2 * sd2**2 +
        2 * rho * w1 * (1 - w1) * sd1 * sd2
    )

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def portfolio_utility(ret, risk, esg_score, gamma, lambda_esg):
    return ret + lambda_esg * (esg_score / 10) - 0.5 * gamma * (risk ** 2)

def build_label(df):
    return df["name"].fillna(df["ticker"]) + " (" + df["ticker"] + ")"

def get_asset_name(ticker):
    match = name_map.loc[name_map["ticker"] == ticker, "name"]
    return match.iloc[0] if len(match) else ticker

def compute_expected_return(price_series):
    if len(price_series) < 2:
        return np.nan
    returns = price_series.pct_change().dropna()
    if len(returns) == 0:
        return np.nan
    return returns.mean() * 12

@st.cache_data
def get_single_asset_summary_all(prices_df):
    summaries = []
    for ticker in prices_df["ticker"].drop_duplicates():
        df = prices_df[prices_df["ticker"] == ticker][["date", "price"]].sort_values("date").copy()
        if len(df) < 12:
            continue

        expected_return = compute_expected_return(df["price"].reset_index(drop=True))
        df["ret"] = df["price"].pct_change()
        df = df.dropna()

        if len(df) < 12 or pd.isna(expected_return):
            continue

        risk = df["ret"].std() * np.sqrt(12)

        summaries.append({
            "ticker": ticker,
            "expected_return": expected_return,
            "risk": risk
        })

    return pd.DataFrame(summaries)

def get_asset_stats(prices_df, ticker1, ticker2):
    raw1 = prices_df[prices_df["ticker"] == ticker1][["date", "price"]].sort_values("date").copy()
    raw2 = prices_df[prices_df["ticker"] == ticker2][["date", "price"]].sort_values("date").copy()

    if len(raw1) < 12 or len(raw2) < 12:
        return None

    r1 = compute_expected_return(raw1["price"].reset_index(drop=True))
    r2 = compute_expected_return(raw2["price"].reset_index(drop=True))

    df1 = raw1.rename(columns={"price": "price_1"})
    df2 = raw2.rename(columns={"price": "price_2"})

    merged = pd.merge(df1, df2, on="date", how="inner")
    merged["ret_1"] = merged["price_1"].pct_change()
    merged["ret_2"] = merged["price_2"].pct_change()
    merged = merged.dropna()

    if len(merged) < 12:
        return None

    sd1 = merged["ret_1"].std() * np.sqrt(12)
    sd2 = merged["ret_2"].std() * np.sqrt(12)
    rho = merged["ret_1"].corr(merged["ret_2"])

    return {
        "merged": merged,
        "r1": r1,
        "r2": r2,
        "sd1": sd1,
        "sd2": sd2,
        "rho": rho
    }

def optimize_two_asset_portfolio(r1, r2, sd1, sd2, rho, esg1, esg2, gamma, lambda_esg):
    weights = np.linspace(0, 1, 1001)

    returns = []
    risks = []
    esgs = []
    utilities = []

    for w in weights:
        ret = portfolio_ret(w, r1, r2)
        risk = portfolio_sd(w, sd1, sd2, rho)
        esg_val = portfolio_esg(w, esg1, esg2)
        utility = portfolio_utility(ret, risk, esg_val, gamma, lambda_esg)

        returns.append(ret)
        risks.append(risk)
        esgs.append(esg_val)
        utilities.append(utility)

    returns = np.array(returns)
    risks = np.array(risks)
    esgs = np.array(esgs)
    utilities = np.array(utilities)

    best_idx = np.argmax(utilities)

    return {
        "weights_grid": weights,
        "portfolio_returns": returns,
        "portfolio_risks": risks,
        "portfolio_esgs": esgs,
        "portfolio_utilities": utilities,
        "w1": weights[best_idx],
        "w2": 1 - weights[best_idx],
        "ret_opt": returns[best_idx],
        "risk_opt": risks[best_idx],
        "esg_opt": esgs[best_idx],
        "utility_opt": utilities[best_idx]
    }

def compute_tangency_portfolio(r1, r2, sd1, sd2, rho, r_free):
    weights = np.linspace(0, 1, 2001)

    best_sharpe = -np.inf
    best_w = 0.0
    best_ret = r_free
    best_sd = 0.0

    for w in weights:
        ret = portfolio_ret(w, r1, r2)
        sd = portfolio_sd(w, sd1, sd2, rho)

        if sd <= 1e-12:
            continue

        sharpe = (ret - r_free) / sd

        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_w = w
            best_ret = ret
            best_sd = sd

    return {
        "w1": best_w,
        "w2": 1 - best_w,
        "ret_tangency": best_ret,
        "sd_tangency": best_sd,
        "sharpe_tangency": best_sharpe if np.isfinite(best_sharpe) else 0.0
    }

def describe_investment_type(risk, esg_mean, sharpe, esg_focus):
    if risk < 0.18:
        risk_text = "relatively defensive"
    elif risk < 0.28:
        risk_text = "balanced"
    else:
        risk_text = "growth-oriented and higher-risk"

    if esg_focus == "Pure Financials Focus":
        esg_text = "with sustainability characteristics shown separately from the selection logic"
    else:
        if esg_mean >= 7.1:
            esg_text = "strong sustainability quality"
        elif esg_mean >= 4.3:
            esg_text = "moderate sustainability quality"
        else:
            esg_text = "weaker sustainability quality"

    if sharpe >= 0.8:
        efficiency_text = "efficient on a risk-adjusted basis"
    elif sharpe >= 0.3:
        efficiency_text = "reasonable on a risk-adjusted basis"
    else:
        efficiency_text = "less efficient on a risk-adjusted basis"

    return f"This portfolio is a {risk_text} investment {esg_text}, and it appears {efficiency_text}."

def get_esg_focus_weights(esg_focus):
    if esg_focus == "Balanced ESG":
        return 1/3, 1/3, 1/3, 0.75
    elif esg_focus == "Environmental":
        return 1.0, 0.0, 0.0, 1.00
    elif esg_focus == "Social":
        return 0.0, 1.0, 0.0, 1.00
    elif esg_focus == "Governance":
        return 0.0, 0.0, 1.0, 1.00
    else:
        return 1/3, 1/3, 1/3, 0.0

def add_preference_scores(esg_df, esg_focus):
    env_weight, soc_weight, gov_weight, lambda_esg = get_esg_focus_weights(esg_focus)
    out = esg_df.copy()

    if esg_focus == "Balanced ESG":
        out["preference_score"] = out["esg_mean_score"]
    elif esg_focus == "Environmental":
        out["preference_score"] = out["environmental"]
    elif esg_focus == "Social":
        out["preference_score"] = out["social"]
    elif esg_focus == "Governance":
        out["preference_score"] = out["governance"]
    else:
        out["preference_score"] = 0.0

    return out, lambda_esg

def plot_esg_pie(ax, row, title):
    labels = ["Environmental", "Social", "Governance"]
    values = [
        row["environmental_weight"],
        row["social_weight"],
        row["governance_weight"]
    ]
    total = sum(values)
    if total == 0:
        values = [1/3, 1/3, 1/3]
    else:
        values = [v / total for v in values]

    colors = ["#2f8f3a", "#0b5cad", "#6bb8ff"]
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90, colors=colors, textprops={"fontsize": 10})
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f2d68")

def build_recommendation_universe(esg_df, asset_summary, esg_focus):
    universe = esg_df.merge(asset_summary, on="ticker", how="inner").copy()
    universe = universe.replace([np.inf, -np.inf], np.nan)
    universe = universe.dropna(subset=["expected_return", "risk"])

    universe = universe[universe["expected_return"] <= 0.25].copy()

    if esg_focus in ["Environmental", "Social", "Governance", "Balanced ESG"]:
        universe = universe[universe["expected_return"] >= 0.10].copy()

    if universe.empty:
        return universe

    if esg_focus == "Environmental":
        universe["priority_score"] = universe["environmental"]
        universe = universe.sort_values(
            ["priority_score", "expected_return", "esg_mean_score", "risk"],
            ascending=[False, False, False, True]
        ).copy()

    elif esg_focus == "Social":
        universe["priority_score"] = universe["social"]
        universe = universe.sort_values(
            ["priority_score", "expected_return", "esg_mean_score", "risk"],
            ascending=[False, False, False, True]
        ).copy()

    elif esg_focus == "Governance":
        universe["priority_score"] = universe["governance"]
        universe = universe.sort_values(
            ["priority_score", "expected_return", "esg_mean_score", "risk"],
            ascending=[False, False, False, True]
        ).copy()

    elif esg_focus == "Balanced ESG":
        universe["priority_score"] = universe["esg_mean_score"]
        universe = universe.sort_values(
            ["priority_score", "expected_return", "risk"],
            ascending=[False, False, True]
        ).copy()

    else:
        universe["priority_score"] = universe["expected_return"]
        universe = universe.sort_values(
            ["priority_score", "risk"],
            ascending=[False, True]
        ).copy()

    return universe

def choose_recommended_pair(prices_df, universe, esg_focus, gamma, lambda_esg):
    if len(universe) < 2:
        return None

    top_n = min(18, len(universe))
    candidate_pool = universe.head(top_n).copy()

    pair_records = []

    for t1, t2 in combinations(candidate_pool["ticker"], 2):
        stats = get_asset_stats(prices_df, t1, t2)
        if stats is None:
            continue

        row1 = candidate_pool[candidate_pool["ticker"] == t1].iloc[0]
        row2 = candidate_pool[candidate_pool["ticker"] == t2].iloc[0]

        if esg_focus == "Pure Financials Focus":
            pref1 = 0.0
            pref2 = 0.0
        else:
            pref1 = float(row1["preference_score"])
            pref2 = float(row2["preference_score"])

        result = optimize_two_asset_portfolio(
            stats["r1"], stats["r2"],
            stats["sd1"], stats["sd2"],
            stats["rho"],
            pref1, pref2,
            gamma, lambda_esg
        )

        avg_priority = (float(row1["priority_score"]) + float(row2["priority_score"])) / 2
        avg_return = (float(row1["expected_return"]) + float(row2["expected_return"])) / 2
        diversification_bonus = -abs(stats["rho"])
        pair_risk = result["risk_opt"]

        if esg_focus == "Pure Financials Focus":
            final_score = (
                0.60 * avg_return
                - 0.18 * pair_risk
                + 0.12 * diversification_bonus
                + 0.10 * result["ret_opt"]
            )
        else:
            gamma_penalty = 0.03 * gamma * pair_risk
            final_score = (
                0.55 * (avg_priority / 10)
                + 0.20 * avg_return
                + 0.10 * result["ret_opt"]
                + 0.10 * diversification_bonus
                - gamma_penalty
            )

        pair_records.append({
            "ticker1": t1,
            "ticker2": t2,
            "stats": stats,
            "result": result,
            "row1": row1,
            "row2": row2,
            "final_score": final_score
        })

    if not pair_records:
        return None

    pairs_df = pd.DataFrame(pair_records)
    best_idx = pairs_df["final_score"].idxmax()
    best_row = pairs_df.loc[best_idx]

    return {
        "ticker1": best_row["ticker1"],
        "ticker2": best_row["ticker2"],
        "stats": best_row["stats"],
        "result": best_row["result"],
        "row1": best_row["row1"],
        "row2": best_row["row2"]
    }

def build_recommendation_reason(esg_focus, row1, row2):
    name1 = row1["name"]
    name2 = row2["name"]

    if esg_focus == "Environmental":
        return (
            f"These two stocks were chosen because they rank among the strongest candidates on "
            f"**Environmental score** while still keeping solid profitability. "
            f"{name1} has an environmental score of **{row1['environmental']:.2f}** and expected return of **{row1['expected_return']*100:.2f}%**, "
            f"while {name2} has an environmental score of **{row2['environmental']:.2f}** and expected return of **{row2['expected_return']*100:.2f}%**."
        )

    if esg_focus == "Social":
        return (
            f"These two stocks were chosen because they rank among the strongest candidates on "
            f"**Social score** while still keeping solid profitability. "
            f"{name1} has a social score of **{row1['social']:.2f}** and expected return of **{row1['expected_return']*100:.2f}%**, "
            f"while {name2} has a social score of **{row2['social']:.2f}** and expected return of **{row2['expected_return']*100:.2f}%**."
        )

    if esg_focus == "Governance":
        return (
            f"These two stocks were chosen because they rank among the strongest candidates on "
            f"**Governance score** while still keeping solid profitability. "
            f"{name1} has a governance score of **{row1['governance']:.2f}** and expected return of **{row1['expected_return']*100:.2f}%**, "
            f"while {name2} has a governance score of **{row2['governance']:.2f}** and expected return of **{row2['expected_return']*100:.2f}%**."
        )

    if esg_focus == "Balanced ESG":
        return (
            f"These two stocks were chosen because they rank among the strongest candidates on "
            f"**average ESG score** while still keeping solid profitability. "
            f"{name1} has an average ESG score of **{row1['esg_mean_score']:.2f}** and expected return of **{row1['expected_return']*100:.2f}%**, "
            f"while {name2} has an average ESG score of **{row2['esg_mean_score']:.2f}** and expected return of **{row2['expected_return']*100:.2f}%**."
        )

    return (
        f"These two stocks were chosen because they offered some of the **highest expected returns** available, "
        f"while still producing a strong recommended pair. "
        f"{name1} has an expected return of **{row1['expected_return']*100:.2f}%**, and "
        f"{name2} has an expected return of **{row2['expected_return']*100:.2f}%**."
    )

def render_back_button():
    left, right = st.columns([1.2, 6])
    with left:
        if st.button("⬅ Back to Home"):
            go_to("home")
    with right:
        st.markdown("<div class='soft-rule'></div>", unsafe_allow_html=True)

def render_brand_header(show_tagline=True):
    col1, col2 = st.columns([1.1, 5])
    with col1:
        st.image(logo, width=120)
    with col2:
        st.markdown(
            """
            <div class="main-title">
                <span class="main-title-blue">Let It </span>
                <span class="main-title-green">Grow</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if show_tagline:
            st.markdown(
                '<div class="subtitle">Grow your wealth with purpose through sustainable portfolio design.</div>',
                unsafe_allow_html=True
            )

def render_outputs(
    ticker1, ticker2, stats, result, r_free, esg_focus,
    esg_row_1, esg_row_2, name1, name2,
    rating1, rating2, level1, level2,
    recommendation_reason=None
):
    # True portfolio ESG rating must always be based on the stocks' actual average ESG scores
    portfolio_esg_mean = (
        result["w1"] * float(esg_row_1["esg_mean_score"]) +
        result["w2"] * float(esg_row_2["esg_mean_score"])
    )
    portfolio_rating, portfolio_level = esg_rating(float(portfolio_esg_mean))

    if result["risk_opt"] > 0:
        sharpe_ratio = (result["ret_opt"] - r_free) / result["risk_opt"]
    else:
        sharpe_ratio = 0

    tangency = compute_tangency_portfolio(
        stats["r1"], stats["r2"],
        stats["sd1"], stats["sd2"],
        stats["rho"], r_free
    )
    ret_tangency = tangency["ret_tangency"]
    sd_tangency = tangency["sd_tangency"]

    investment_description = describe_investment_type(result["risk_opt"], portfolio_esg_mean, sharpe_ratio, esg_focus)

    summary_text = (
        f"The optimized portfolio allocates {result['w1']*100:.2f}% to {name1} and "
        f"{result['w2']*100:.2f}% to {name2}. "
        f"It has an expected annual return of {result['ret_opt']*100:.2f}% and annual risk of {result['risk_opt']*100:.2f}%. "
        f"Based on the true weighted average ESG score, the portfolio receives a rating of {portfolio_rating} ({portfolio_level})."
    )

    tab1, tab2, tab3 = st.tabs(["📊 Portfolio Results", "📈 Visualisation", "🏢 ESG Overview"])

    with tab1:
        st.info(summary_text)

        if recommendation_reason:
            st.markdown("### Why these stocks were chosen")
            st.write(recommendation_reason)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Return", f"{result['ret_opt']*100:.2f}%")
        col2.metric("Risk (Std Dev)", f"{result['risk_opt']*100:.2f}%")
        col3.metric("Sharpe Ratio", f"{sharpe_ratio:.3f}")
        col4.metric("Portfolio ESG Rating", f"{portfolio_rating} ({portfolio_level})")

        st.markdown("### Interpretation")
        st.write(investment_description)

        st.markdown("### Optimized Portfolio Composition")
        weights_df = pd.DataFrame({
            "Asset": [name1, name2],
            "Ticker": [ticker1, ticker2],
            "Weight (%)": [result["w1"] * 100, result["w2"] * 100],
            "Expected Return (%)": [stats["r1"] * 100, stats["r2"] * 100],
            "Risk (%)": [stats["sd1"] * 100, stats["sd2"] * 100],
            "Average ESG Score": [esg_row_1["esg_mean_score"], esg_row_2["esg_mean_score"]],
            "ESG Rating": [rating1, rating2]
        }).round(2)
        st.dataframe(weights_df, use_container_width=True)

        st.write(
            "This table shows how much of the final portfolio is allocated to each stock, "
            "together with each stock’s expected annual return estimate, annualized volatility, and sustainability rating."
        )

        st.markdown("### What the Asset Statistics Mean")
        st.write(
            f"**{name1}** has an estimated annual return of **{stats['r1']*100:.2f}%**, based on the historical average monthly return, "
            f"and annual volatility of **{stats['sd1']*100:.2f}%**. Its ESG profile translates into a **{rating1} ({level1})** rating."
        )
        st.write(
            f"**{name2}** has an estimated annual return of **{stats['r2']*100:.2f}%**, based on the historical average monthly return, "
            f"and annual volatility of **{stats['sd2']*100:.2f}%**. Its ESG profile translates into a **{rating2} ({level2})** rating."
        )
        st.write(
            f"The correlation between the two assets is **{stats['rho']:.2f}**, which measures how similarly they move over time. "
            f"Lower correlation generally means better diversification benefits."
        )

    with tab2:
        st.markdown("### Risk-Return Frontier")

        weights_plot = np.linspace(0, 1, 400)
        returns_all = np.array([portfolio_ret(w, stats["r1"], stats["r2"]) for w in weights_plot])
        risks_all = np.array([portfolio_sd(w, stats["sd1"], stats["sd2"], stats["rho"]) for w in weights_plot])

        # Keep only the clean efficient upper branch
        min_var_idx = np.argmin(risks_all)
        min_var_ret = returns_all[min_var_idx]
        efficient_mask = returns_all >= (min_var_ret - 1e-12)

        frontier_risks = risks_all[efficient_mask]
        frontier_returns = returns_all[efficient_mask]

        order = np.argsort(frontier_risks)
        frontier_risks = frontier_risks[order]
        frontier_returns = frontier_returns[order]

        unique_sd, unique_idx = np.unique(np.round(frontier_risks, 8), return_index=True)
        frontier_risks = frontier_risks[unique_idx]
        frontier_returns = frontier_returns[unique_idx]

        sd_max = max(
            np.max(frontier_risks),
            stats["sd1"],
            stats["sd2"],
            result["risk_opt"],
            sd_tangency
        ) * 1.18

        sd_cml = np.linspace(0, sd_max, 200)
        if sd_tangency > 0:
            ret_cml = r_free + ((ret_tangency - r_free) / sd_tangency) * sd_cml
        else:
            ret_cml = np.ones_like(sd_cml) * r_free

        x_min = 0
        x_max = sd_max
        y_candidates = [
            np.min(frontier_returns),
            stats["r1"],
            stats["r2"],
            result["ret_opt"],
            ret_tangency,
            r_free
        ]
        y_min = min(y_candidates) - 0.03
        y_max = max(max(y_candidates), np.max(ret_cml)) + 0.03

        fig, ax = plt.subplots(figsize=(10.4, 6.4), dpi=170)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#fbfdff")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#0f2d68")
        ax.spines["bottom"].set_color("#0f2d68")
        ax.spines["left"].set_linewidth(1.6)
        ax.spines["bottom"].set_linewidth(1.6)

        ax.grid(True, color="#c7d2e4", alpha=0.55, linewidth=0.8)

        frontier_handle, = ax.plot(
            frontier_risks,
            frontier_returns,
            color="#4e9f58",
            linewidth=4.2,
            solid_capstyle="round",
            label="Efficient Frontier",
            zorder=2
        )

        cml_handle, = ax.plot(
            sd_cml,
            ret_cml,
            linestyle="--",
            color="#0b5cad",
            linewidth=2.7,
            label="Capital Market Line",
            zorder=1
        )

        asset1_handle = ax.scatter(
            stats["sd1"], stats["r1"],
            s=230, color="#1f66c2", edgecolor="#184d93", linewidth=1.2,
            label=name1, zorder=5
        )

        asset2_handle = ax.scatter(
            stats["sd2"], stats["r2"],
            s=230, color="#66a84f", edgecolor="#4c7e3b", linewidth=1.2,
            label=name2, zorder=5
        )

        tangency_handle = ax.scatter(
            sd_tangency, ret_tangency,
            s=520, color="#2f8f3a", edgecolor="#246d2d", linewidth=1.0,
            marker="*", label="Tangency Portfolio", zorder=6
        )

        optimal_handle = ax.scatter(
            result["risk_opt"], result["ret_opt"],
            s=230, color="#ffb84d", edgecolor="#d08c24", linewidth=1.2,
            marker="D", label="Your Optimal Portfolio", zorder=7
        )

        rf_handle = ax.scatter(
            0, r_free,
            s=170, color="#6bb8ff", edgecolor="#3d8ed8", linewidth=1.1,
            marker="s", label="Risk-Free Asset", zorder=6
        )

        ax.set_title("Risk-Return Frontier", fontsize=24, color="#0f2d68", fontweight="bold", pad=16)
        ax.set_xlabel("Risk (Standard Deviation)", fontsize=17, color="#0f2d68", labelpad=12)
        ax.set_ylabel("Expected Return", fontsize=17, color="#0f2d68", labelpad=14)

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
        ax.tick_params(axis="both", labelsize=13, colors="#0f2d68", width=1.2, length=5)

        legend = ax.legend(
            handles=[
                asset1_handle, asset2_handle, optimal_handle,
                tangency_handle, rf_handle, frontier_handle, cml_handle
            ],
            labels=[
                name1, name2, "Your Optimal Portfolio",
                "Tangency Portfolio", "Risk-Free Asset",
                "Efficient Frontier", "Capital Market Line"
            ],
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            borderaxespad=0.0,
            frameon=True,
            facecolor="white",
            edgecolor="#b9c8df",
            fontsize=9,
            borderpad=0.6,
            labelspacing=0.45,
            handlelength=1.8,
            handletextpad=0.5,
            markerscale=0.9
        )

        for text in legend.get_texts():
            txt = text.get_text()
            if txt == "Efficient Frontier":
                text.set_color("#4e9f58")
            elif txt == "Capital Market Line":
                text.set_color("#0b5cad")
            else:
                text.set_color("#0f2d68")

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        st.write(
            "The chart shows the two-asset efficient frontier, the Capital Market Line, the tangency portfolio, "
            "your utility-maximizing portfolio, and the risk-free asset."
        )

        st.markdown("### ESG Weight Composition of Each Stock")
        fig2, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=140)
        plot_esg_pie(axes[0], esg_row_1, f"{name1} ESG Weight Mix")
        plot_esg_pie(axes[1], esg_row_2, f"{name2} ESG Weight Mix")
        plt.tight_layout()
        st.pyplot(fig2)

        st.write(
            "These pie charts show how each stock’s ESG framework is distributed across Environmental, Social, and Governance factors."
        )

    with tab3:
        st.markdown("### ESG Overview")

        esg_display = pd.DataFrame({
            "Asset": [name1, name2],
            "Ticker": [ticker1, ticker2],
            "Environmental": [esg_row_1["environmental"], esg_row_2["environmental"]],
            "Social": [esg_row_1["social"], esg_row_2["social"]],
            "Governance": [esg_row_1["governance"], esg_row_2["governance"]],
            "Total ESG Score": [esg_row_1["esg_score"], esg_row_2["esg_score"]],
            "Average ESG Score": [esg_row_1["esg_mean_score"], esg_row_2["esg_mean_score"]],
            "ESG Rating": [rating1, rating2],
            "Category": [level1, level2]
        }).round(2)
        st.dataframe(esg_display, use_container_width=True)

        st.write("**How to read the rating scale**")
        st.write(
            "We convert the total ESG score into an average score by dividing by 3. "
            "That average score is then mapped to the sustainability scale: "
            "AAA = 8.6–10.0, AA = 7.1–8.5, A = 5.7–7.0, BBB = 4.3–5.6, BB = 2.9–4.2, B = 1.4–2.8, CCC = 0.0–1.3."
        )

        st.write(
            f"Using the portfolio weights, the final portfolio has a true weighted average ESG score of **{portfolio_esg_mean:.2f}**, "
            f"which corresponds to **{portfolio_rating} ({portfolio_level})**."
        )

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if st.session_state.page == "home":
    header_left, header_right = st.columns([1.5, 7])
    with header_left:
        st.image(logo, width=240)
    with header_right:
        st.markdown("")

    st.markdown("""
        <div style="text-align: center; padding: 0.2rem 0 1rem 0;">
            <div class="main-title">
                <span class="main-title-blue">Let It </span>
                <span class="main-title-green">Grow</span>
            </div>
            <div style="font-size: 1.15rem; color: #48637d; max-width: 760px; margin: 0 auto;">
                Build a personalised portfolio that balances financial returns, risk, and ESG values through real S&amp;P500 data and portfolio optimization.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
            <div class="page-panel">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🌍</div>
                <h3 style="color: #17324d; margin-bottom: 0.5rem;">The climate transition is here</h3>
                <p style="color: #48637d; line-height: 1.4;">
                Investors are shifting focus – from simply reducing emissions to actively allocating capital
                toward companies that are well positioned for a low-carbon future. But how do you know which
                stocks truly align with your values without sacrificing returns?
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div class="page-panel">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📈</div>
                <h3 style="color: #17324d; margin-bottom: 0.5rem;">Retail investors demand more</h3>
                <p style="color: #48637d; line-height: 1.4;">
                Retail investors increasingly want their investments to reflect their ESG concerns.
                Let It Grow gives you the tools – powered by real S&P500 ESG data and modern portfolio theory –
                to make informed, sustainable choices without ignoring risk-adjusted returns.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-panel" style="text-align:center; margin-top: 0.8rem;">
            👇 Choose one of the three tools below to start building your sustainable portfolio 👇
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## Choose How You Want To Grow")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="home-card" style="text-align: center;">
            <div class="home-icon">🤖</div>
            <div class="home-title">Recommendation Engine</div>
            <div class="home-text">The app selects two suitable stocks automatically based on your ESG focus, risk tolerance, and risk-free rate.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
        if st.button("Open Recommendation Engine", key="rec_home", use_container_width=True):
            go_to("recommendation")

    with c2:
        st.markdown("""
        <div class="home-card" style="text-align: center;">
            <div class="home-icon">📊</div>
            <div class="home-title">S&P500 Stocks Comparison</div>
            <div class="home-text">Choose any two S&P500 stocks from the dataset and compare them using return, risk, correlation, and ESG characteristics.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
        if st.button("Open S&P500 Comparison", key="sp_home", use_container_width=True):
            go_to("sp500")

    with c3:
        st.markdown("""
        <div class="home-card" style="text-align: center;">
            <div class="home-icon">🛠️</div>
            <div class="home-title">Advanced Custom Generator</div>
            <div class="home-text">Manually enter two custom assets and all portfolio parameters to generate a fully custom optimised portfolio.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
        if st.button("Open Custom Generator", key="custom_home", use_container_width=True):
            go_to("custom")

    st.markdown("## Why Let It Grow?")
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.markdown("""
        <div class="page-panel" style="text-align: center;">
            <div style="font-size: 1.8rem;">🎯</div>
            <div style="font-weight: 600; margin: 0.5rem 0; color: #17324d;">Personalised</div>
            <div style="font-size: 0.85rem; color: #64748b;">Adjust risk, ESG focus, and rate</div>
        </div>
        """, unsafe_allow_html=True)

    with b2:
        st.markdown("""
        <div class="page-panel" style="text-align: center;">
            <div style="font-size: 1.8rem;">📈</div>
            <div style="font-weight: 600; margin: 0.5rem 0; color: #17324d;">Modern Theory</div>
            <div style="font-size: 0.85rem; color: #64748b;">Efficient frontier + utility max</div>
        </div>
        """, unsafe_allow_html=True)

    with b3:
        st.markdown("""
        <div class="page-panel" style="text-align: center;">
            <div style="font-size: 1.8rem;">🌍</div>
            <div style="font-weight: 600; margin: 0.5rem 0; color: #17324d;">Real ESG data</div>
            <div style="font-size: 0.85rem; color: #64748b;">S&P500 E/S/G scores</div>
        </div>
        """, unsafe_allow_html=True)

    with b4:
        st.markdown("""
        <div class="page-panel" style="text-align: center;">
            <div style="font-size: 1.8rem;">⚡</div>
            <div style="font-weight: 600; margin: 0.5rem 0; color: #17324d;">Interactive</div>
            <div style="font-size: 0.85rem; color: #64748b;">Works on any device</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## Three Ways To Build Your Let It Grow Portfolio")
    with st.expander("🤖 Recommendation Engine – fully automated"):
        st.write("""
        - Environmental / Social / Governance modes prioritize the matching ESG dimension while keeping strong profitability.
        - Balanced ESG ranks stocks by average ESG score.
        - Pure Financials Focus ignores ESG for stock selection and ranks by return.
        - The selected pair is then optimized into a final portfolio.
        """)

    with st.expander("📊 S&P500 Stocks Comparison – pick any two"):
        st.write("""
        - Choose any two S&P500 stocks by name or ticker.
        - The app fetches returns, volatilities, correlation, and ESG scores.
        - It then draws the efficient frontier, Capital Market Line, and finds the optimal blend for your utility.
        """)

    with st.expander("🛠️ Advanced Custom Generator – full control"):
        st.write("""
        - Define every parameter manually: return, risk, correlation, ESG scores, and internal E/S/G weights.
        - No dependency on the dataset – analyse any two assets you want.
        - Ideal for testing hypothetical or classroom portfolios.
        """)

# --------------------------------------------------
# RECOMMENDATION PAGE
# --------------------------------------------------
elif st.session_state.page == "recommendation":
    render_brand_header()
    render_back_button()

    st.markdown('<div class="page-panel">', unsafe_allow_html=True)
    st.subheader("Recommendation Engine")

    col1, col2, col3 = st.columns(3)
    with col1:
        esg_focus = st.selectbox(
            "Preferred ESG Focus",
            ["Balanced ESG", "Environmental", "Social", "Governance", "Pure Financials Focus"],
            key="rec_esg_focus"
        )
    with col2:
        gamma = st.slider("Risk Tolerance / Aversion (γ)", 0.5, 10.0, 5.0, 0.5, key="rec_gamma")
    with col3:
        r_free = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1, key="rec_rf") / 100

    st.markdown("</div>", unsafe_allow_html=True)

    esg_pref, lambda_esg = add_preference_scores(esg, esg_focus)
    asset_summary = get_single_asset_summary_all(prices)

    universe = build_recommendation_universe(esg_pref, asset_summary, esg_focus)
    chosen = choose_recommended_pair(prices, universe, esg_focus, gamma, lambda_esg)

    if chosen is None:
        st.error("No valid stock pair could be formed under the current recommendation constraints.")
        st.stop()

    ticker1 = chosen["ticker1"]
    ticker2 = chosen["ticker2"]
    stats = chosen["stats"]
    result = chosen["result"]
    chosen_row_1 = chosen["row1"]
    chosen_row_2 = chosen["row2"]

    name1 = get_asset_name(ticker1)
    name2 = get_asset_name(ticker2)

    esg_row_1 = esg_pref[esg_pref["ticker"] == ticker1].iloc[0]
    esg_row_2 = esg_pref[esg_pref["ticker"] == ticker2].iloc[0]

    rating1, level1 = esg_rating(float(esg_row_1["esg_mean_score"]))
    rating2, level2 = esg_rating(float(esg_row_2["esg_mean_score"]))

    recommendation_reason = build_recommendation_reason(esg_focus, chosen_row_1, chosen_row_2)

    render_outputs(
        ticker1, ticker2, stats, result, r_free, esg_focus,
        esg_row_1, esg_row_2, name1, name2,
        rating1, rating2, level1, level2,
        recommendation_reason=recommendation_reason
    )

# --------------------------------------------------
# S&P500 PAGE
# --------------------------------------------------
elif st.session_state.page == "sp500":
    render_brand_header()
    render_back_button()

    st.markdown('<div class="page-panel">', unsafe_allow_html=True)
    st.subheader("S&P500 Stocks Comparison")

    search_df = name_map.copy()
    search_df["label"] = build_label(search_df)
    labels = sorted(search_df["label"].tolist())

    c1, c2, c3 = st.columns(3)
    with c1:
        esg_focus = st.selectbox(
            "Preferred ESG Focus",
            ["Balanced ESG", "Environmental", "Social", "Governance", "Pure Financials Focus"],
            key="sp_esg_focus"
        )
    with c2:
        gamma = st.slider("Risk Tolerance / Aversion (γ)", 0.5, 10.0, 5.0, 0.5, key="sp_gamma")
    with c3:
        r_free = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1, key="sp_rf") / 100

    d1, d2 = st.columns(2)
    with d1:
        label1 = st.selectbox("Select Asset 1", labels, key="sp_label1")
    with d2:
        label2 = st.selectbox("Select Asset 2", labels, index=1 if len(labels) > 1 else 0, key="sp_label2")

    st.markdown("</div>", unsafe_allow_html=True)

    ticker1 = search_df.loc[search_df["label"] == label1, "ticker"].iloc[0]
    ticker2 = search_df.loc[search_df["label"] == label2, "ticker"].iloc[0]

    if ticker1 == ticker2:
        st.warning("Please select two different assets.")
        st.stop()

    esg_pref, lambda_esg = add_preference_scores(esg, esg_focus)
    stats = get_asset_stats(prices, ticker1, ticker2)
    if stats is None:
        st.error("Not enough overlapping data to compare these two assets.")
        st.stop()

    if esg_focus == "Pure Financials Focus":
        pref1 = 0.0
        pref2 = 0.0
    else:
        pref1 = float(esg_pref.loc[esg_pref["ticker"] == ticker1, "preference_score"].iloc[0])
        pref2 = float(esg_pref.loc[esg_pref["ticker"] == ticker2, "preference_score"].iloc[0])

    result = optimize_two_asset_portfolio(
        stats["r1"], stats["r2"],
        stats["sd1"], stats["sd2"],
        stats["rho"],
        pref1, pref2,
        gamma, lambda_esg
    )

    name1 = get_asset_name(ticker1)
    name2 = get_asset_name(ticker2)

    esg_row_1 = esg_pref[esg_pref["ticker"] == ticker1].iloc[0]
    esg_row_2 = esg_pref[esg_pref["ticker"] == ticker2].iloc[0]

    rating1, level1 = esg_rating(float(esg_row_1["esg_mean_score"]))
    rating2, level2 = esg_rating(float(esg_row_2["esg_mean_score"]))

    render_outputs(
        ticker1, ticker2, stats, result, r_free, esg_focus,
        esg_row_1, esg_row_2, name1, name2,
        rating1, rating2, level1, level2
    )

# --------------------------------------------------
# CUSTOM PAGE
# --------------------------------------------------
elif st.session_state.page == "custom":
    render_brand_header()
    render_back_button()

    st.markdown('<div class="page-panel">', unsafe_allow_html=True)
    st.subheader("Advanced Custom Portfolio Generator")

    c1, c2, c3 = st.columns(3)
    with c1:
        esg_focus = st.selectbox(
            "Preferred ESG Focus",
            ["Balanced ESG", "Environmental", "Social", "Governance", "Pure Financials Focus"],
            key="custom_esg_focus"
        )
    with c2:
        gamma = st.slider("Risk Tolerance / Aversion (γ)", 0.5, 10.0, 5.0, 0.5, key="custom_gamma")
    with c3:
        r_free = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1, key="custom_rf") / 100

    st.markdown("<div class='soft-rule'></div>", unsafe_allow_html=True)

    a1, a2 = st.columns(2)

    with a1:
        st.markdown("### Asset 1")
        name1 = st.text_input("Asset 1 Name", value="Asset 1", key="custom_name1")
        ticker1 = name1
        r1 = st.number_input("Asset 1 Expected Return (%)", value=8.0, step=0.1, key="custom_r1") / 100
        sd1 = st.number_input("Asset 1 Standard Deviation (%)", value=15.0, step=0.1, key="custom_sd1") / 100
        esg_mean_1 = st.number_input("Asset 1 Average ESG Score (0-10)", min_value=0.0, max_value=10.0, value=6.5, step=0.1, key="custom_esgmean1")
        env1 = st.number_input("Asset 1 Environmental Weight", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="custom_env1")
        soc1 = st.number_input("Asset 1 Social Weight", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="custom_soc1")
        gov1 = st.number_input("Asset 1 Governance Weight", min_value=0.0, max_value=1.0, value=0.34, step=0.01, key="custom_gov1")

    with a2:
        st.markdown("### Asset 2")
        name2 = st.text_input("Asset 2 Name", value="Asset 2", key="custom_name2")
        ticker2 = name2
        r2 = st.number_input("Asset 2 Expected Return (%)", value=10.0, step=0.1, key="custom_r2") / 100
        sd2 = st.number_input("Asset 2 Standard Deviation (%)", value=18.0, step=0.1, key="custom_sd2") / 100
        esg_mean_2 = st.number_input("Asset 2 Average ESG Score (0-10)", min_value=0.0, max_value=10.0, value=5.8, step=0.1, key="custom_esgmean2")
        env2 = st.number_input("Asset 2 Environmental Weight", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="custom_env2")
        soc2 = st.number_input("Asset 2 Social Weight", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="custom_soc2")
        gov2 = st.number_input("Asset 2 Governance Weight", min_value=0.0, max_value=1.0, value=0.34, step=0.01, key="custom_gov2")

    rho = st.number_input("Correlation Between Asset 1 and Asset 2", min_value=-1.0, max_value=1.0, value=0.25, step=0.01, key="custom_rho")

    st.markdown("</div>", unsafe_allow_html=True)

    _, _, _, lambda_esg = get_esg_focus_weights(esg_focus)

    def custom_pref_score(env, soc, gov, esg_focus):
        if esg_focus == "Balanced ESG":
            return ((env + soc + gov) / 3) * 10
        elif esg_focus == "Environmental":
            return env * 10
        elif esg_focus == "Social":
            return soc * 10
        elif esg_focus == "Governance":
            return gov * 10
        else:
            return 0.0

    pref1 = custom_pref_score(env1, soc1, gov1, esg_focus)
    pref2 = custom_pref_score(env2, soc2, gov2, esg_focus)

    result = optimize_two_asset_portfolio(
        r1, r2, sd1, sd2, rho, pref1, pref2, gamma, lambda_esg
    )

    stats = {
        "r1": r1,
        "r2": r2,
        "sd1": sd1,
        "sd2": sd2,
        "rho": rho
    }

    esg_row_1 = pd.Series({
        "environmental": env1 * 10,
        "social": soc1 * 10,
        "governance": gov1 * 10,
        "esg_score": esg_mean_1 * 3,
        "esg_mean_score": esg_mean_1,
        "environmental_weight": env1,
        "social_weight": soc1,
        "governance_weight": gov1
    })

    esg_row_2 = pd.Series({
        "environmental": env2 * 10,
        "social": soc2 * 10,
        "governance": gov2 * 10,
        "esg_score": esg_mean_2 * 3,
        "esg_mean_score": esg_mean_2,
        "environmental_weight": env2,
        "social_weight": soc2,
        "governance_weight": gov2
    })

    rating1, level1 = esg_rating(float(esg_row_1["esg_mean_score"]))
    rating2, level2 = esg_rating(float(esg_row_2["esg_mean_score"]))

    render_outputs(
        ticker1, ticker2, stats, result, r_free, esg_focus,
        esg_row_1, esg_row_2, name1, name2,
        rating1, rating2, level1, level2
    )
