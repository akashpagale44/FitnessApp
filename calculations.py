
def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation."""
    gender = str(gender).strip().lower()

    if gender in ("male", "m"):
        return round(10 * weight + 6.25 * height - 5 * age + 5)
    elif gender in ("female", "f"):
        return round(10 * weight + 6.25 * height - 5 * age - 161)
    else:
        return round(10 * weight + 6.25 * height - 5 * age + 5)


def calculate_tdee(bmr, activity_level):
    """Estimate daily calorie expenditure based on activity level."""
    activity_level = str(activity_level).strip().lower()

    activity_multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9,
    }

    multiplier = activity_multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier)


def calculate_calorie_target(tdee, fitness_goal):
    """Estimate daily calorie target based on the fitness goal."""
    goal = str(fitness_goal).strip().lower()

    if goal in ("build muscle", "muscle gain", "gain muscle", "bulk"):
        return round(tdee + 250)

    elif goal in ("lose weight", "weight loss", "fat loss", "cut"):
        return round(tdee - 400)

    else:
        return round(tdee)


def calculate_protein_target(weight, fitness_goal=None):
    """Estimate daily protein target in grams."""
    if fitness_goal is None:
        return round(weight * 1.6)

    goal = str(fitness_goal).strip().lower()

    if goal in ("build muscle", "muscle gain", "gain muscle", "bulk"):
        return round(weight * 1.8)

    elif goal in ("lose weight", "weight loss", "fat loss", "cut"):
        return round(weight * 2.0)

    else:
        return round(weight * 1.6)

