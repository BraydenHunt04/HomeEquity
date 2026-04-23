import pickle
from pathlib import Path

import pandas as pd
import streamlit as st


LENDER_PAYOUTS = {
    "A": 250,
    "B": 350,
    "C": 150,
}


def render_styles():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Source+Sans+3:wght@400;600;700&display=swap');

            :root {
                --brand-navy: #102542;
                --brand-slate: #1f3b57;
                --brand-gold: #f2a65a;
                --brand-cream: #f8f4ee;
                --brand-mint: #d7efe8;
                --brand-rose: #f6d8d4;
                --text-dark: #132238;
            }

            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(242, 166, 90, 0.20), transparent 28%),
                    radial-gradient(circle at left top, rgba(215, 239, 232, 0.75), transparent 24%),
                    linear-gradient(180deg, #f6efe5 0%, #fbfaf7 42%, #f3f7fa 100%);
                color: var(--text-dark);
                font-family: 'Source Sans 3', sans-serif;
            }

            .block-container {
                padding-top: 2.2rem;
                padding-bottom: 3rem;
                max-width: 1180px;
            }

            h1, h2, h3 {
                font-family: 'Space Grotesk', sans-serif;
                letter-spacing: -0.03em;
                color: var(--brand-navy);
            }

            .hero-shell {
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(16, 37, 66, 0.10);
                border-radius: 28px;
                padding: 2rem 2rem 1.5rem 2rem;
                background: linear-gradient(135deg, rgba(16, 37, 66, 0.97), rgba(31, 59, 87, 0.92));
                box-shadow: 0 22px 60px rgba(16, 37, 66, 0.16);
                margin-bottom: 1.25rem;
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                inset: auto -60px -90px auto;
                width: 260px;
                height: 260px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(242, 166, 90, 0.28), rgba(242, 166, 90, 0));
            }

            .hero-kicker {
                display: inline-block;
                margin-bottom: 0.7rem;
                padding: 0.38rem 0.75rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.12);
                color: #f7e7d1;
                font-size: 0.84rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .hero-title {
                margin: 0;
                color: white;
                font-size: 3rem;
                line-height: 0.98;
            }

            .hero-copy {
                max-width: 680px;
                margin: 0.8rem 0 1.2rem 0;
                color: rgba(255, 255, 255, 0.82);
                font-size: 1.08rem;
            }

            .hero-stats {
                display: flex;
                flex-wrap: wrap;
                gap: 0.8rem;
            }

            .hero-stat {
                min-width: 180px;
                padding: 0.9rem 1rem;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.09);
                backdrop-filter: blur(4px);
            }

            .hero-stat-label {
                color: rgba(255, 255, 255, 0.68);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .hero-stat-value {
                color: white;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.4rem;
                font-weight: 700;
            }

            .section-card {
                border: 1px solid rgba(16, 37, 66, 0.09);
                border-radius: 24px;
                padding: 1.1rem 1.15rem 0.6rem 1.15rem;
                background: rgba(255, 255, 255, 0.72);
                box-shadow: 0 14px 42px rgba(16, 37, 66, 0.07);
                backdrop-filter: blur(8px);
                margin-bottom: 1rem;
            }

            .section-title {
                margin: 0;
                font-size: 1.25rem;
                color: var(--brand-navy);
            }

            .section-copy {
                margin: 0.2rem 0 0.7rem 0;
                color: #516072;
                font-size: 0.98rem;
            }

            .results-banner {
                border: 1px solid rgba(16, 37, 66, 0.08);
                border-radius: 24px;
                padding: 1rem 1.15rem;
                background: linear-gradient(135deg, rgba(255,255,255,0.82), rgba(247, 241, 232, 0.82));
                box-shadow: 0 12px 36px rgba(16, 37, 66, 0.08);
                margin: 0.75rem 0 1rem 0;
            }

            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(16, 37, 66, 0.08);
                border-radius: 22px;
                padding: 1rem 1.1rem;
                box-shadow: 0 12px 30px rgba(16, 37, 66, 0.06);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #fffdf9 0%, #f3f4ef 100%);
                border-right: 1px solid rgba(16, 37, 66, 0.08);
            }

            .stButton > button {
                border-radius: 999px;
                border: none;
                min-height: 3.1rem;
                padding: 0.75rem 1.4rem;
                font-weight: 700;
                background: linear-gradient(135deg, #f2a65a, #eb7f57);
                color: white;
                box-shadow: 0 14px 28px rgba(235, 127, 87, 0.28);
            }

            .stButton > button:hover {
                background: linear-gradient(135deg, #eb9951, #de6d48);
            }

            div[data-baseweb="slider"] > div > div {
                background: linear-gradient(90deg, #f2a65a, #eb7f57);
            }

            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #f2a65a, #eb7f57);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-kicker">Payout-Optimized Underwriting</div>
            <h1 class="hero-title">LenderMatch Intelligence</h1>
            <p class="hero-copy">
                Evaluate applicant strength, estimate approval likelihood, and prioritize the lender
                that offers the strongest expected return for each application.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-label">Primary Goal</div>
                    <div class="hero-stat-value">Maximize Payout</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Model Focus</div>
                    <div class="hero-stat-value">Approval + Profitability</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Decision Lens</div>
                    <div class="hero-stat-value">Risk Aware</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, copy: str):
    st.markdown(
        f"""
        <div class="section-card">
            <h3 class="section-title">{title}</h3>
            <p class="section-copy">{copy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_model(model_path: Path):
    with open(model_path, "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_reference_data(csv_path: Path):
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


def pick_options(df: pd.DataFrame, column: str, fallback: list[str]) -> list[str]:
    if df is None or column not in df.columns:
        return fallback

    values = sorted([str(v) for v in df[column].dropna().unique().tolist()])
    return values if values else fallback


def numeric_default(df: pd.DataFrame, column: str, fallback: float) -> float:
    if df is None or column not in df.columns:
        return fallback

    return float(df[column].median())


def build_model_input(raw_values: dict, model_feature_names) -> pd.DataFrame:
    input_df = pd.DataFrame([raw_values])
    encoded_input = pd.get_dummies(input_df, drop_first=True)

    # Reindex to match the exact order used when the model was trained.
    encoded_input = encoded_input.reindex(columns=model_feature_names, fill_value=0)
    return encoded_input


def predict_for_lender(raw_values: dict, lender: str, model, model_feature_names):
    lender_values = dict(raw_values)
    lender_values["Lender"] = lender
    model_input = build_model_input(lender_values, model_feature_names)

    pred_class = int(model.predict(model_input)[0])
    pred_prob = None
    if hasattr(model, "predict_proba"):
        pred_prob = float(model.predict_proba(model_input)[0][1])

    return pred_class, pred_prob


def main():
    st.set_page_config(page_title="Loan Approval App", layout="wide")
    render_styles()
    render_hero()

    base_dir = Path(__file__).parent
    default_model_path = base_dir / "my_model.pkl"
    default_csv_path = base_dir / "loan_data_analysis_final.csv"

    with st.sidebar:
        st.markdown("### Payout Reference")
        st.caption("Use expected payout to decide which lender should receive the application first.")
        payout_df = pd.DataFrame(
            [
                {"Lender": lender, "Payout ($)": payout}
                for lender, payout in LENDER_PAYOUTS.items()
            ]
        )
        st.dataframe(payout_df, use_container_width=True, hide_index=True)

        with st.expander("Advanced Model Settings"):
            model_path_text = st.text_input("Path to model (.pkl)", value=str(default_model_path))
            csv_path_text = st.text_input("Optional path to reference CSV", value=str(default_csv_path))

    model_path = Path(model_path_text)
    csv_path = Path(csv_path_text)

    if not model_path.exists():
        st.error(f"Model file was not found: {model_path}")
        st.stop()

    model = load_model(model_path)

    if not hasattr(model, "feature_names_in_"):
        st.error("This model does not expose feature_names_in_. Re-train with a pandas DataFrame and save again.")
        st.stop()

    model_feature_names = list(model.feature_names_in_)
    ref_df = load_reference_data(csv_path)

    reason_options = pick_options(
        ref_df,
        "Reason",
        ["credit_card_refinancing", "debt_consolidation", "home_improvement", "major_purchase"],
    )
    emp_status_options = pick_options(ref_df, "Employment_Status", ["full_time", "part_time", "self_employed", "unemployed"])
    emp_sector_options = pick_options(
        ref_df,
        "Employment_Sector",
        ["information_technology", "healthcare", "finance", "consumer_discretionary"],
    )
    lender_options = pick_options(ref_df, "Lender", ["A", "B", "C"])

    fico_default = numeric_default(ref_df, "FICO_score", 680)
    income_default = numeric_default(ref_df, "Monthly_Gross_Income", 5500)
    housing_default = numeric_default(ref_df, "Monthly_Housing_Payment", 1200)
    requested_default = numeric_default(ref_df, "Requested_Loan_Amount", 75000)

    render_section_intro(
        "Financial Information",
        "Capture the core financial drivers that most strongly influence loan approval and payout value.",
    )
    with st.container(border=True):
        fin_col1, fin_col2 = st.columns(2)

        with fin_col1:
            fico_score = st.slider("FICO Score", 300, 850, value=int(fico_default))
            monthly_gross_income = st.number_input(
                "Monthly Gross Income ($)",
                min_value=0.0,
                value=float(income_default),
                step=100.0,
            )

        with fin_col2:
            monthly_housing_payment = st.number_input(
                "Monthly Housing Payment ($)",
                min_value=0.0,
                value=float(housing_default),
                step=25.0,
            )
            requested_loan_amount = st.number_input(
                "Requested Loan Amount ($)",
                min_value=0.0,
                value=float(requested_default),
                step=500.0,
            )

    render_section_intro(
        "Application Details",
        "Complete the profile with application context so the model can compare lenders on both risk and return.",
    )
    with st.container(border=True):
        app_col1, app_col2 = st.columns(2)

        with app_col1:
            reason = st.selectbox("Loan Reason", reason_options)
            employment_status = st.radio("Employment Status", emp_status_options)
            ever_bankrupt = st.radio("Ever Bankrupt or Foreclose?", ["No", "Yes"], horizontal=True)

        with app_col2:
            employment_sector = st.selectbox("Employment Sector", emp_sector_options)
            selected_lender = st.radio("Lender", lender_options, horizontal=True)

    raw_values = {
        "Reason": reason,
        "Requested_Loan_Amount": float(requested_loan_amount),
        "FICO_score": float(fico_score),
        "Employment_Status": employment_status,
        "Employment_Sector": employment_sector,
        "Monthly_Gross_Income": float(monthly_gross_income),
        "Monthly_Housing_Payment": float(monthly_housing_payment),
        "Ever_Bankrupt_or_Foreclose": 1 if ever_bankrupt == "Yes" else 0,
        "Lender": selected_lender,
    }

    if st.button("Predict Approval", type="primary"):
        model_input = build_model_input(raw_values, model_feature_names)
        prediction = int(model.predict(model_input)[0])

        prob_approved = None
        if hasattr(model, "predict_proba"):
            prob_approved = float(model.predict_proba(model_input)[0][1])

        comparison_rows = []
        for lender in lender_options:
            pred_class, pred_prob = predict_for_lender(raw_values, lender, model, model_feature_names)
            expected_payout = None
            if pred_prob is not None:
                expected_payout = pred_prob * LENDER_PAYOUTS.get(lender, 0)

            comparison_rows.append(
                {
                    "Lender": lender,
                    "Predicted Decision": "Approved" if pred_class == 1 else "Denied",
                    "Approval Probability": pred_prob if pred_prob is not None else float("nan"),
                    "Expected Payout": expected_payout if expected_payout is not None else float("nan"),
                }
            )

        comparison_df = pd.DataFrame(comparison_rows)
        if comparison_df["Expected Payout"].notna().any():
            comparison_df = comparison_df.sort_values(by="Expected Payout", ascending=False)
        elif comparison_df["Approval Probability"].notna().any():
            comparison_df = comparison_df.sort_values(by="Approval Probability", ascending=False)

        st.markdown(
            """
            <div class="results-banner">
                <h3 class="section-title">Decision Summary</h3>
                <p class="section-copy">Review approval strength first, then choose the lender with the best expected payout.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        top_metrics = st.columns(2)
        if prob_approved is not None:
            top_metrics[0].metric("Approval Likelihood", f"{prob_approved:.2%}")
        else:
            top_metrics[0].metric("Approval Likelihood", "N/A")

        if comparison_df["Expected Payout"].notna().any():
            best_row = comparison_df.iloc[0]
            top_metrics[1].metric(
                "Best Recommended Lender",
                str(best_row["Lender"]),
                delta=f"Expected payout ${best_row['Expected Payout']:.2f}",
            )
        else:
            top_metrics[1].metric("Best Recommended Lender", str(selected_lender))

        st.subheader("Prediction")
        if prediction == 1:
            st.success("Prediction: Approved")
        elif prob_approved is not None and 0.4 <= prob_approved <= 0.6:
            st.warning("Prediction: Borderline case. Manual review recommended.")
        else:
            st.error("Prediction: Denied")

        if prob_approved is not None:
            st.progress(prob_approved)
            st.write(f"Approval probability: {prob_approved:.2%}")

        st.subheader("Lender Comparison")
        display_df = comparison_df.copy()
        if display_df["Approval Probability"].notna().any():
            display_df["Approval Probability"] = display_df["Approval Probability"].map(lambda value: f"{value:.2%}" if pd.notna(value) else "N/A")
        if display_df["Expected Payout"].notna().any():
            display_df["Expected Payout"] = display_df["Expected Payout"].map(lambda value: f"${value:.2f}" if pd.notna(value) else "N/A")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if comparison_df["Expected Payout"].notna().any():
            top_lender = comparison_df.iloc[0]["Lender"]
            top_value = comparison_df.iloc[0]["Expected Payout"]
            st.info(f"Best lender to prioritize: {top_lender} (${top_value:.2f} expected payout)")
        elif comparison_df["Approval Probability"].notna().any():
            top_lender = comparison_df.iloc[0]["Lender"]
            top_prob = comparison_df.iloc[0]["Approval Probability"]
            st.info(f"Best lender to prioritize: {top_lender} ({top_prob:.2%} approval probability)")


if __name__ == "__main__":
    main()
