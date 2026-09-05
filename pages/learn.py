import streamlit as st


st.title("📚 Learn")

st.write(
    "Learn the basics of fitness, nutrition, recovery, and healthy training."
)


# -------------------------
# Muscle Building
# -------------------------

with st.expander("💪 Muscle Building"):

    st.write("""
    Muscle growth happens when you consistently train your muscles,
    eat enough protein and calories, and recover properly.

    **Key points:**
    - Perform resistance training regularly.
    - Gradually increase reps, weight, or training difficulty.
    - Consume enough protein throughout the day.
    - Get enough sleep and recovery.
    """)


# -------------------------
# Nutrition
# -------------------------

with st.expander("🍎 Nutrition"):

    st.write("""
    A balanced diet provides the energy and nutrients needed for training
    and recovery.

    **Key points:**
    - Eat enough calories for your goal.
    - Include protein-rich foods.
    - Eat fruits and vegetables regularly.
    - Drink enough water.
    - Choose mostly nutritious, minimally processed foods.
    """)


# -------------------------
# Fat Loss
# -------------------------

with st.expander("🔥 Fat Loss"):

    st.write("""
    Fat loss mainly depends on maintaining a calorie deficit over time.

    **Key points:**
    - Consume fewer calories than you use.
    - Keep protein intake adequate.
    - Continue resistance training.
    - Stay physically active.
    - Focus on long-term consistency rather than extreme diets.
    """)


# -------------------------
# Recovery
# -------------------------

with st.expander("😴 Recovery"):

    st.write("""
    Recovery is an important part of making progress.

    **Key points:**
    - Aim for around 7–9 hours of sleep.
    - Give muscles enough time to recover.
    - Manage training volume and intensity.
    - Stay hydrated.
    - Take rest days when needed.
    """)


# -------------------------
# Supplements
# -------------------------

with st.expander("💊 Supplements"):

    st.write("""
    Supplements can support a good diet, but they are not a replacement
    for proper nutrition and training.

    **Common examples:**
    - Creatine monohydrate
    - Protein powder
    - Caffeine

    Supplements should be considered based on individual needs and
    should not replace a balanced diet.
    """)


# -------------------------
# Fitness Myths
# -------------------------

with st.expander("❌ Fitness Myths"):

    st.write("""
    **Myth:** You can lose fat from one specific body part.

    **Fact:** Fat loss occurs across the body and cannot be precisely
    controlled by exercising one area.

    **Myth:** More exercise always means better results.

    **Fact:** Training, nutrition, recovery, and consistency all matter.

    **Myth:** Supplements are necessary to build muscle.

    **Fact:** Consistent training and adequate nutrition are the foundation
    of muscle growth.
    """)