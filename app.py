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
    page_icon="🌿",
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
    .stApp {
        background: linear-gradient(180deg, #f4fbf6 0%, #e8f5e9 100%);
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1b5e20;
        margin-bottom: 0.15rem;
    }
    .subtitle {
        font-size: 1.08rem;
        color: #2e7d32;
        margin-bottom: 1.2rem;
    }
    .section-card {
        background-color: white;
        border: 1px solid #d0e8d4;
        border-radius: 18px;
        padding: 20px 24px;
        box-shadow: 0 4px 14px rgba(27, 94, 32, 0.08);
        margin-bottom: 16px;
    }
    .home-card {
        background-color: white;
        border: 1px solid #d0e8d4;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(27, 94, 32, 0.08);
        min-height: 250px;
    }
    .home-icon {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
    }
    .home-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0.4rem;
    }
    .home-text {
        color: #355e3b;
        font-size: 0.98rem;
        min-height: 90px;
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
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        color: white;
    }
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

@st.cache_data
def get_single_asset_summary_all(prices_df):
    summaries = []
    for ticker in prices_df["ticker"].drop_duplicates():
        df = prices_df[prices_df["ticker"] == ticker][["date", "price"]].sort_values("date").copy()
        if len(df) < 12:
            continue

        cagr = compute_cagr(df["price"].reset_index(drop=True), df["date"].reset_index(drop=True))
        df["ret"] = df["price"].pct_change()
        df = df.dropna()

        if len(df) < 12 or pd.isna(cagr):
            continue

        risk = df["ret"].std() * np.sqrt(12)

        summaries.append({
            "ticker": ticker,
            "expected_return": cagr,
            "risk": risk
        })

    return pd.DataFrame(summaries)

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

def describe_investment_type(risk, esg_mean, sharpe, esg_focus):
    if risk < 0.18:
        risk_text = "relatively defensive"
    elif risk < 0.28:
        risk_text = "balanced"
    else:
        risk_text = "growth-oriented and higher-risk"

    if esg_focus == "Pure Financials Focus":
        esg_text = "designed primarily around financial performance rather than sustainability"
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

    return f"This portfolio is a {risk_text} investment with {esg_text}, and it appears {efficiency_text}."

def get_esg_focus_weights(esg_focus):
    if esg_focus == "Balanced ESG":
        return 1/3, 1/3, 1/3, 0.75
    elif esg_focus == "Environmental":
        return 0.7, 0.15, 0.15, 0.85
    elif esg_focus == "Social":
        return 0.15, 0.7, 0.15, 0.85
    elif esg_focus == "Governance":
        return 0.15, 0.15, 0.7, 0.85
    else:  # Pure Financials Focus
        return 1/3, 1/3, 1/3, 0.0

def add_preference_scores(esg_df, esg_focus):
    env_weight, soc_weight, gov_weight, lambda_esg = get_esg_focus_weights(esg_focus)
    out = esg_df.copy()
    out["preference_score"] = (
        env_weight * out["environmental"] +
        soc_weight * out["social"] +
        gov_weight * out["governance"]
    )
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

    colors = ["#66bb6a", "#42a5f5", "#ffa726"]
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90, colors=colors, textprops={"fontsize": 10})
    ax.set_title(title, fontsize=12, fontweight="bold")

def render_back_button():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    if st.button("⬅ Back to Home"):
        go_to("home")
    st.markdown("</div>", unsafe_allow_html=True)

def render_outputs(
    ticker1, ticker2, stats, result, r_free, esg_focus,
    esg_row_1, esg_row_2, name1, name2,
    rating1, rating2, level1, level2
):
    portfolio_esg_mean = result["esg_opt"]
    portfolio_rating, portfolio_level = esg_rating(float(portfolio_esg_mean))

    if result["risk_opt"] > 0:
        sharpe_ratio = (result["ret_opt"] - r_free) / result["risk_opt"]
    else:
        sharpe_ratio = 0

    investment_description = describe_investment_type(result["risk_opt"], portfolio_esg_mean, sharpe_ratio, esg_focus)

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

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("ESG Weight Composition of Each Stock")

        fig2, axes = plt.subplots(1, 2, figsize=(12, 5))
        plot_esg_pie(axes[0], esg_row_1, f"{name1} ESG Weight Mix")
        plot_esg_pie(axes[1], esg_row_2, f"{name2} ESG Weight Mix")
        st.pyplot(fig2)

        st.write(
            "These pie charts show how each stock’s ESG framework is distributed across Environmental, Social, and Governance factors."
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

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if st.session_state.page == "home":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Choose a workflow")
    st.write(
        "Select one of the three tools below to explore sustainable portfolio construction."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="home-card">', unsafe_allow_html=True)
        st.markdown('<div class="home-icon">🤖</div>', unsafe_allow_html=True)
        st.markdown('<div class="home-title">Recommendation Engine</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="home-text">The app selects two suitable stocks automatically based on your ESG focus, risk tolerance, and risk-free rate.</div>',
            unsafe_allow_html=True
        )
        if st.button("Open Recommendation Engine"):
            go_to("recommendation")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="home-card">', unsafe_allow_html=True)
        st.markdown('<div class="home-icon">📊</div>', unsafe_allow_html=True)
        st.markdown('<div class="home-title">S&P500 Stocks Comparison</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="home-text">Choose any two S&P500 stocks from the dataset and compare them using return, risk, correlation, and ESG characteristics.</div>',
            unsafe_allow_html=True
        )
        if st.button("Open S&P500 Comparison"):
            go_to("sp500")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="home-card">', unsafe_allow_html=True)
        st.markdown('<div class="home-icon">🛠️</div>', unsafe_allow_html=True)
        st.markdown('<div class="home-title">Advanced Custom Portfolio Generator</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="home-text">Manually enter two custom assets and all portfolio parameters to generate a fully custom optimized portfolio.</div>',
            unsafe_allow_html=True
        )
        if st.button("Open Custom Generator"):
            go_to("custom")
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# RECOMMENDATION PAGE
# --------------------------------------------------
elif st.session_state.page == "recommendation":
    render_back_button()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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

    universe = esg_pref.merge(asset_summary, on="ticker", how="inner")

    # Cap expected return at 25%
    universe = universe[universe["expected_return"] <= 0.25].copy()

    if esg_focus == "Pure Financials Focus":
        universe["selection_score"] = (
            0.80 * universe["expected_return"] -
            0.20 * universe["risk"]
        )
    else:
        universe["selection_score"] = (
            0.70 * (universe["preference_score"] / 10) +
            0.20 * universe["expected_return"] -
            0.10 * universe["risk"]
        )

    shortlist = universe.sort_values("selection_score", ascending=False).head(10).copy()

    best_pair = None
    best_pair_score = -np.inf

    for t1, t2 in combinations(shortlist["ticker"], 2):
        stats = get_asset_stats(prices, t1, t2)
        if stats is None:
            continue

        esg1 = float(esg_pref.loc[esg_pref["ticker"] == t1, "preference_score"].iloc[0])
        esg2 = float(esg_pref.loc[esg_pref["ticker"] == t2, "preference_score"].iloc[0])

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
        st.error("No valid stock pair could be formed under the current recommendation constraints.")
        st.stop()

    ticker1, ticker2, stats, result = best_pair

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
# S&P500 COMPARISON PAGE
# --------------------------------------------------
elif st.session_state.page == "sp500":
    render_back_button()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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

    esg1 = float(esg_pref.loc[esg_pref["ticker"] == ticker1, "preference_score"].iloc[0])
    esg2 = float(esg_pref.loc[esg_pref["ticker"] == ticker2, "preference_score"].iloc[0])

    result = optimize_two_asset_portfolio(
        stats["r1"], stats["r2"],
        stats["sd1"], stats["sd2"],
        stats["rho"],
        esg1, esg2,
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
# CUSTOM GENERATOR PAGE
# --------------------------------------------------
elif st.session_state.page == "custom":
    render_back_button()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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

    st.markdown("---")

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

    # Preference score based on focus
    def custom_pref_score(env, soc, gov, esg_focus):
        if esg_focus == "Balanced ESG":
            return (env + soc + gov) / 3
        elif esg_focus == "Environmental":
            return 0.7 * env + 0.15 * soc + 0.15 * gov
        elif esg_focus == "Social":
            return 0.15 * env + 0.7 * soc + 0.15 * gov
        elif esg_focus == "Governance":
            return 0.15 * env + 0.15 * soc + 0.7 * gov
        else:
            return (env + soc + gov) / 3

    esg1 = custom_pref_score(env1, soc1, gov1, esg_focus)
    esg2 = custom_pref_score(env2, soc2, gov2, esg_focus)

    result = optimize_two_asset_portfolio(
        r1, r2, sd1, sd2, rho, esg1, esg2, gamma, lambda_esg
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
