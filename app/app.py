"""Persuadable: a small demo of the uplift model built in the notebooks."""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
TEST_DATA = ROOT / "data" / "test.parquet"

# Same column order the models were trained on (see notebooks/06_feature_engineering).
FEATURE_COLS = [
    "recency", "history", "mens", "womens", "newbie",
    "channel_Multichannel", "channel_Phone", "channel_Web",
    "zip_code_Rural", "zip_code_Surburban", "zip_code_Urban",
]


@st.cache_resource
def load_models():
    winner = (MODELS / "winning_model_name.txt").read_text().strip()
    model = joblib.load(MODELS / "winning_uplift_model.pkl")
    if winner == "T-Learner":
        arms = (joblib.load(MODELS / "t_learner_treatment_arm.pkl"),
                joblib.load(MODELS / "t_learner_control_arm.pkl"))
    else:
        arms = joblib.load(MODELS / "s_learner_base_estimator.pkl")
    return winner, model, arms


@st.cache_data
def test_set_scores():
    """Predicted uplift for every customer in the held-out test set, used to show where a customer ranks."""
    if not TEST_DATA.exists():
        return None
    _, model, _ = load_models()
    return model.predict(pd.read_parquet(TEST_DATA)[FEATURE_COLS])


def build_row(recency, history, mens, womens, newbie, channel, zip_code):
    """One-hot encode the form inputs into the 11 columns the model was trained on."""
    row = {col: 0 for col in FEATURE_COLS}
    row.update({"recency": recency, "history": history,
                "mens": int(mens), "womens": int(womens), "newbie": int(newbie)})
    row[f"channel_{channel}"] = 1
    row[f"zip_code_{zip_code}"] = 1
    return pd.DataFrame([row])[FEATURE_COLS]


def money(x):
    return f"-${abs(x):.2f}" if x < 0 else f"${x:.2f}"


def visit_probabilities(winner, arms, row):
    """P(visit) if emailed and if not emailed, for either model type."""
    if winner == "T-Learner":
        treatment_model, control_model = arms
        return (float(treatment_model.predict_proba(row)[0, 1]),
                float(control_model.predict_proba(row)[0, 1]))
    return (float(arms.predict_proba(row.assign(treatment=1))[0, 1]),
            float(arms.predict_proba(row.assign(treatment=0))[0, 1]))


st.set_page_config(page_title="Persuadable", layout="centered")
st.title("Persuadable: who should get the email?")
st.write("Enter a customer's details to see how much the model thinks a promotional email "
         "would change their chance of visiting the website.")

winner, model, arms = load_models()

left, right = st.columns(2)
recency = left.slider("Months since last purchase", 1, 12, 6)
history = left.number_input("Spend in the past year ($)", min_value=0.0, value=250.0, step=10.0)
mens = left.checkbox("Bought men's merchandise")
womens = left.checkbox("Bought women's merchandise")
newbie = left.checkbox("New customer (first purchase in the last 12 months)")
channel = right.selectbox("Purchase channel", ["Phone", "Web", "Multichannel"])
area = right.selectbox("Area", ["Rural", "Suburban", "Urban"])
zip_code = "Surburban" if area == "Suburban" else area  # the dataset spells it this way

st.subheader("Business assumptions")
cost = st.number_input("Cost per email ($)", min_value=0.0, value=0.10, step=0.05)
value = st.number_input("Value of one extra visit ($)", min_value=0.0, value=7.90, step=0.10)

row = build_row(recency, history, mens, womens, newbie, channel, zip_code)
p_email, p_no_email = visit_probabilities(winner, arms, row)
uplift = float(model.predict(row)[0])

st.subheader("Prediction")
c1, c2, c3 = st.columns(3)
c1.metric("Visit chance if emailed", f"{p_email:.1%}")
c2.metric("Visit chance if not emailed", f"{p_no_email:.1%}")
c3.metric("Predicted uplift", f"{uplift * 100:+.1f} pp")

net = uplift * value - cost
if net > 0:
    st.success(f"Worth emailing at these assumptions: about {money(net)} expected net value per customer.")
else:
    st.warning(f"Not worth emailing at these assumptions: about {money(net)} expected net value per customer.")

scores = test_set_scores()
if scores is not None:
    share = float((scores < uplift).mean())
    st.write(f"This customer's predicted uplift is higher than {share:.0%} of customers in the test set.")

st.info("Treat the dollar figure as a rough guide. On held-out data the model ranked customers well, "
        "but its predicted uplifts ran higher than what actually happened (customers it rated near +12 "
        "points showed about +3 points). The ranking is more reliable than the number.")
st.caption(f"Model: {winner} (XGBoost). Data: Hillstrom MineThatData email experiment, outcomes over two weeks.")

