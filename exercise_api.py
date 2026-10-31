
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import streamlit as st


API_URL = "https://exercise-api.com/v1/exercises"


@st.cache_data(ttl=300, show_spinner=False)
def search_online_exercises(
    query="",
    muscle=None,
    equipment=None,
    available_equipment=None,
    limit=20,
    offset=0,
    sort="preferred_rank",
):
    """
    Search ExerciseAPI directly using its online filters.

    Results remain in the API's original format.
    Nothing is saved to the local SQLite database.
    Identical requests are cached for 5 minutes.
    """

    params = {
        "limit": max(1, min(int(limit), 200)),
        "offset": max(0, int(offset)),
        "sort": sort,
    }

    if query and query.strip():
        params["q"] = query.strip()

    if muscle:
        params["muscle"] = muscle

    if equipment:
        params["equipment"] = equipment

    if available_equipment:
        params["available_equipment"] = available_equipment

    request_url = f"{API_URL}?{urlencode(params)}"

    request = Request(
        request_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "FitnessApp-CollegeProject/1.0",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        if error.code == 429:
            raise RuntimeError(
                "ExerciseAPI request limit reached. Please try again later."
            ) from error

        raise RuntimeError(
            f"ExerciseAPI returned an HTTP error: {error.code}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            "Could not connect to ExerciseAPI. Check your internet connection."
        ) from error

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "ExerciseAPI returned an invalid response."
        ) from error

    if not isinstance(payload, dict) or not isinstance(
        payload.get("data"), list
    ):
        raise RuntimeError(
            "ExerciseAPI returned an unexpected response format."
        )

    # Return the original API response, including pagination details.
    return payload
