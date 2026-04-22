# Loan Approval Streamlit App

This project contains a Streamlit app that loads a trained `.pkl` model and predicts loan approval outcomes.

## Files to Upload to GitHub

- `loanapp.py`
- `my_model.pkl`
- `requirements.txt`
- `runtime.txt`
- `loan_data_analysis_final.csv` (optional but recommended for dropdown defaults)
- `.gitignore`

## Local Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start Streamlit:
   ```bash
   streamlit run loanapp.py
   ```

## Streamlit Cloud Deployment

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, click **New app**.
3. Select your repo and branch.
4. Set **Main file path** to `loanapp.py`.
5. Deploy.

The app will use `my_model.pkl` by default when it is in the same folder as `loanapp.py`.

## Notes

- The model was trained with one-hot encoded features. The app recreates those encodings and aligns columns to the model's expected `feature_names_in_`.
- If you move the model file, update the path in the app sidebar.
