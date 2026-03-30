import streamlit as st
import re
import pandas as pd

# ---------------- CONFIG ----------------
BEST_TOTALS = {5: 30, 6: 24, 1: 18, 3: 15}
BAD_TOTALS = {4: -22, 8: -28, 7: -12, 9: -8, 2: -3}

GOOD_DIGITS = {'5': 8, '6': 7, '1': 5, '3': 5, '0': 4}
BAD_DIGITS = {'4': -8, '8': -10, '7': -4, '9': -3}


# ---------------- HELPERS ----------------
def digital_root(n):
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def extract_last_4_digits(car_number):
    digits = re.findall(r'\d', car_number)
    if len(digits) < 4:
        return None
    return ''.join(digits[-4:])


def life_path_number(dob):
    digits = [int(d) for d in dob if d.isdigit()]
    if not digits:
        return None
    return digital_root(sum(digits))


# ---------------- SCORING ----------------
def score_car_number(car_number, user_lp, wife_lp):
    num = extract_last_4_digits(car_number)
    if not num:
        return None

    total = sum(int(d) for d in num)
    root = digital_root(total)

    score = 50

    # root scoring
    score += BEST_TOTALS.get(root, 0)
    score += BAD_TOTALS.get(root, 0)

    # digit scoring
    for d in num:
        score += GOOD_DIGITS.get(d, 0)
        score += BAD_DIGITS.get(d, 0)

    # patterns
    if num.endswith("00"):
        score += 8

    # personal match
    if user_lp:
        if root == user_lp:
            score += 15
        elif abs(root - user_lp) == 1:
            score += 8

    # wife match
    if wife_lp:
        if root == wife_lp:
            score += 10
        elif abs(root - wife_lp) == 1:
            score += 5

    # penalties
    if num.count('4') >= 2:
        score -= 10
    if num.count('8') >= 2:
        score -= 12

    score = max(0, min(100, score))

    return {
        "Car Number": car_number,
        "Digits": num,
        "Root": root,
        "Score (%)": score
    }


# ---------------- UI ----------------
st.set_page_config(page_title="Car Number Numerology", layout="centered")

st.title("🚗 Car Number Numerology Analyzer")

st.markdown("### Enter Car Numbers (comma separated)")
numbers_input = st.text_area("Example: MH12AB2300, MH14TC1500, 5000")

st.markdown("### Enter Your Details")

col1, col2 = st.columns(2)

with col1:
    user_dob = st.text_input("Your DOB (DDMMYYYY)")

with col2:
    wife_dob = st.text_input("Wife DOB (optional)")

if st.button("Analyze 🔍"):

    numbers = [n.strip() for n in numbers_input.split(",") if n.strip()]

    if not numbers:
        st.error("Please enter at least one car number.")
    else:
        user_lp = life_path_number(user_dob)
        wife_lp = life_path_number(wife_dob) if wife_dob else None

        st.markdown("### 🔢 Numerology Insights")
        if user_lp:
            st.write(f"👤 Your Life Path Number: **{user_lp}**")
        if wife_lp:
            st.write(f"💑 Wife Life Path Number: **{wife_lp}**")

        results = []
        for n in numbers:
            res = score_car_number(n, user_lp, wife_lp)
            if res:
                results.append(res)

        if not results:
            st.error("Invalid numbers provided.")
        else:
            df = pd.DataFrame(results)
            df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
            df.index += 1

            st.markdown("### 📊 Comparison Table")
            st.dataframe(df)

            best = df.iloc[0]

            st.markdown("## ⭐ Final Recommendation")
            st.success(
                f"Choose **{best['Car Number']}** "
                f"(Score: {best['Score (%)']}%, Root: {best['Root']})"
            )
