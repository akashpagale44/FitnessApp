
import streamlit as st

from database import get_exercise_library, get_all_exercise_muscles
from exercise_api import search_online_exercises


st.set_page_config(
    page_title="Exercise Library",
    page_icon="🏋️",
    layout="wide",
)

st.title("🏋️ Exercise Library")
st.write(
    "Search exercises, learn proper technique, and discover "
    "the primary and secondary muscles they train."
)


# =========================================================
# PART 1: EXISTING LOCAL EXERCISE LIBRARY
# =========================================================

st.header("Local Exercise Library")
st.caption("Exercises stored in your Fitness App database.")

exercises = get_exercise_library()
all_muscle_rows = get_all_exercise_muscles()

muscles_by_exercise = {}
for row in all_muscle_rows:
    muscles_by_exercise.setdefault(row["exercise_id"], []).append(row)

exercise_data = []

for exercise in exercises:
    item = dict(exercise)
    muscle_rows = muscles_by_exercise.get(item["id"], [])

    item["primary_muscles"] = [
        row["name"] for row in muscle_rows
        if row["role"] == "primary"
    ]

    item["secondary_muscles"] = [
        row["name"] for row in muscle_rows
        if row["role"] == "secondary"
    ]

    item["all_muscles"] = (
        item["primary_muscles"] + item["secondary_muscles"]
    )

    exercise_data.append(item)

st.subheader("Find an exercise")

search = st.text_input(
    "Search by exercise, muscle, or equipment",
    placeholder="Try lateral raise, chest, or dumbbells",
).strip().lower()

all_muscles = sorted({
    muscle
    for exercise in exercise_data
    for muscle in exercise["all_muscles"]
})

all_equipment = sorted({
    exercise["equipment"] for exercise in exercise_data
})

all_levels = sorted({
    exercise["difficulty"] for exercise in exercise_data
})

col1, col2, col3 = st.columns(3)

with col1:
    muscle_filter = st.selectbox(
        "Muscle group",
        ["All"] + all_muscles,
    )

with col2:
    equipment_filter = st.selectbox(
        "Equipment",
        ["All"] + all_equipment,
    )

with col3:
    level_filter = st.selectbox(
        "Difficulty",
        ["All"] + all_levels,
    )


filtered = []

for exercise in exercise_data:
    search_text = " ".join([
        exercise["name"],
        exercise["equipment"],
        exercise["difficulty"],
        " ".join(exercise["all_muscles"]),
        exercise["description"] or "",
    ]).lower()

    matches_search = search in search_text

    matches_muscle = (
        muscle_filter == "All"
        or muscle_filter in exercise["all_muscles"]
    )

    matches_equipment = (
        equipment_filter == "All"
        or exercise["equipment"] == equipment_filter
    )

    matches_level = (
        level_filter == "All"
        or exercise["difficulty"] == level_filter
    )

    if (
        matches_search
        and matches_muscle
        and matches_equipment
        and matches_level
    ):
        filtered.append(exercise)


st.caption(f"{len(filtered)} local exercises found")

if not filtered:
    st.info("No matching local exercises found.")

for exercise in filtered:
    primary = ", ".join(exercise["primary_muscles"]) or "Not specified"
    secondary = ", ".join(exercise["secondary_muscles"]) or "Not specified"

    with st.expander(exercise["name"]):
        col_a, col_b, col_c = st.columns(3)

        col_a.metric("Equipment", exercise["equipment"])
        col_b.metric("Difficulty", exercise["difficulty"])
        col_c.metric(
            "Suggested sets",
            str(exercise["recommended_sets"] or "—"),
        )

        st.markdown(f"**Primary muscles:** {primary}")
        st.markdown(f"**Secondary muscles:** {secondary}")

        if exercise["description"]:
            st.write(exercise["description"])

        if exercise["hold_seconds"]:
            st.markdown(
                f"**Suggested hold:** {exercise['hold_seconds']} seconds"
            )
        elif exercise["rep_range"]:
            st.markdown(
                f"**Suggested repetitions:** {exercise['rep_range']}"
            )

        if exercise["instructions"]:
            st.markdown("**How to perform the exercise**")

            for number, step in enumerate(
                exercise["instructions"].splitlines(),
                start=1,
            ):
                if step.strip():
                    st.write(f"{number}. {step.strip()}")

        if exercise["common_mistakes"]:
            st.markdown("**Common mistakes**")

            for mistake in exercise["common_mistakes"].splitlines():
                if mistake.strip():
                    st.write(f"- {mistake.strip()}")


# =========================================================
# PART 2: LIVE ONLINE EXERCISE EXPLORER
# =========================================================

st.divider()
st.header("Online Exercise Explorer")
st.write(
    "Search the ExerciseAPI online database. "
    "These results are fetched directly from the online service "
    "and are not saved in your local database."
)

online_col1, online_col2 = st.columns(2)

with online_col1:
    online_query = st.text_input(
        "Exercise name",
        placeholder="Try bench press or squat",
        key="online_exercise_query",
    ).strip()

with online_col2:
    online_muscle = st.text_input(
        "Primary muscle filter",
        placeholder="Example: chest, biceps, lower_back",
        key="online_exercise_muscle",
    ).strip().lower()

online_equipment = st.text_input(
    "Equipment filter",
    placeholder="Example: dumbbells, barbell, cables",
    key="online_exercise_equipment",
).strip().lower()


# Reset pagination when the search or filters change.
current_signature = (
    online_query,
    online_muscle,
    online_equipment,
)

if st.session_state.get("online_search_signature") != current_signature:
    st.session_state["online_search_signature"] = current_signature
    st.session_state["online_exercise_offset"] = 0

offset = st.session_state.get("online_exercise_offset", 0)
page_size = 20

if online_query or online_muscle or online_equipment:
    try:
        with st.spinner("Searching the online exercise database..."):
            online_result = search_online_exercises(
                query=online_query,
                muscle=online_muscle or None,
                equipment=online_equipment or None,
                limit=page_size,
                offset=offset,
                sort="preferred_rank",
            )

        online_exercises = online_result["data"]
        total_online = online_result["total"]

        st.caption(
            f"Showing {len(online_exercises)} results on this page. "
            f"Total matching online exercises: {total_online}"
        )

        if not online_exercises:
            st.info(
                "No online exercises matched your search. "
                "Try changing the search or filters."
            )

        for exercise in online_exercises:
            name = exercise.get("name", "Unnamed exercise")

            with st.expander(name):
                primary = exercise.get("primary_muscle") or "Not specified"
                secondary = exercise.get("secondary_muscles") or []
                equipment = exercise.get("equipment") or []

                col_a, col_b, col_c = st.columns(3)

                col_a.metric("Primary muscle", primary.replace("_", " ").title())

                col_b.metric(
                    "Movement pattern",
                    (exercise.get("pattern") or "Not specified")
                    .replace("_", " ").title(),
                )

                col_c.metric(
                    "Training category",
                    (exercise.get("modality") or "Not specified").title(),
                )

                st.markdown(
                    "**Secondary muscles:** "
                    + (
                        ", ".join(
                            muscle.replace("_", " ").title()
                            for muscle in secondary
                        )
                        if secondary else "Not specified"
                    )
                )

                st.markdown(
                    "**Equipment:** "
                    + (
                        ", ".join(
                            item.replace("_", " ").title()
                            for item in equipment
                        )
                        if equipment else "Not specified"
                    )
                )

                rep_low = exercise.get("default_rep_low")
                rep_high = exercise.get("default_rep_high")

                if rep_low is not None and rep_high is not None:
                    st.markdown(
                        f"**Suggested repetitions:** {rep_low}–{rep_high}"
                    )

                if exercise.get("sfr_class"):
                    st.markdown(
                        f"**Stimulus-to-fatigue category:** "
                        f"{exercise['sfr_class'].title()}"
                    )

                if exercise.get("tier"):
                    st.markdown(
                        f"**Exercise tier:** {exercise['tier'].title()}"
                    )

                if exercise.get("is_gold_standard"):
                    st.success("Marked as a gold-standard exercise by the API.")

                if exercise.get("cues"):
                    st.markdown("**Coaching cues**")
                    st.write(exercise["cues"])

                st.caption(f"Online exercise ID: {exercise.get('id', 'N/A')}")

        # Load more results from the online API.
        if offset + len(online_exercises) < total_online:
            if st.button("Load More Online Exercises"):
                st.session_state["online_exercise_offset"] = (
                    offset + page_size
                )
                st.rerun()

    except Exception as error:
        st.error(f"Could not load online exercises: {error}")
else:
    st.info("Enter an exercise name, muscle, or equipment above to search the online database.")

st.divider()

st.caption(
    "Start with a manageable weight and controlled technique. "
    "These are general training suggestions, not personalised prescriptions. "
    "Stop if you experience sharp or unusual pain."
)

st.caption(
    "Online exercise data by ExerciseAPI "
    "(https://exercise-api.com), licensed under CC BY 4.0."
)
