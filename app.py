import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from itertools import combinations

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="GreenVest Portfolio Optimizer",
    page_icon="♻️",
    layout="wide"
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f4fbf6 0%, #e8f5e9 100%);
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #2e7d32;
        margin-bottom: 1.2rem;
    }
    .section-card {
        background-color: white;
        border: 1px solid #d0e8d4;
        border-radius: 18px;
        padding: 18px 22px;
        box-shadow: 0 4px 14px rgba(27, 94, 32, 0.08);
        margin-bottom: 16px;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dceedd;
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 3px 10px rgba(27, 94, 32, 0.05);
    }
    .stButton > button {
        background: linear-gradient(90deg, #2e7d32, #43a047);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.6rem 1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">👔 GreenVest Portfolio Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Find sustainable portfolio recommendations based on risk tolerance and ESG preferences.</div>',
    unsafe_allow_html=True
)

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

def compute_cagr(price_series, date_series):
    if len(price_series) < 2:
        return np.nan
    start_price = price_series.iloc[0]
    end_price = price_series.iloc[-1]
    start_date = date_series.iloc[0]
    end_date = date_series.iloc[-1]

    if start_price <= 0 or end_price <= 0 or end_date <= start_date:
        return np.nan

    years = (end_date - start_date).days / 365.25
    if years <= 0:
        return np.nan

    return (end_price / start_price) ** (1 / years) - 1

def get_single_asset_summary(prices_df, ticker):
    df = prices_df[prices_df["ticker"] == ticker][["date", "price"]].sort_values("date").copy()
    if len(df) < 12:
        return None

    df["ret"] = df["price"].pct_change()
    df = df.dropna()

    if len(df) < 12:
        return None

    cagr = compute_cagr(
        prices_df[prices_df["ticker"] == ticker].sort_values("date")["price"].reset_index(drop=True),
        prices_df[prices_df["ticker"] == ticker].sort_values("date")["date"].reset_index(drop=True)
    )
    risk = df["ret"].std() * np.sqrt(12)

    return {"expected_return": cagr, "risk": risk}

def get_asset_stats(prices_df, ticker1, ticker2):
    raw1 = prices_df[prices_df["ticker"] == ticker1][["date", "price"]].sort_values("date").copy()
    raw2 = prices_df[prices_df["ticker"] == ticker2][["date", "price"]].sort_values("date").copy()

    if len(raw1) < 12 or len(raw2) < 12:
        return None

    cagr1 = compute_cagr(raw1["price"].reset_index(drop=True), raw1["date"].reset_index(drop=True))
    cagr2 = compute_cagr(raw2["price"].reset_index(drop=True), raw2["date"].reset_index(drop=True))

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
        "r1": cagr1,
        "r2": cagr2,
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

def describe_investment_type(risk, esg_mean, sharpe):
    if risk < 0.18:
        risk_text = "relatively defensive"
    elif risk < 0.28:
        risk_text = "balanced"
    else:
        risk_text = "growth-oriented and higher-risk"

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

    return f"This portfolio is a {risk_text} investment with {esg_text}, and it appears {efficiency_text}."

# --------------------------------------------------
# SIDEBAR INPUTS
# --------------------------------------------------
st.sidebar.header("Investor Preferences")

mode = st.sidebar.radio(
    "Choose App Mode",
    ["Simple Recommendation", "Advanced Comparison"]
)

esg_focus = st.sidebar.selectbox(
    "Preferred ESG Focus",
    ["Balanced ESG", "Environmental", "Social", "Governance"]
)

gamma = st.sidebar.slider("Risk Tolerance / Aversion (γ)", 0.5, 10.0, 5.0, 0.5)
r_free = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1) / 100

if esg_focus == "Balanced ESG":
    env_weight, soc_weight, gov_weight = 1/3, 1/3, 1/3
    lambda_esg = 0.6
elif esg_focus == "Environmental":
    env_weight, soc_weight, gov_weight = 0.7, 0.15, 0.15
    lambda_esg = 0.7
elif esg_focus == "Social":
    env_weight, soc_weight, gov_weight = 0.15, 0.7, 0.15
    lambda_esg = 0.7
else:
    env_weight, soc_weight, gov_weight = 0.15, 0.15, 0.7
    lambda_esg = 0.7

esg["preference_score"] = (
    env_weight * esg["environmental"] +
    soc_weight * esg["social"] +
    gov_weight * esg["governance"]
)

# --------------------------------------------------
# SIMPLE RECOMMENDATION MODE
# --------------------------------------------------
if mode == "Simple Recommendation":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Simple Recommendation")
    st.write(
        "This mode identifies promising stocks based on your ESG focus and historical performance, "
        "then builds the optimized two-asset portfolio."
    )

    summaries = []
    for ticker in prices["ticker"].drop_duplicates():
        s = get_single_asset_summary(prices, ticker)
        if s is not None and pd.notna(s["expected_return"]) and pd.notna(s["risk"]):
            summaries.append({
                "ticker": ticker,
                "expected_return": s["expected_return"],
                "risk": s["risk"]
            })

    asset_summary = pd.DataFrame(summaries)

    universe = esg.merge(asset_summary, on="ticker", how="inner")

    universe["selection_score"] = (
        0.55 * (universe["preference_score"] / 10) +
        0.30 * universe["expected_return"] -
        0.15 * universe["risk"]
    )

    top_assets = universe.sort_values("selection_score", ascending=False).head(15).copy()

    best_pair = None
    best_pair_score = -np.inf

    for t1, t2 in combinations(top_assets["ticker"], 2):
        stats = get_asset_stats(prices, t1, t2)
        if stats is None:
            continue

        esg1 = float(esg.loc[esg["ticker"] == t1, "preference_score"].iloc[0])
        esg2 = float(esg.loc[esg["ticker"] == t2, "preference_score"].iloc[0])

        result = optimize_two_asset_portfolio(
            stats["r1"], stats["r2"],
            stats["sd1"], stats["sd2"],
            stats["rho"],
            esg1, esg2,
            gamma, lambda_esg
        )

        if result["utility_opt"] > best_pair_score:
            best_pair_score = result["utility_opt"]
            best_pair = (t1, t2, stats, result)

    if best_pair is None:
        st.error("No valid stock pair could be formed from the available data.")
        st.stop()

    ticker1, ticker2, stats, result = best_pair

# --------------------------------------------------
# ADVANCED COMPARISON MODE
# --------------------------------------------------
else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Advanced Comparison")

    search_df = name_map.copy()
    search_df["label"] = build_label(search_df)

    labels = sorted(search_df["label"].tolist())
    label1 = st.selectbox("Select Asset 1", labels)
    label2 = st.selectbox("Select Asset 2", labels, index=1 if len(labels) > 1 else 0)

    ticker1 = search_df.loc[search_df["label"] == label1, "ticker"].iloc[0]
    ticker2 = search_df.loc[search_df["label"] == label2, "ticker"].iloc[0]

    if ticker1 == ticker2:
        st.warning("Please select two different assets.")
        st.stop()

    stats = get_asset_stats(prices, ticker1, ticker2)
    if stats is None:
        st.error("Not enough overlapping data to compare these two assets.")
        st.stop()

    esg1 = float(esg.loc[esg["ticker"] == ticker1, "preference_score"].iloc[0])
    esg2 = float(esg.loc[esg["ticker"] == ticker2, "preference_score"].iloc[0])

    result = optimize_two_asset_portfolio(
        stats["r1"], stats["r2"],
        stats["sd1"], stats["sd2"],
        stats["rho"],
        esg1, esg2,
        gamma, lambda_esg
    )

# --------------------------------------------------
# COMMON OUTPUT
# --------------------------------------------------
name1 = get_asset_name(ticker1)
name2 = get_asset_name(ticker2)

esg_row_1 = esg[esg["ticker"] == ticker1].iloc[0]
esg_row_2 = esg[esg["ticker"] == ticker2].iloc[0]

rating1, level1 = esg_rating(float(esg_row_1["esg_mean_score"]))
rating2, level2 = esg_rating(float(esg_row_2["esg_mean_score"]))

portfolio_esg_mean = result["esg_opt"]
portfolio_rating, portfolio_level = esg_rating(float(portfolio_esg_mean))

if result["risk_opt"] > 0:
    sharpe_ratio = (result["ret_opt"] - r_free) / result["risk_opt"]
else:
    sharpe_ratio = 0

investment_description = describe_investment_type(result["risk_opt"], portfolio_esg_mean, sharpe_ratio)

summary_text = (
    f"The optimized portfolio allocates {result['w1']*100:.2f}% to {name1} and "
    f"{result['w2']*100:.2f}% to {name2}. "
    f"It has an expected annual return of {result['ret_opt']*100:.2f}% and annual risk of {result['risk_opt']*100:.2f}%. "
    f"Based on the average ESG score scale, the portfolio receives a rating of {portfolio_rating} ({portfolio_level})."
)

tab1, tab2, tab3 = st.tabs(["📊 Portfolio Results", "📈 Visualisation", "🏢 ESG Overview"])

with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Portfolio Recommendation")
    st.info(summary_text)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Expected Return", f"{result['ret_opt']*100:.2f}%")
    col2.metric("Risk (Std Dev)", f"{result['risk_opt']*100:.2f}%")
    col3.metric("Sharpe Ratio", f"{sharpe_ratio:.3f}")
    col4.metric("Portfolio ESG Rating", f"{portfolio_rating} ({portfolio_level})")

    st.write("**Interpretation**")
    st.write(investment_description)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Optimized Portfolio Composition")

    weights_df = pd.DataFrame({
        "Asset": [name1, name2],
        "Ticker": [ticker1, ticker2],
        "Weight (%)": [result["w1"] * 100, result["w2"] * 100],
        "Expected Return (%)": [stats["r1"] * 100, stats["r2"] * 100],
        "Risk (%)": [stats["sd1"] * 100, stats["sd2"] * 100],
        "Average ESG Score": [esg_row_1["esg_mean_score"], esg_row_2["esg_mean_score"]],
        "ESG Rating": [rating1, rating2]
    })
    st.dataframe(weights_df, use_container_width=True)

    st.write(
        "This table shows how much of the final portfolio is allocated to each stock, "
        "together with each stock’s CAGR-based return estimate, annualized volatility, and sustainability rating."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("What the Asset Statistics Mean")

    st.write(
        f"**{name1}** has an estimated annual return of **{stats['r1']*100:.2f}%**, measured using CAGR over the sample period, "
        f"and annual volatility of **{stats['sd1']*100:.2f}%**. Its ESG profile translates into a **{rating1} ({level1})** rating."
    )
    st.write(
        f"**{name2}** has an estimated annual return of **{stats['r2']*100:.2f}%**, measured using CAGR over the sample period, "
        f"and annual volatility of **{stats['sd2']*100:.2f}%**. Its ESG profile translates into a **{rating2} ({level2})** rating."
    )
    st.write(
        f"The correlation between the two assets is **{stats['rho']:.3f}**, which measures how similarly they move over time. "
        f"Lower correlation generally means better diversification benefits."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Portfolio Frontier")

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fbfffc")

    ax.plot(
        result["portfolio_risks"],
        result["portfolio_returns"],
        color="#2e7d32",
        linewidth=2.8,
        label="Portfolio Frontier"
    )

    ax.scatter(stats["sd1"], stats["r1"], color="#81c784", s=130, label=name1, zorder=5)
    ax.scatter(stats["sd2"], stats["r2"], color="#388e3c", s=130, label=name2, zorder=5)
    ax.scatter(result["risk_opt"], result["ret_opt"], color="#1b5e20", s=220, marker="D", label="Optimal Portfolio", zorder=6)

    ax.set_title("Risk-Return Frontier", fontsize=14, color="#1b5e20", fontweight="bold")
    ax.set_xlabel("Risk (Standard Deviation)")
    ax.set_ylabel("Expected Return")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.grid(True, alpha=0.25)
    ax.legend()

    st.pyplot(fig)

    st.write(
        "The frontier shows all possible portfolios formed by combining the two selected stocks. "
        "The dark green diamond marks the portfolio with the highest utility given your risk tolerance and ESG preference."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("ESG Overview")

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
    })
    st.dataframe(esg_display, use_container_width=True)

    st.write("**How to read the rating scale**")
    st.write(
        "We convert the total ESG score into an average score by dividing by 3. "
        "That average score is then mapped to the sustainability scale: "
        "AAA = 8.6–10.0, AA = 7.1–8.5, A = 5.7–7.0, BBB = 4.3–5.6, BB = 2.9–4.2, B = 1.4–2.8, CCC = 0.0–1.3."
    )

    st.write(
        f"Based on your chosen ESG focus, **{name1}** and **{name2}** were evaluated using a preference-weighted ESG score. "
        f"The final portfolio itself scores **{portfolio_esg_mean:.2f}**, corresponding to **{portfolio_rating} ({portfolio_level})**."
    )
    st.markdown("</div>", unsafe_allow_html=True)
