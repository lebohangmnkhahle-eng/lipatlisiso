# Simple web interface using Streamlit

import streamlit as st
import pandas as pd

import os
st.title("Sesotho Orthographic Normalization Evaluation")

# Get evaluator ID
if 'evaluator_id' not in st.session_state:
    st.session_state.evaluator_id = ""

evaluator_id = st.text_input("Please enter your name or ID:", value=st.session_state.evaluator_id)
st.session_state.evaluator_id = evaluator_id


# Load data
if 'eval_data' not in st.session_state:
    try:
        st.session_state.eval_data = pd.read_csv('data/human_eval_samples.csv')
        st.session_state.current_idx = 0
        st.session_state.ratings = []
    except FileNotFoundError:
        st.error("`data/human_eval_samples.csv` not found. Please run `human_evaluation.py` first.")
        st.stop()


if evaluator_id:
    df = st.session_state.eval_data
    idx = st.session_state.current_idx

    if idx < len(df):
        row = df.iloc[idx]

        st.subheader(f"Example {idx+1} of {len(df)}")

        st.write("**Source (SA Sesotho):**")
        st.write(row['source'])

        st.write("**System Output:**")
        system = st.selectbox("System", ["Rule-based", "ByT5"])
        output_column = f'pred_{system.lower().replace("-", "_")}'
        if output_column in row:
            st.write(row[output_column])
        else:
            st.warning(f"Prediction for '{system}' not found in data.")

        st.write("**Reference (Lesotho):**")
        st.write(row['target'])

        # Rating scales
        fluency = st.slider("Fluency (1-5)", 1, 5, 3, key=f"fluency_{idx}")
        adequacy = st.slider("Adequacy (1-5)", 1, 5, 3, key=f"adequacy_{idx}")
        preference = st.slider("Preference (1-5)", 1, 5, 3, key=f"preference_{idx}")

        comments = st.text_area("Comments (optional)", key=f"comments_{idx}")

        if st.button("Submit Rating"):
            st.session_state.ratings.append({
                'example_id': idx,
                'system': system,
                'fluency': fluency,
                'adequacy': adequacy,
                'preference': preference,
                'comments': comments
            })
            st.session_state.current_idx += 1
            st.rerun()
    else:
        st.success("Evaluation complete!")
        if st.button("Save Ratings"):
            os.makedirs('results', exist_ok=True)
            ratings_df = pd.DataFrame(st.session_state.ratings)
            file_path = f'results/human_eval_{evaluator_id}.csv'
            ratings_df.to_csv(file_path, index=False)
            st.write(f"Ratings saved to `{file_path}`")

else:
    st.warning("Please enter your ID to begin the evaluation.")
