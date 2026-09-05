def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate (BMR)
    using the Mifflin-St Jeor equation.
    """

    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    return round(bmr)

def get_activity_multiplier(activity_level):
    """Return the activity multiplier."""

    multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }

    return multipliers.get(activity_level, 1.2)

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure (TDEE)."""

    multiplier = get_activity_multiplier(activity_level)

    tdee = bmr * multiplier

    return round(tdee)

def calculate_calorie_target(tdee, fitness_goal):
    """Calculate daily calorie target based on the fitness goal."""

    if fitness_goal == "Lose Fat":
        calories = tdee - 400

    elif fitness_goal == "Build Muscle":
        calories = tdee + 250

    else:
        calories = tdee

    return round(calories)

def calculate_protein_target(weight):
    """Calculate daily protein target based on body weight."""

    protein = weight * 1.6

    return round(protein)
