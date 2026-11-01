from database import add_exercise, get_exercise_library

EXERCISES = [
    ("Incline Barbell Bench Press", "Barbell", "Intermediate", ["Chest"], ["Shoulders", "Triceps"], "Upper chest pressing exercise."),
    ("Decline Bench Press", "Barbell", "Intermediate", ["Chest"], ["Triceps"], "Decline pressing variation for chest development."),
    ("Chest Fly", "Dumbbells", "Beginner", ["Chest"], ["Shoulders"], "Isolation exercise for the chest."),
    ("Cable Chest Fly", "Cable", "Beginner", ["Chest"], ["Shoulders"], "Cable isolation exercise for chest."),
    ("Chest Dip", "Bodyweight", "Intermediate", ["Chest", "Triceps"], ["Shoulders"], "Compound bodyweight pushing exercise."),
    ("Pec Deck", "Machine", "Beginner", ["Chest"], [], "Machine-based chest isolation exercise."),
    ("Pull-Ups", "Bodyweight", "Intermediate", ["Back"], ["Biceps", "Forearms"], "Vertical pulling bodyweight exercise."),
    ("Chin-Ups", "Bodyweight", "Intermediate", ["Back", "Biceps"], ["Forearms"], "Underhand-grip vertical pulling exercise."),
    ("Seated Cable Row", "Cable", "Beginner", ["Back"], ["Biceps", "Forearms"], "Horizontal cable rowing exercise."),
    ("Barbell Bent-Over Row", "Barbell", "Intermediate", ["Back"], ["Biceps", "Forearms", "Traps"], "Compound horizontal pulling exercise."),
    ("T-Bar Row", "Machine", "Intermediate", ["Back"], ["Biceps", "Traps"], "Supported or landmine rowing variation."),
    ("Straight-Arm Pulldown", "Cable", "Beginner", ["Back"], ["Shoulders"], "Cable exercise emphasizing the lats."),
    ("Face Pull", "Cable", "Beginner", ["Shoulders", "Traps"], ["Back"], "Cable pulling exercise for rear shoulders."),
    ("Reverse Pec Deck", "Machine", "Beginner", ["Shoulders"], ["Traps"], "Machine exercise for rear deltoids."),
    ("Front Raise", "Dumbbells", "Beginner", ["Shoulders"], [], "Shoulder isolation exercise emphasizing front deltoids."),
    ("Arnold Press", "Dumbbells", "Intermediate", ["Shoulders"], ["Triceps"], "Rotating dumbbell overhead press."),
    ("Preacher Curl", "Barbell", "Beginner", ["Biceps"], ["Forearms"], "Supported biceps curl variation."),
    ("Concentration Curl", "Dumbbells", "Beginner", ["Biceps"], [], "Single-arm biceps isolation exercise."),
    ("Cable Biceps Curl", "Cable", "Beginner", ["Biceps"], ["Forearms"], "Cable-based biceps curl."),
    ("EZ-Bar Curl", "EZ Bar", "Beginner", ["Biceps"], ["Forearms"], "Curl variation using an EZ bar."),
    ("Overhead Triceps Extension", "Dumbbells", "Beginner", ["Triceps"], [], "Overhead triceps isolation exercise."),
    ("Skull Crushers", "EZ Bar", "Intermediate", ["Triceps"], [], "Lying triceps extension exercise."),
    ("Close-Grip Bench Press", "Barbell", "Intermediate", ["Triceps"], ["Chest", "Shoulders"], "Narrow-grip compound pressing exercise."),
    ("Diamond Push-Ups", "Bodyweight", "Intermediate", ["Triceps"], ["Chest", "Shoulders"], "Close-hand push-up variation."),
    ("Goblet Squat", "Dumbbells", "Beginner", ["Quadriceps"], ["Glutes"], "Front-loaded squat variation."),
    ("Bulgarian Split Squat", "Dumbbells", "Intermediate", ["Quadriceps", "Glutes"], ["Hamstrings"], "Single-leg squat variation."),
    ("Leg Extension", "Machine", "Beginner", ["Quadriceps"], [], "Machine-based quadriceps isolation exercise."),
    ("Seated Leg Curl", "Machine", "Beginner", ["Hamstrings"], [], "Machine-based hamstring curl."),
    ("Lying Leg Curl", "Machine", "Beginner", ["Hamstrings"], [], "Lying machine hamstring curl."),
    ("Hip Thrust", "Barbell", "Intermediate", ["Glutes"], ["Hamstrings"], "Loaded hip extension exercise."),
    ("Standing Calf Raise", "Machine", "Beginner", ["Calves"], [], "Standing calf isolation exercise."),
    ("Seated Calf Raise", "Machine", "Beginner", ["Calves"], [], "Seated calf exercise emphasizing soleus."),
    ("Russian Twist", "Bodyweight", "Beginner", ["Obliques"], ["Abdominals"], "Rotational core exercise."),
    ("Crunches", "Bodyweight", "Beginner", ["Abdominals"], [], "Basic abdominal flexion exercise."),
    ("Hanging Knee Raise", "Bodyweight", "Intermediate", ["Abdominals"], ["Forearms"], "Hanging core exercise.")
]

before = len(get_exercise_library())

for name, equipment, difficulty, primary, secondary, description in EXERCISES:
    add_exercise(
        name=name,
        equipment=equipment,
        difficulty=difficulty,
        recommended_sets=3,
        rep_range="8-12 reps",
        description=description,
        instructions="Perform the movement with controlled technique and a comfortable range of motion.",
        common_mistakes="Using excessive weight; rushing repetitions; losing control of the movement.",
        primary_muscles=primary,
        secondary_muscles=secondary
    )

after = len(get_exercise_library())

print("Exercise library expansion completed.")
print("New entries attempted:", len(EXERCISES))
print("Exercises before:", before)
print("Exercises after:", after)
print("New exercises added:", after - before)
