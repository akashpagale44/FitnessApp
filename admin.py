import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "fitness.db"

st.set_page_config(
    page_title="Fitness App Admin",
    page_icon="📊",
    layout="wide"
)

# Automatically refresh every 30 seconds
st_autorefresh(interval=30000, key="admin_refresh")

st.title("📊 Fitness App — Admin Dashboard")
st.caption(
    "Monitor registered users, fitness activity, and learning progress."
)
st.caption("🔄 Dashboard refreshes automatically every 30 seconds.")

if not DB_PATH.exists():
    st.error("Database not found. Check that data/fitness.db exists.")
    st.stop()


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


try:
    with sqlite3.connect(str(DB_PATH)) as connection:

        # Find all database tables
        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """,
            connection
        )["name"].tolist()

        if not tables:
            st.warning("No database tables found.")
            st.stop()

        # Count records in every table
        table_counts = {}

        for table in tables:
            table_counts[table] = pd.read_sql_query(
                f"SELECT COUNT(*) AS total FROM {quote_identifier(table)}",
                connection
            ).iloc[0]["total"]

        # Detect relevant tables by their names
        def find_table(*keywords):
            for table in tables:
                if any(word in table.lower() for word in keywords):
                    return table
            return None

        users_table = find_table("user")
        nutrition_table = find_table("nutrition", "food")
        workout_table = find_table("workout", "exercise")
        quiz_table = find_table("quiz")

        def count_for(table):
            return table_counts.get(table, 0) if table else 0

        # Overview cards
        st.subheader("📌 Overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Registered Users",
            count_for(users_table)
        )

        c2.metric(
            "Nutrition Entries",
            count_for(nutrition_table)
        )

        c3.metric(
            "Workout Entries",
            count_for(workout_table)
        )

        c4.metric(
            "Quiz Attempts",
            count_for(quiz_table)
        )

        st.divider()

        # Database activity chart
        st.subheader("📈 Database Activity")

        activity_data = pd.DataFrame({
            "Category": [
                "Users",
                "Nutrition",
                "Workouts",
                "Quiz Attempts"
            ],
            "Records": [
                count_for(users_table),
                count_for(nutrition_table),
                count_for(workout_table),
                count_for(quiz_table)
            ]
        })

        st.bar_chart(
            activity_data.set_index("Category"),
            y="Records"
        )

        st.caption(
            "Comparison of records stored in each detected category."
        )

        # Explore database records
        st.divider()
        st.subheader("🗂️ Explore Database Records")

        selected_table = st.selectbox(
            "Choose a database table",
            tables
        )

        data = pd.read_sql_query(
            f"SELECT * FROM {quote_identifier(selected_table)}",
            connection
        )

        col1, col2 = st.columns(2)

        col1.metric("Records in Selected Table", len(data))
        col2.metric("Number of Columns", len(data.columns))

        if data.empty:
            st.info("No records have been saved in this table yet.")
        else:
            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                label="⬇️ Download Selected Table as CSV",
                data=data.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_table}.csv",
                mime="text/csv"
            )

        # Summary of all database tables
        st.divider()

        with st.expander("View All Database Tables"):
            summary = pd.DataFrame({
                "Table Name": list(table_counts.keys()),
                "Total Records": list(table_counts.values())
            })

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True
            )

except Exception as error:
    st.error(f"Unable to read the database: {error}")