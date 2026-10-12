
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================
# DATABASE SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "fitness.db"

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


def get_connection():
    """Connect to the existing fitness database."""
    return sqlite3.connect(DATABASE_PATH)


def initialize_quiz_database():
    """Create quiz history storage if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                attempted_at TEXT NOT NULL
            )
            """
        )


def save_quiz_score(score, total_questions):
    """Save a completed quiz attempt permanently."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO quiz_logs
                (user_id, score, total_questions, attempted_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                score,
                total_questions,
                datetime.now().isoformat(timespec="seconds")
            )
        )


def get_quiz_history():
    """Return the latest 10 quiz attempts."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT score, total_questions, attempted_at
            FROM quiz_logs
            WHERE user_id = ?
            ORDER BY attempted_at DESC, id DESC
            LIMIT 10
            """,
            connection,
            params=(user_id,)
        )


initialize_quiz_database()


# =========================
# LEARNING CENTER
# =========================

st.title("📚 Fitness Learning Center")

st.write(
    "Build your fitness knowledge with practical lessons on "
    "muscle growth, nutrition, training, recovery, and healthy habits."
)

st.info(
    "💡 Learn one topic at a time and apply what you learn "
    "to your own fitness journey."
)


# =========================
# MUSCLE BUILDING
# =========================

with st.expander("💪 Muscle Building", expanded=True):
    st.subheader("How do muscles grow?")

    st.write(
        "Resistance training challenges your muscles. With appropriate "
        "nutrition and recovery, your body adapts and can build muscle "
        "over time."
    )

    st.markdown("""
    **What you should do:**
    - Train each major muscle group consistently.
    - Use controlled movements and proper technique.
    - Gradually increase repetitions or resistance.
    - Eat enough calories and protein.
    - Get sufficient sleep and recovery.
    """)

    st.success(
        "Example: If you perform 3 sets of 8 bench-press repetitions "
        "with good technique, work toward 9 or 10 repetitions before "
        "increasing the weight."
    )


# =========================
# NUTRITION
# =========================

with st.expander("🍎 Nutrition"):
    st.subheader("Build a balanced diet")

    st.write(
        "A balanced diet supplies energy, protein, fats, carbohydrates, "
        "vitamins, minerals, and fiber."
    )

    st.markdown("""
    **Useful protein sources:**
    - Eggs and milk
    - Chicken and fish
    - Soya chunks
    - Dal, beans, and chickpeas
    - Paneer, curd, and other dairy foods

    **Other important habits:**
    - Eat fruits and vegetables regularly.
    - Include carbohydrate sources such as rice, oats, and chapati.
    - Include suitable sources of dietary fat.
    - Choose foods that fit your budget and routine.
    """)

    st.info(
        "Practical tip: You do not need expensive supplements or "
        "special foods to make progress."
    )


# =========================
# CALORIES AND MACROS
# =========================

with st.expander("⚡ Calories & Macronutrients"):
    st.subheader("Understand your food")

    st.markdown("""
    | Nutrient | Energy per gram | Main role |
    |---|---:|---|
    | Protein | 4 kcal | Muscle repair and growth |
    | Carbohydrates | 4 kcal | Energy |
    | Fat | 9 kcal | Energy and essential body functions |
    """)

    st.write(
        "Calories measure the energy supplied by food. Your energy "
        "needs depend on body size, activity, and goals."
    )

    st.markdown("**Example:**")

    st.write(
        "A meal containing 25 g protein, 60 g carbohydrates, and "
        "15 g fat provides approximately 475 kcal from these "
        "macronutrients."
    )

    st.caption(
        "Actual food-label calories can differ slightly because "
        "of rounding, fiber, and other factors."
    )


# =========================
# FAT LOSS
# =========================

with st.expander("🔥 Fat Loss"):
    st.subheader("Understand the calorie deficit")

    st.write(
        "Fat loss generally requires maintaining an energy deficit "
        "over time. This means consuming less energy than your body uses."
    )

    st.markdown("""
    - Use a moderate, sustainable calorie deficit.
    - Eat adequate protein.
    - Continue resistance training.
    - Stay physically active.
    - Monitor trends rather than individual daily weigh-ins.
    - Avoid crash diets and extreme restrictions.
    """)

    st.warning(
        "Daily body weight can change because of water, digestion, "
        "carbohydrate intake, and other normal fluctuations."
    )


# =========================
# RECOVERY
# =========================

with st.expander("😴 Recovery"):
    st.subheader("Progress happens outside the gym too")

    st.markdown("""
    - Most adults should aim for 7–9 hours of sleep.
    - Allow enough recovery between demanding sessions.
    - Increase training difficulty gradually.
    - Eat enough to support your activity.
    - Manage stress and maintain a regular schedule.
    """)

    st.write(
        "You do not need to feel sore after every workout to make progress."
    )


# =========================
# PROGRESSIVE OVERLOAD
# =========================

with st.expander("📈 Progressive Overload"):
    st.subheader("Make gradual improvements")

    st.write(
        "Progressive overload means gradually increasing the training "
        "challenge as your ability improves."
    )

    st.markdown("""
    You can progress by:
    - Performing more repetitions with the same weight.
    - Increasing resistance while maintaining good technique.
    - Improving range of motion and control.
    - Adding sets when appropriate.
    """)

    st.success(
        "Example: Complete 3 sets of 10 repetitions with good form "
        "before considering a small increase in weight."
    )


# =========================
# SUPPLEMENTS
# =========================

with st.expander("💊 Supplements"):
    st.subheader("Supplements are optional")

    st.markdown("""
    **Creatine monohydrate**
    - Can improve performance in repeated high-intensity exercise.
    - Is one of the better-studied sports supplements.

    **Protein powder**
    - Can help meet protein needs when ordinary food is insufficient.
    - Is not necessary if your diet already supplies enough protein.

    **Caffeine**
    - May improve alertness and exercise performance.
    - Can affect sleep and may cause unwanted side effects.
    """)

    st.warning(
        "Choose reputable products, follow label directions, and "
        "consider medical advice if you have a health condition or "
        "take medication. Supplements cannot replace training, food, "
        "or sleep."
    )


# =========================
# FITNESS MYTHS
# =========================

with st.expander("❌ Fitness Myths"):
    st.markdown("""
    **Myth: Ab exercises specifically burn belly fat.**

    Fact: Ab exercises strengthen the abdominal muscles, but they
    cannot selectively remove belly fat.

    ---

    **Myth: You must be sore after every workout.**

    Fact: Soreness is not required for muscle growth.

    ---

    **Myth: Eating carbohydrates automatically makes you fat.**

    Fact: Long-term changes in body fat depend largely on overall
    energy balance and other individual factors.

    ---

    **Myth: Supplements are necessary to build muscle.**

    Fact: Appropriate training, nutrition, and recovery are the foundation.
    """)


# =========================
# HYDRATION
# =========================

with st.expander("💧 Hydration"):
    st.subheader("Stay hydrated")

    st.markdown("""
    - Drink fluids regularly throughout the day.
    - Adjust intake for heat, exercise, and sweating.
    - Pay attention to thirst and your activity level.
    - For prolonged, intense exercise in hot conditions, electrolytes
      may sometimes be helpful.
    """)

    st.write(
        "Fluid requirements vary between people, so one fixed water "
        "target is not suitable for everyone."
    )


# =========================
# CONSISTENCY AND GOALS
# =========================

with st.expander("🎯 Consistency & Goal Setting"):
    st.subheader("Make your goals achievable")

    st.markdown("""
    - Set a realistic and measurable goal.
    - Follow a repeatable workout routine.
    - Track food intake when it is useful for your goal.
    - Review trends in weight and strength.
    - Adjust your plan gradually.
    - Focus on habits you can maintain.
    """)

    st.success(
        "Remember: a sustainable routine followed consistently "
        "is more useful than a perfect plan you cannot maintain."
    )


# =========================
# KNOWLEDGE CHECK
# =========================

st.divider()
st.header("🧠 Test Your Fitness Knowledge")

questions = [
    {
        "question": "1. What is the main purpose of progressive overload?",
        "options": [
            "To make every workout exhausting",
            "To gradually increase the training challenge",
            "To avoid increasing repetitions",
            "To eliminate recovery days"
        ],
        "answer": "To gradually increase the training challenge"
    },
    {
        "question": "2. Which nutrient provides 9 kcal per gram?",
        "options": [
            "Protein",
            "Carbohydrates",
            "Fat",
            "Water"
        ],
        "answer": "Fat"
    },
    {
        "question": "3. Can ab exercises selectively burn belly fat?",
        "options": [
            "Yes, every time",
            "No, spot reduction is not reliable",
            "Only when performed daily",
            "Only when using supplements"
        ],
        "answer": "No, spot reduction is not reliable"
    },
    {
        "question": "4. Which is the foundation of muscle growth?",
        "options": [
            "Supplements alone",
            "Daily soreness",
            "Resistance training, nutrition, and recovery",
            "Skipping rest days"
        ],
        "answer": "Resistance training, nutrition, and recovery"
    },
    {
        "question": "5. What should you do when body weight fluctuates daily?",
        "options": [
            "Immediately change your entire diet",
            "Stop drinking water",
            "Consider longer-term weight trends",
            "Assume every increase is fat"
        ],
        "answer": "Consider longer-term weight trends"
    }
]


with st.form("fitness_quiz"):
    answers = {}

    for index, question in enumerate(questions):
        answers[index] = st.radio(
            question["question"],
            question["options"],
            key=f"fitness_quiz_{index}"
        )

    submitted = st.form_submit_button("Check My Answers")


if submitted:
    score = sum(
        answers[index] == question["answer"]
        for index, question in enumerate(questions)
    )

    try:
        save_quiz_score(score, len(questions))
        st.metric("Your Score", f"{score} / {len(questions)}")

        if score == len(questions):
            st.success(
                "Excellent! You answered every question correctly."
            )
        elif score >= 3:
            st.info(
                "Good work! Review the topics you missed and try again."
            )
        else:
            st.info(
                "Keep learning! Revisit the lessons and try the quiz again."
            )

        st.success("Your quiz result has been saved!")

    except sqlite3.Error as error:
        st.error(f"Could not save your quiz result: {error}")


# =========================
# QUIZ HISTORY
# =========================

st.divider()
st.subheader("📊 Your Quiz History")

try:
    history = get_quiz_history()

    if history.empty:
        st.info(
            "No quiz attempts saved yet. Complete the quiz to "
            "start tracking your learning progress."
        )
    else:
        valid_history = history[
            history["total_questions"] > 0
        ].copy()

        if not valid_history.empty:
            percentages = (
                valid_history["score"]
                / valid_history["total_questions"]
                * 100
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Attempts Shown", len(valid_history))

            with col2:
                st.metric("Best Score", f"{percentages.max():.0f}%")

            display_history = valid_history.copy()

            display_history["Attempted At"] = pd.to_datetime(
                display_history["attempted_at"],
                errors="coerce"
            ).dt.strftime("%d %b %Y, %I:%M %p")

            display_history["Score"] = (
                display_history["score"].astype(str)
                + " / "
                + display_history["total_questions"].astype(str)
            )

            display_history["Percentage"] = percentages.map(
                lambda value: f"{value:.0f}%"
            )

            display_history = display_history[
                ["Attempted At", "Score", "Percentage"]
            ]

            display_history.columns = [
                "Date & Time",
                "Score",
                "Percentage"
            ]

            st.dataframe(
                display_history,
                use_container_width=True,
                hide_index=True
            )

except sqlite3.Error as error:
    st.error(f"Could not load quiz history: {error}")
