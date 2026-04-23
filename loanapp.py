import pickle
from pathlib import Path

import pandas as pd
import streamlit as st


LENDER_PAYOUTS = {
    "A": 250,
    "B": 350,
    "C": 150,
}


def prettify_option(value: str) -> str:
    return str(value).replace("_", " ").strip().title()


def option_labels(options: list[str]) -> dict[str, str]:
    return {option: prettify_option(option) for option in options}


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        /* ── Hero banner ── */
        .hero {
            border-radius: 20px;
            padding: 2.4rem 2.6rem 2rem;
            background: linear-gradient(135deg, #0d1b2a 0%, #1849a9 100%);
            margin-bottom: 2rem;
        }
        .hero-badge {
            display: inline-block;
            padding: 0.28rem 0.85rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            color: #bfd0f5;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.9rem;
        }
        .hero h1 {
            margin: 0 0 0.55rem;
            color: #ffffff !important;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.06;
            letter-spacing: -0.03em;
        }
        .hero p {
            margin: 0 0 1.5rem;
            color: rgba(255,255,255,0.78) !important;
            font-size: 1.03rem;
            max-width: 600px;
            line-height: 1.6;
        }
        .hero-chips { display: flex; flex-wrap: wrap; gap: 0.55rem; }
        .hero-chip {
            padding: 0.45rem 1rem;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.18);
            color: #ffffff !important;
            font-size: 0.85rem;
            font-weight: 500;
        }

        /* ── Section headers ── */
        .sec-hdr {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.5rem 0 0.2rem;
        }
        .sec-icon {
            width: 30px; height: 30px;
            border-radius: 8px;
            background: #dbeafe;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.95rem;
            flex-shrink: 0;
        }
        .sec-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #0d1b2a !important;
        }
        .sec-sub {
            font-size: 0.88rem;
            color: #64748b !important;
            margin: 0.1rem 0 0.85rem;
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            border: 1.5px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 1rem 1.1rem !important;
            background: #ffffff !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #475569 !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stMetricValue"] > div {
            color: #0d1b2a !important;
            font-weight: 700 !important;
        }

        /* ── Result boxes ── */
        .result-box {
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin: 0.6rem 0 0.4rem;
            font-weight: 700;
            font-size: 1rem;
        }
        .result-approved { background: #f0fdf4; border: 2px solid #22c55e; color: #14532d !important; }
        .result-denied   { background: #fef2f2; border: 2px solid #ef4444; color: #7f1d1d !important; }
        .result-review   { background: #fffbeb; border: 2px solid #f59e0b; color: #78350f !important; }

        /* ── Progress bar ── */
        .stProgress > div > div > div > div {
            border-radius: 999px;
            background: linear-gradient(90deg, #1849a9, #3b82f6) !important;
        }

        /* ── Predict button ── */
        div[data-testid="stButton"] > button[kind="primary"] {
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            font-weight: 700;
            width: 100%;
            background: linear-gradient(135deg, #1849a9, #3b82f6) !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(24,73,169,0.3) !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1340a0, #2563eb) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-badge">BUS 458 &mdash; Loan Decision Intelligence</div>
            <h1>LenderMatch Intelligence</h1>
            <p>
                Predict loan approval and identify which lender delivers the highest expected
                payout for each applicant &mdash; built on a Decision Tree classifier
                trained on real-world loan data.
            </p>
            <div class="hero-chips">
                <div class="hero-chip">Maximize Total Payout</div>
                <div class="hero-chip">Decision Tree Model</div>
                <div class="hero-chip">Risk-Aware Scoring</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, sub: str):
    st.markdown(
        f"""
        <div class="sec-hdr">
            <div class="sec-icon">{icon}</div>
            <span class="sec-title">{title}</span>
        </div>
        <p class="sec-sub">{sub}</p>
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
    st.set_page_config(
        page_title="LenderMatch Intelligence",
        page_icon=":bar_chart:",
        layout="wide",
    )
    inject_css()
    render_hero()

    base_dir = Path(__file__).parent
    default_model_path = base_dir / "my_model.pkl"
    default_csv_path = base_dir / "loan_data_analysis_final.csv"

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("#### Lender Payout Reference")
        st.caption("Expected Payout = Approval Probability x Lender Payout")
        payout_df = pd.DataFrame(
            [{"Lender": k, "Max Payout ($)": v} for k, v in LENDER_PAYOUTS.items()]
        )
        st.dataframe(payout_df, use_container_width=True, hide_index=True)
        st.divider()
        with st.expander("Model Settings"):
            model_path_text = st.text_input("Model (.pkl) path", value=str(default_model_path))
            csv_path_text = st.text_input("Reference CSV path", value=str(default_csv_path))

    # ── Load model ────────────────────────────────────────────────
    model_path = Path(model_path_text)
    csv_path = Path(csv_path_text)

    if not model_path.exists():
        st.error(f"Model file not found: `{model_path}`")
        st.stop()

    model = load_model(model_path)

    if not hasattr(model, "feature_names_in_"):
        st.error("Model does not expose `feature_names_in_`. Re-train using a pandas DataFrame.")
        st.stop()

    model_feature_names = list(model.feature_names_in_)
    ref_df = load_reference_data(csv_path)

    # ── Option lists ──────────────────────────────────────────────
    reason_options = pick_options(
        ref_df, "Reason",
        ["credit_card_refinancing", "debt_consolidation", "home_improvement", "major_purchase"],
    )
    emp_status_options = pick_options(
        ref_df, "Employment_Status",
        ["full_time", "part_time", "self_employed", "unemployed"],
    )
    emp_sector_options = pick_options(
        ref_df, "Employment_Sector",
        ["information_technology", "healthcare", "finance", "consumer_discretionary"],
    )
    lender_options = pick_options(ref_df, "Lender", ["A", "B", "C"])

    reason_labels = option_labels(reason_options)
    emp_status_labels = option_labels(emp_status_options)
    emp_sector_labels = option_labels(emp_sector_options)

    fico_default = numeric_default(ref_df, "FICO_score", 680)
    income_default = numeric_default(ref_df, "Monthly_Gross_Income", 5500)
    housing_default = numeric_default(ref_df, "Monthly_Housing_Payment", 1200)
    requested_default = numeric_default(ref_df, "Requested_Loan_Amount", 75000)

    # ── Financial Information ─────────────────────────────────────
    with st.container(border=True):
        section_header(
            "💰", "Financial Information",
            "The primary drivers of approval likelihood and credit risk.",
        )
        fin_col1, fin_col2 = st.columns(2)
        with fin_col1:
            fico_score = st.slider("FICO Score", 300, 850, value=int(fico_default))
            monthly_gross_income = st.number_input(
                "Monthly Gross Income ($)", min_value=0.0, value=float(income_default), step=100.0,
            )
        with fin_col2:
            monthly_housing_payment = st.number_input(
                "Monthly Housing Payment ($)", min_value=0.0, value=float(housing_default), step=25.0,
            )
            requested_loan_amount = st.number_input(
                "Requested Loan Amount ($)", min_value=0.0, value=float(requested_default), step=500.0,
            )

    # ── Application Details ───────────────────────────────────────
    with st.container(border=True):
        section_header(
            "📋", "Application Details",
            "Complete the profile so the model can compare lenders on risk and return.",
        )
        app_col1, app_col2 = st.columns(2)
        with app_col1:
            reason = st.selectbox(
                "Loan Reason", reason_options,
                format_func=lambda o: reason_labels.get(o, o),
            )
            employment_status = st.radio(
                "Employment Status", emp_status_options,
                format_func=lambda o: emp_status_labels.get(o, o),
            )
            ever_bankrupt = st.radio(
                "Ever Bankrupt or Foreclose?", ["No", "Yes"], horizontal=True,
            )
        with app_col2:
            employment_sector = st.selectbox(
                "Employment Sector", emp_sector_options,
                format_func=lambda o: emp_sector_labels.get(o, o),
            )
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

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("Run Prediction", type="primary")

    if predict_clicked:
        model_input = build_model_input(raw_values, model_feature_names)
        prediction = int(model.predict(model_input)[0])
        prob_approved = (
            float(model.predict_proba(model_input)[0][1])
            if hasattr(model, "predict_proba") else None
        )

        # Build lender comparison first so best-lender metric is available
        comparison_rows = []
        for lender in lender_options:
            pred_class, pred_prob = predict_for_lender(raw_values, lender, model, model_feature_names)
            expected_payout = (
                pred_prob * LENDER_PAYOUTS.get(lender, 0)
                if pred_prob is not None else float("nan")
            )
            comparison_rows.append({
                "Lender": lender,
                "Decision": "Approved" if pred_class == 1 else "Denied",
                "Approval Probability": pred_prob if pred_prob is not None else float("nan"),
                "Expected Payout ($)": expected_payout,
            })

        comparison_df = pd.DataFrame(comparison_rows)
        sort_col = (
            "Expected Payout ($)"
            if comparison_df["Expected Payout ($)"].notna().any()
            else "Approval Probability"
        )
        comparison_df = comparison_df.sort_values(by=sort_col, ascending=False).reset_index(drop=True)

        st.divider()

        # ── Headline metrics ──────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Approval Likelihood",
            f"{prob_approved:.1%}" if prob_approved is not None else "N/A",
        )
        best_row = comparison_df.iloc[0]
        m2.metric(
            "Best Lender",
            f"Lender {best_row['Lender']}",
            delta=(
                f"${best_row['Expected Payout ($)']:.2f} expected"
                if pd.notna(best_row["Expected Payout ($)"])
                else None
            ),
        )
        m3.metric("Max Available Payout", f"${LENDER_PAYOUTS.get(best_row['Lender'], 0)}")

        # ── Decision result ───────────────────────────────────────
        if prediction == 1:
            st.markdown(
                '<div class="result-box result-approved">&#x2713;&nbsp; Prediction: Approved</div>',
                unsafe_allow_html=True,
            )
        elif prob_approved is not None and 0.4 <= prob_approved <= 0.6:
            st.markdown(
                '<div class="result-box result-review">&#x26A0;&nbsp; Borderline &mdash; Manual Review Recommended</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="result-box result-denied">&#x2715;&nbsp; Prediction: Denied</div>',
                unsafe_allow_html=True,
            )

        if prob_approved is not None:
            st.caption(f"Approval probability: {prob_approved:.2%}")
            st.progress(prob_approved)

        # ── Lender comparison table ───────────────────────────────
        st.markdown("#### Lender Comparison")
        display_df = comparison_df.copy()
        display_df["Approval Probability"] = display_df["Approval Probability"].map(
            lambda v: f"{v:.1%}" if pd.notna(v) else "N/A"
        )
        display_df["Expected Payout ($)"] = display_df["Expected Payout ($)"].map(
            lambda v: f"${v:.2f}" if pd.notna(v) else "N/A"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        top_lender = comparison_df.iloc[0]["Lender"]
        top_ev = comparison_df.iloc[0]["Expected Payout ($)"]
        if pd.notna(top_ev):
            st.success(f"Prioritize **Lender {top_lender}** — highest expected payout of **${top_ev:.2f}**")
        else:
            st.info(f"Prioritize Lender {top_lender}")


if __name__ == "__main__":
    main()
