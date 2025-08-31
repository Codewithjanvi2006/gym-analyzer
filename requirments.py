import streamlit as st
import pandas as pd
import datetime as dt
from pathlib import Path

st.set_page_config(page_title="Gym Weekly Muscle Work Analyzer", page_icon="💪", layout="centered")

st.title("💪 Gym Weekly Muscle Work Analyzer")
st.write("Track which muscle groups you trained and how much work you did each week.")

DATA_PATH = Path("workouts.csv")

# ---- Exercise Database ----
EXERCISE_DB = {
    # Chest
    "Bench Press": "Chest",
    "Incline Dumbbell Press": "Chest",
    "Push-ups": "Chest",
    # Back
    "Deadlift": "Back",
    "Barbell Row": "Back",
    "Lat Pulldown": "Back",
    "Pull-ups": "Back",
    # Legs
    "Squat": "Legs",
    "Lunges": "Legs",
    "Leg Press": "Legs",
    # Shoulders
    "Overhead Press": "Shoulders",
    "Lateral Raise": "Shoulders",
    # Arms
    "Biceps Curl": "Arms",
    "Hammer Curl": "Arms",
    "Triceps Pushdown": "Arms",
    # Core
    "Plank": "Core",
    "Crunches": "Core",
}

MUSCLE_ORDER = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Core"]

def load_data():
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])
        return df
    else:
        df = pd.DataFrame(columns=["date", "exercise", "muscle_group", "sets", "reps", "weight", "volume"])
        df.to_csv(DATA_PATH, index=False)
        return df

def save_entry(entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
    return df

def compute_volume(sets, reps, weight):
    if weight <= 0:
        weight = 1  # bodyweight exercise
    return sets * reps * weight

# ---- Input Form ----
with st.expander("➕ Add Workout Entry", expanded=True):
    d = st.date_input("Date", dt.date.today())
    ex = st.selectbox("Exercise", sorted(EXERCISE_DB.keys()))
    col1, col2, col3 = st.columns(3)
    with col1:
        sets = st.number_input("Sets", min_value=1, max_value=20, value=3, step=1)
    with col2:
        reps = st.number_input("Reps", min_value=1, max_value=100, value=10, step=1)
    with col3:
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=0.0, step=0.5)

    if st.button("Save Entry"):  
        mg = EXERCISE_DB.get(ex, "Other")  
        vol = compute_volume(int(sets), int(reps), float(weight))  
        entry = {  
            "date": pd.to_datetime(d),  
            "exercise": ex,  
            "muscle_group": mg,  
            "sets": int(sets),  
            "reps": int(reps),  
            "weight": float(weight),  
            "volume": float(vol),  
        }  
        df = save_entry(entry)  
        st.success(f"Saved: {ex} on {d} → {mg}, volume={vol:.0f}")

st.divider()

# ---- Analysis ----
df = load_data()
if df.empty:
    st.info("No data yet. Add a workout entry above.")
else:
    st.subheader("📅 Weekly Summary")
    today = dt.date.today()
    start_date = st.date_input("Start date", today - dt.timedelta(days=6))
    end_date = st.date_input("End date", today)
    mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    wdf = df.loc[mask].copy()

    if wdf.empty:  
        st.warning("No entries in the selected date range.")  
    else:  
        agg = wdf.groupby("muscle_group", as_index=False)["volume"].sum()  
        agg["muscle_group"] = pd.Categorical(agg["muscle_group"], categories=MUSCLE_ORDER, ordered=True)  
        agg = agg.sort_values("muscle_group")  

        st.write("**Total Volume by Muscle Group**")  
        st.dataframe(agg)  

        # Plot bar chart  
  
        
       
        # Suggestions  
        max_vol = agg["volume"].max()  
        threshold = 0.2 * max_vol if max_vol > 0 else 0  
        neglected = agg[agg["volume"] < threshold]["muscle_group"].astype(str).tolist()  

        st.subheader("🤖 Smart Suggestions")  
        if len(neglected) == 0:  
            st.success("Great balance! No muscle group looks neglected this week.")  
        else:  
            st.warning("You might be neglecting: *" + ", ".join(neglected) + "*")  
