import streamlit as st
import re
import pandas as pd

# =========================================================
# CONFIG
# =========================================================
BEST_TOTALS = {5: 30, 6: 24, 1: 18, 3: 15}
BAD_TOTALS = {4: -22, 8: -28, 7: -12, 9: -8, 2: -3}

GOOD_DIGITS = {'5': 8, '6': 7, '1': 5, '3': 5, '0': 4}
BAD_DIGITS = {'4': -8, '8': -10, '7': -4, '9': -3}


# =========================================================
# HELPERS
# =========================================================
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


def is_ascending(num):
    return list(num) == sorted(num)


def is_descending(num):
    return list(num) == sorted(num, reverse=True)


def is_balanced(num):
    return num == num[::-1] or (num[0] == num[3] and num[1] == num[2])


def has_zero_finish(num):
    return num.endswith("00") or num.endswith("0")


def count_repeats(num):
    freq = {}
    for d in num:
        freq[d] = freq.get(d, 0) + 1
    return freq


def sequence_smoothness(num):
    jumps = [abs(int(num[i]) - int(num[i+1])) for i in range(len(num)-1)]
    avg_jump = sum(jumps) / len(jumps)

    if avg_jump <= 1.5:
        return 12, f"Smooth digit flow (avg jump {avg_jump:.2f})"
    elif avg_jump <= 3:
        return 6, f"Moderately smooth flow (avg jump {avg_jump:.2f})"
    elif avg_jump <= 5:
        return -3, f"Jerky sequence flow (avg jump {avg_jump:.2f})"
    else:
        return -8, f"Very rough sequence flow (avg jump {avg_jump:.2f})"


# =========================================================
# VERSION 1 / BASE ENGINE
# =========================================================
def detailed_score_car_number(car_number):
    num = extract_last_4_digits(car_number)
    if not num:
        return None

    total = sum(int(d) for d in num)
    root = digital_root(total)

    score = 50
    reasons = []

    # 1. Root scoring
    if root in BEST_TOTALS:
        score += BEST_TOTALS[root]
        reasons.append(f"Excellent root total {root}")
    elif root in BAD_TOTALS:
        score += BAD_TOTALS[root]
        reasons.append(f"Weak / avoid root total {root}")
    else:
        reasons.append(f"Neutral root total {root}")

    # 2. Digit scoring
    for d in num:
        score += GOOD_DIGITS.get(d, 0)
        score += BAD_DIGITS.get(d, 0)

    good_count = sum(1 for d in num if d in GOOD_DIGITS)
    bad_count = sum(1 for d in num if d in BAD_DIGITS)

    if good_count > bad_count:
        reasons.append(f"Contains more supportive digits ({good_count} good vs {bad_count} harsh)")
    elif bad_count > good_count:
        reasons.append(f"Contains more harsh digits ({bad_count} harsh vs {good_count} supportive)")
    else:
        reasons.append("Digit quality is balanced")

    # 3. Repeats
    repeats = count_repeats(num)
    if repeats.get('4', 0) >= 2:
        score -= 12
        reasons.append("Repeated 4 detected (not ideal for vehicles)")
    if repeats.get('8', 0) >= 2:
        score -= 15
        reasons.append("Repeated 8 detected (heavy vehicle energy)")
    if repeats.get('5', 0) >= 2:
        score += 10
        reasons.append("Repeated 5 detected (excellent movement energy)")
    if repeats.get('6', 0) >= 2:
        score += 8
        reasons.append("Repeated 6 detected (good family comfort energy)")

    # 4. Sequence smoothness
    seq_score, seq_reason = sequence_smoothness(num)
    score += seq_score
    reasons.append(seq_reason)

    if is_ascending(num):
        score += 8
        reasons.append("Ascending pattern detected (good flow)")
    elif is_descending(num):
        score += 4
        reasons.append("Descending pattern detected (acceptable flow)")

    if is_balanced(num):
        score += 7
        reasons.append("Balanced / mirror-like structure detected")

    if has_zero_finish(num):
        score += 8
        reasons.append("Zero-finish pattern gives premium and stable feel")

    # 5. Collision combos
    if '4' in num and '8' in num:
        score -= 12
        reasons.append("4 + 8 combination present (energetically rough)")
    if '7' in num and '8' in num:
        score -= 8
        reasons.append("7 + 8 combination present (detached + heavy)")

    # 6. Premium structure
    if re.match(r'^[1-6][0-9]00$', num):
        score += 10
        reasons.append("Premium clean pattern (XY00 style)")
    elif re.match(r'^[1-6]500$', num):
        score += 8
        reasons.append("Strong premium family/movement structure")

    score = max(0, min(100, score))

    if score >= 85:
        decision = "BUY IT ✅"
    elif score >= 70:
        decision = "GOOD / SAFE TO BUY 👍"
    elif score >= 55:
        decision = "CONSIDER IF YOU REALLY LIKE IT 🤔"
    else:
        decision = "AVOID ❌"

    return {
        "Car Number": car_number,
        "Digits": num,
        "Digit Sum": total,
        "Root": root,
        "Score (%)": score,
        "Decision": decision,
        "Reasons": reasons
    }


# =========================================================
# VERSION 2 - MULTI COMPARE
# =========================================================
def simple_compare_score(car_number):
    result = detailed_score_car_number(car_number)
    if not result:
        return None
    return {
        "Car Number": result["Car Number"],
        "Digits": result["Digits"],
        "Root": result["Root"],
        "Score (%)": result["Score (%)"],
        "Decision": result["Decision"]
    }


# =========================================================
# VERSION 3 - ADVANCED MATCHING
# =========================================================
def advanced_score_car_number(car_number, user_lp=None, wife_lp=None):
    base = detailed_score_car_number(car_number)
    if not base:
        return None

    score = base["Score (%)"]
    root = base["Root"]
    reasons = list(base["Reasons"])

    user_match = "No"
    wife_match = "No"

    # Personal match
    if user_lp:
        if root == user_lp:
            score += 15
            user_match = "Strong"
            reasons.append(f"Strong personal DOB match (Root {root} = Your Life Path {user_lp})")
        elif abs(root - user_lp) == 1:
            score += 8
            user_match = "Good"
            reasons.append(f"Good personal DOB compatibility (Root {root} near Your Life Path {user_lp})")
        else:
            user_match = "Weak"

    # Wife match
    if wife_lp:
        if root == wife_lp:
            score += 10
            wife_match = "Strong"
            reasons.append(f"Strong wife compatibility (Root {root} = Wife Life Path {wife_lp})")
        elif abs(root - wife_lp) == 1:
            score += 5
            wife_match = "Good"
            reasons.append(f"Good wife compatibility (Root {root} near Wife Life Path {wife_lp})")
        else:
            wife_match = "Weak"

    score = max(0, min(100, score))

    if score >= 90:
        final_tag = "EXCELLENT PICK ⭐"
    elif score >= 80:
        final_tag = "VERY GOOD PICK ✅"
    elif score >= 65:
        final_tag = "DECENT OPTION 👍"
    else:
        final_tag = "NOT RECOMMENDED ❌"

    return {
        "Car Number": base["Car Number"],
        "Digits": base["Digits"],
        "Root": root,
        "Base Score (%)": base["Score (%)"],
        "Final Score (%)": score,
        "Your Match": user_match,
        "Wife Match": wife_match,
        "Recommendation": final_tag,
        "Reasons": reasons
    }


# =========================================================
# UI
# =========================================================
st.set_page_config(page_title="Car Number Numerology Analyzer", layout="wide")

st.title("🚗 Car Number Numerology Analyzer")
st.markdown("### Analyze, compare, and choose the best car number plate")

tab1, tab2, tab3 = st.tabs([
    "🔍 Single Number Checker",
    "📊 Compare Multiple Numbers",
    "💑 Advanced DOB Matching"
])

# =========================================================
# TAB 1 - SINGLE CHECKER
# =========================================================
with tab1:
    st.subheader("Single Car Number Analysis")
    st.write("Check whether a single car number is worth buying based on numerology.")

    single_number = st.text_input("Enter car number", placeholder="e.g. MH12AB2300 or 2300", key="single")

    if st.button("Analyze Single Number", key="single_btn"):
        result = detailed_score_car_number(single_number)

        if not result:
            st.error("Please enter a valid car number with at least 4 digits.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Digits", result["Digits"])
            col2.metric("Root", result["Root"])
            col3.metric("Score", f"{result['Score (%)']}%")

            st.markdown(f"## {result['Decision']}")

            st.markdown("### Details")
            st.write(f"**Digit Sum:** {result['Digit Sum']}")

            st.markdown("### Reasons")
            for r in result["Reasons"]:
                st.write(f"- {r}")

# =========================================================
# TAB 2 - MULTI COMPARE
# =========================================================
with tab2:
    st.subheader("Compare Up to 10 Car Numbers")
    st.write("Compare multiple numbers and sort them from best to worst.")

    compare_input = st.text_area(
        "Enter car numbers (comma separated)",
        placeholder="e.g. MH12AB2300, MH14TC1500, 5000, 8440",
        key="compare"
    )

    if st.button("Compare Numbers", key="compare_btn"):
        numbers = [n.strip() for n in compare_input.split(",") if n.strip()]
        numbers = numbers[:10]

        if not numbers:
            st.error("Please enter at least one valid car number.")
        else:
            results = []
            for n in numbers:
                r = simple_compare_score(n)
                if r:
                    results.append(r)

            if not results:
                st.error("No valid numbers found.")
            else:
                df = pd.DataFrame(results)
                df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
                df.index += 1

                st.markdown("### Ranked Comparison Table")
                st.dataframe(df, use_container_width=True)

                best = df.iloc[0]
                st.success(
                    f"🏆 Best Option: **{best['Car Number']}** "
                    f"(Score: {best['Score (%)']}%, Root: {best['Root']})"
                )

# =========================================================
# TAB 3 - ADVANCED MATCHING
# =========================================================
with tab3:
    st.subheader("Advanced Numerology Matching")
    st.write("Compare car numbers with your DOB and wife compatibility.")

    advanced_numbers = st.text_area(
        "Enter car numbers (comma separated)",
        placeholder="e.g. MH12AB2300, MH14TC1500, 5000, 8440",
        key="advanced"
    )

    col1, col2 = st.columns(2)
    with col1:
        user_dob = st.text_input("Your DOB", placeholder="DDMMYYYY", key="user_dob")
    with col2:
        wife_dob = st.text_input("Wife DOB (optional)", placeholder="DDMMYYYY", key="wife_dob")

    if st.button("Run Advanced Analysis", key="advanced_btn"):
        numbers = [n.strip() for n in advanced_numbers.split(",") if n.strip()]
        numbers = numbers[:10]

        if not numbers:
            st.error("Please enter at least one valid car number.")
        else:
            user_lp = life_path_number(user_dob)
            wife_lp = life_path_number(wife_dob) if wife_dob else None

            info_col1, info_col2 = st.columns(2)
            if user_lp:
                info_col1.info(f"👤 Your Life Path Number: **{user_lp}**")
            else:
                info_col1.warning("👤 Your DOB missing / invalid")

            if wife_lp:
                info_col2.info(f"💑 Wife Life Path Number: **{wife_lp}**")
            else:
                info_col2.warning("💑 Wife DOB not provided / invalid")

            results = []
            for n in numbers:
                r = advanced_score_car_number(n, user_lp, wife_lp)
                if r:
                    results.append(r)

            if not results:
                st.error("No valid numbers found.")
            else:
                df = pd.DataFrame(results)
                df = df.sort_values(by="Final Score (%)", ascending=False).reset_index(drop=True)
                df.index += 1

                st.markdown("### Advanced Comparison Table")
                st.dataframe(df[[
                    "Car Number",
                    "Digits",
                    "Root",
                    "Base Score (%)",
                    "Final Score (%)",
                    "Your Match",
                    "Wife Match",
                    "Recommendation"
                ]], use_container_width=True)

                best = df.iloc[0]

                st.markdown("## ⭐ Final Recommendation")
                st.success(
                    f"Choose **{best['Car Number']}** "
                    f"(Final Score: {best['Final Score (%)']}%, Root: {best['Root']})"
                )

                with st.expander("See Why This Number Was Chosen"):
                    for reason in best["Reasons"]:
                        st.write(f"- {reason}")
