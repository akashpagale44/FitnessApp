from database import add_exercise, get_exercise_library

EXERCISES = [
    {
        "name": "Push-Ups",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "8-15 reps",
        "description": "A bodyweight compound exercise targeting the chest, triceps and shoulders.",
        "instructions": [
            "Place your hands slightly wider than shoulder-width.",
            "Keep your body straight from head to heels.",
            "Lower your chest towards the floor in a controlled manner.",
            "Push back up without allowing your hips to sag."
        ],
        "common_mistakes": [
            "Allowing the hips to sag.",
            "Flaring the elbows excessively.",
            "Performing partial repetitions."
        ],
        "primary_muscles": ["Chest"],
        "secondary_muscles": ["Triceps", "Shoulders"]
    },
    {
        "name": "Bench Press",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "6-10 reps",
        "description": "A compound pressing exercise primarily targeting the chest.",
        "instructions": [
            "Keep your feet firmly planted on the floor.",
            "Grip the bar slightly wider than shoulder-width.",
            "Lower the bar towards your mid-chest.",
            "Press the bar upward while keeping your shoulders stable."
        ],
        "common_mistakes": [
            "Bouncing the bar off the chest.",
            "Lifting excessively heavy without a spotter.",
            "Losing control of the bar."
        ],
        "primary_muscles": ["Chest"],
        "secondary_muscles": ["Triceps", "Shoulders"]
    },
    {
        "name": "Incline Dumbbell Press",
        "equipment": "Dumbbells",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "8-12 reps",
        "description": "An incline pressing exercise emphasizing the upper chest.",
        "instructions": [
            "Set the bench at a modest incline.",
            "Hold dumbbells near your upper chest.",
            "Press the dumbbells upward with control.",
            "Lower them slowly to the starting position."
        ],
        "common_mistakes": [
            "Setting the bench at an excessively steep angle.",
            "Arching the lower back excessively.",
            "Dropping the dumbbells too quickly."
        ],
        "primary_muscles": ["Chest"],
        "secondary_muscles": ["Shoulders", "Triceps"]
    },
    {
        "name": "Lat Pulldown",
        "equipment": "Machine",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "8-12 reps",
        "description": "A vertical pulling exercise targeting the latissimus dorsi.",
        "instructions": [
            "Sit securely and adjust the thigh pad.",
            "Keep your chest lifted and torso stable.",
            "Pull the bar towards your upper chest.",
            "Return the bar slowly with control."
        ],
        "common_mistakes": [
            "Pulling the bar behind the neck.",
            "Swinging the torso excessively.",
            "Using momentum instead of controlled movement."
        ],
        "primary_muscles": ["Back"],
        "secondary_muscles": ["Biceps", "Forearms"]
    },
    {
        "name": "One-Arm Dumbbell Row",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "8-12 reps per side",
        "description": "A unilateral rowing exercise for back development.",
        "instructions": [
            "Support one hand on a bench.",
            "Keep your back neutral.",
            "Pull the dumbbell towards your hip.",
            "Lower the dumbbell in a controlled manner."
        ],
        "common_mistakes": [
            "Rotating the torso excessively.",
            "Jerking the weight upward.",
            "Rounding the back."
        ],
        "primary_muscles": ["Back"],
        "secondary_muscles": ["Biceps", "Forearms", "Traps"]
    },
    {
        "name": "Deadlift",
        "equipment": "Barbell",
        "difficulty": "Advanced",
        "recommended_sets": 3,
        "rep_range": "3-6 reps",
        "description": "A compound hip-hinge exercise involving the posterior chain.",
        "instructions": [
            "Position the bar over the middle of your feet.",
            "Hinge at the hips and grip the bar.",
            "Brace your trunk and keep the bar close to your body.",
            "Stand by driving through your feet and extending your hips.",
            "Lower the bar with control."
        ],
        "common_mistakes": [
            "Rounding the back under heavy loads.",
            "Jerking the bar off the floor.",
            "Allowing the bar to drift away from the body."
        ],
        "primary_muscles": ["Glutes", "Hamstrings"],
        "secondary_muscles": ["Lower Back", "Back", "Traps"]
    },
    {
        "name": "Dumbbell Biceps Curl",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "10-15 reps",
        "description": "An isolation exercise targeting the biceps.",
        "instructions": [
            "Stand upright holding dumbbells.",
            "Keep your elbows close to your sides.",
            "Curl the weights without swinging your body.",
            "Lower the weights slowly."
        ],
        "common_mistakes": [
            "Swinging the body to lift the weights.",
            "Moving the elbows excessively.",
            "Dropping the weights quickly."
        ],
        "primary_muscles": ["Biceps"],
        "secondary_muscles": ["Forearms"]
    },
    {
        "name": "Hammer Curl",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "10-15 reps",
        "description": "A neutral-grip curl targeting the biceps and forearm muscles.",
        "instructions": [
            "Hold dumbbells with a neutral grip.",
            "Keep your elbows close to your sides.",
            "Curl the weights while maintaining the neutral grip.",
            "Lower the weights slowly."
        ],
        "common_mistakes": [
            "Using momentum to lift the weights.",
            "Shrugging the shoulders.",
            "Allowing the elbows to move excessively."
        ],
        "primary_muscles": ["Biceps", "Forearms"],
        "secondary_muscles": []
    },
    {
        "name": "Triceps Pushdown",
        "equipment": "Cable",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "10-15 reps",
        "description": "A cable isolation exercise targeting the triceps.",
        "instructions": [
            "Stand facing the cable machine.",
            "Keep your elbows near your torso.",
            "Push the handle downward until your arms extend.",
            "Return slowly to the starting position."
        ],
        "common_mistakes": [
            "Moving the upper arms excessively.",
            "Leaning heavily over the handle.",
            "Using momentum."
        ],
        "primary_muscles": ["Triceps"],
        "secondary_muscles": []
    },
    {
        "name": "Dumbbell Shoulder Press",
        "equipment": "Dumbbells",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "8-12 reps",
        "description": "A compound overhead pressing exercise for the shoulders.",
        "instructions": [
            "Hold dumbbells at shoulder height.",
            "Brace your core and keep your torso stable.",
            "Press the dumbbells overhead.",
            "Lower them slowly to shoulder height."
        ],
        "common_mistakes": [
            "Overarching the lower back.",
            "Forcing a painful range of motion.",
            "Using excessive weight."
        ],
        "primary_muscles": ["Shoulders"],
        "secondary_muscles": ["Triceps"]
    },
    {
        "name": "Lateral Raise",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "12-20 reps",
        "description": "An isolation exercise emphasizing the lateral deltoids.",
        "instructions": [
            "Hold dumbbells beside your thighs.",
            "Maintain a slight bend in your elbows.",
            "Raise your arms sideways with control.",
            "Lower the weights without swinging."
        ],
        "common_mistakes": [
            "Using body momentum.",
            "Choosing excessively heavy weights.",
            "Shrugging the shoulders."
        ],
        "primary_muscles": ["Shoulders"],
        "secondary_muscles": ["Traps"]
    },
    {
        "name": "Squat",
        "equipment": "Barbell",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "6-10 reps",
        "description": "A compound lower-body exercise emphasizing the quadriceps and glutes.",
        "instructions": [
            "Stand with a comfortable stance.",
            "Brace your core and bend at the hips and knees.",
            "Descend to a controlled, comfortable depth.",
            "Drive through your feet to stand."
        ],
        "common_mistakes": [
            "Losing balance during the movement.",
            "Allowing the knees to collapse inward.",
            "Rushing the descent."
        ],
        "primary_muscles": ["Quadriceps"],
        "secondary_muscles": ["Glutes", "Abdominals"]
    },
    {
        "name": "Leg Press",
        "equipment": "Machine",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "10-15 reps",
        "description": "A machine-based compound exercise for the quadriceps and glutes.",
        "instructions": [
            "Keep your back supported against the seat.",
            "Place your feet securely on the platform.",
            "Lower the platform in a controlled manner.",
            "Press upward without forcefully locking your knees."
        ],
        "common_mistakes": [
            "Allowing the lower back to round.",
            "Using excessive weight.",
            "Lowering beyond a controlled range."
        ],
        "primary_muscles": ["Quadriceps"],
        "secondary_muscles": ["Glutes"]
    },
    {
        "name": "Romanian Deadlift",
        "equipment": "Dumbbells",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "8-12 reps",
        "description": "A hip-hinge exercise emphasizing the hamstrings and glutes.",
        "instructions": [
            "Stand holding dumbbells in front of your thighs.",
            "Maintain a slight bend in your knees.",
            "Push your hips backward while keeping the weights close.",
            "Stand by extending your hips."
        ],
        "common_mistakes": [
            "Rounding the back.",
            "Squatting instead of hinging at the hips.",
            "Moving the weights away from the legs."
        ],
        "primary_muscles": ["Hamstrings"],
        "secondary_muscles": ["Glutes", "Lower Back"]
    },
    {
        "name": "Calf Raise",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "12-20 reps",
        "description": "A lower-leg exercise targeting the calf muscles.",
        "instructions": [
            "Stand in a comfortable upright position.",
            "Raise your heels as high as comfortable.",
            "Pause briefly at the top.",
            "Lower your heels slowly."
        ],
        "common_mistakes": [
            "Bouncing through repetitions.",
            "Using a shortened range of motion.",
            "Moving too quickly."
        ],
        "primary_muscles": ["Calves"],
        "secondary_muscles": []
    },
    {
        "name": "Plank",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": None,
        "hold_seconds": 60,
        "description": "An isometric core exercise that develops trunk stability and endurance.",
        "instructions": [
            "Place your forearms on the floor.",
            "Extend your legs to form a straight body line.",
            "Brace your abdominals and glutes.",
            "Breathe steadily while holding the position."
        ],
        "common_mistakes": [
            "Allowing the hips to sag.",
            "Holding your breath.",
            "Raising the hips excessively."
        ],
        "primary_muscles": ["Abdominals"],
        "secondary_muscles": ["Obliques", "Glutes"]
    },
    {
        "name": "Lying Leg Raise",
        "equipment": "Bodyweight",
        "difficulty": "Intermediate",
        "recommended_sets": 3,
        "rep_range": "8-15 reps",
        "description": "A core exercise involving controlled hip flexion and abdominal stabilization.",
        "instructions": [
            "Lie on your back and brace your core.",
            "Raise your legs without swinging.",
            "Lower your legs slowly.",
            "Stop before your lower back arches excessively."
        ],
        "common_mistakes": [
            "Swinging the legs.",
            "Losing lower-back control.",
            "Dropping the legs too quickly."
        ],
        "primary_muscles": ["Abdominals"],
        "secondary_muscles": ["Obliques"]
    },
    {
        "name": "Glute Bridge",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "recommended_sets": 3,
        "rep_range": "12-15 reps",
        "description": "A hip-extension exercise emphasizing the gluteal muscles.",
        "instructions": [
            "Lie on your back with your knees bent.",
            "Keep your feet flat on the floor.",
            "Raise your hips by pressing through your feet.",
            "Lower your hips slowly."
        ],
        "common_mistakes": [
            "Overarching the lower back at the top.",
            "Using momentum.",
            "Placing the feet too far away."
        ],
        "primary_muscles": ["Glutes"],
        "secondary_muscles": ["Hamstrings"]
    }
]


if __name__ == "__main__":
    before = len(get_exercise_library())

    for exercise in EXERCISES:
        exercise["instructions"] = "\n".join(exercise["instructions"])
        exercise["common_mistakes"] = "\n".join(exercise["common_mistakes"])

        add_exercise(**exercise)

    after = len(get_exercise_library())

    print("Exercise library import completed.")
    print(f"Exercises in this import: {len(EXERCISES)}")
    print(f"Exercises already present: {before}")
    print(f"Exercises now in database: {after}")