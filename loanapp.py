import pickle
from pathlib import Path

import pandas as pd
import streamlit as st


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
    st.title("Loan Approval Predictor")
    st.write("Estimate loan approval using your trained model file (`my_model.pkl`).")

    base_dir = Path(__file__).parent
    default_model_path = base_dir / "my_model.pkl"
    default_csv_path = base_dir / "loan_data_analysis_final.csv"

    with st.sidebar:
        st.header("Model Settings")
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

    col1, col2 = st.columns(2)

    with col1:
        reason = st.selectbox("Loan Reason", reason_options)
        fico_score = st.number_input("FICO Score", min_value=300, max_value=850, value=int(fico_default), step=1)
        monthly_gross_income = st.number_input(
            "Monthly Gross Income ($)",
            min_value=0.0,
            value=float(income_default),
            step=100.0,
        )
        monthly_housing_payment = st.number_input(
            "Monthly Housing Payment ($)",
            min_value=0.0,
            value=float(housing_default),
            step=25.0,
        )

    with col2:
        requested_loan_amount = st.number_input(
            "Requested Loan Amount ($)",
            min_value=0.0,
            value=float(requested_default),
            step=500.0,
        )
        employment_status = st.selectbox("Employment Status", emp_status_options)
        employment_sector = st.selectbox("Employment Sector", emp_sector_options)
        ever_bankrupt = st.selectbox("Ever Bankrupt or Foreclose?", ["No", "Yes"])
        selected_lender = st.selectbox("Lender", lender_options)

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

        st.subheader("Prediction")
        if prediction == 1:
            st.success("Prediction: Approved")
        else:
            st.error("Prediction: Denied")

        if prob_approved is not None:
            st.write(f"Approval probability: {prob_approved:.2%}")

        st.subheader("Lender Comparison")
        comparison_rows = []
        for lender in lender_options:
            pred_class, pred_prob = predict_for_lender(raw_values, lender, model, model_feature_names)
            comparison_rows.append(
                {
                    "Lender": lender,
                    "Predicted Decision": "Approved" if pred_class == 1 else "Denied",
                    "Approval Probability": pred_prob if pred_prob is not None else float("nan"),
                }
            )

        comparison_df = pd.DataFrame(comparison_rows)
        if comparison_df["Approval Probability"].notna().any():
            comparison_df = comparison_df.sort_values(by="Approval Probability", ascending=False)

        st.dataframe(comparison_df, use_container_width=True)

        if comparison_df["Approval Probability"].notna().any():
            top_lender = comparison_df.iloc[0]["Lender"]
            top_prob = comparison_df.iloc[0]["Approval Probability"]
            st.info(f"Best lender to prioritize: {top_lender} ({top_prob:.2%} approval probability)")


if __name__ == "__main__":
    main()
