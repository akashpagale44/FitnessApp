from database import get_connection

GUIDANCE = {
"Incline Barbell Bench Press": (
["Set the bench to a 30–45 degree incline.",
 "Plant your feet firmly and grip the bar slightly wider than shoulder-width.",
 "Lower the bar under control toward your upper chest.",
 "Press upward without bouncing or excessively arching your back."],
["Setting the bench too steeply.",
 "Bouncing the bar off the chest.",
 "Flaring the elbows excessively or losing shoulder stability."]
),
"Decline Bench Press": (
["Secure your legs under the bench supports.",
 "Grip the bar evenly and lower it toward your lower chest.",
 "Keep your shoulder blades stable against the bench.",
 "Press the bar upward with controlled movement."],
["Using an unsecured bench setup.",
 "Bouncing the bar off the chest.",
 "Using excessive weight without a spotter."]
),
"Chest Fly": (
["Lie on a flat bench with a dumbbell in each hand.",
 "Keep a slight bend in your elbows and face your palms inward.",
 "Open your arms slowly until you feel a comfortable chest stretch.",
 "Bring the dumbbells together above your chest without striking them."],
["Using heavy dumbbells.",
 "Straightening or excessively bending the elbows.",
 "Lowering the arms beyond a comfortable shoulder range."]
),
"Cable Chest Fly": (
["Set both cable pulleys around chest height.",
 "Stand centrally with one foot slightly forward.",
 "Keep a slight bend in your elbows.",
 "Bring your hands together in front of your chest.",
 "Return slowly while maintaining control."],
["Using momentum to move the cables.",
 "Allowing the shoulders to roll forward.",
 "Using excessive weight."]
),
"Chest Dip": (
["Hold the parallel bars and support your body with straight arms.",
 "Lean your torso slightly forward to emphasize the chest.",
 "Bend your elbows and lower yourself within a comfortable range.",
 "Push through your hands to return to the starting position."],
["Dropping too deeply and irritating the shoulders.",
 "Swinging the legs or using momentum.",
 "Shrugging the shoulders toward the ears."]
),
"Pec Deck": (
["Adjust the seat so the handles are approximately chest height.",
 "Place your forearms or hands against the machine pads.",
 "Bring the handles together in front of your chest.",
 "Return slowly until you feel a comfortable chest stretch."],
["Setting the seat too high or too low.",
 "Slamming the handles together.",
 "Allowing the weight stack to drop."]
),
"Pull-Ups": (
["Grip the bar slightly wider than shoulder-width.",
 "Begin from a controlled hang with your shoulders engaged.",
 "Pull your chest toward the bar.",
 "Lower yourself slowly until your arms are extended comfortably."],
["Kipping or swinging to complete repetitions.",
 "Using a partial range of motion unintentionally.",
 "Shrugging excessively during the pull."]
),
"Chin-Ups": (
["Grip the bar with palms facing toward you.",
 "Start from a controlled hang.",
 "Pull yourself upward until your chin reaches bar height.",
 "Lower yourself slowly without swinging."],
["Swinging the body to gain momentum.",
 "Using excessive wrist movement.",
 "Dropping quickly from the top position."]
),
"Seated Cable Row": (
["Sit upright with your feet supported on the platform.",
 "Hold the handle with your arms extended comfortably.",
 "Pull the handle toward your lower torso.",
 "Squeeze your shoulder blades gently together.",
 "Return the handle slowly without rounding your back."],
["Rounding the lower back.",
 "Leaning backward excessively.",
 "Jerking the handle toward the body."]
),
"Barbell Bent-Over Row": (
["Stand with feet about hip-width apart and hold the barbell.",
 "Hinge at the hips while keeping your spine neutral.",
 "Let the bar hang below your shoulders.",
 "Pull the bar toward your lower ribs.",
 "Lower it slowly while maintaining your torso position."],
["Rounding the lower back.",
 "Using momentum to lift the bar.",
 "Standing too upright during the movement."]
),
"T-Bar Row": (
["Position yourself securely on the machine or landmine setup.",
 "Hold the handles and maintain a stable torso.",
 "Pull the handle toward your lower chest or upper abdomen.",
 "Squeeze your back muscles briefly.",
 "Lower the weight under control."],
["Rounding the back.",
 "Using excessive momentum.",
 "Pulling with the arms while neglecting back control."]
),
"Straight-Arm Pulldown": (
["Stand facing the cable machine with a high pulley.",
 "Hold the bar with arms extended and a slight elbow bend.",
 "Keep your torso stable.",
 "Pull the bar down toward your thighs.",
 "Return slowly to the starting position."],
["Bending the elbows excessively.",
 "Leaning backward to move the weight.",
 "Using momentum instead of controlling the cable."]
),
"Face Pull": (
["Set the cable pulley around face height.",
 "Hold the rope with both hands.",
 "Pull the rope toward your face while separating your hands.",
 "Keep your elbows raised and squeeze your rear shoulders.",
 "Return slowly."],
["Pulling the rope toward the chest instead of the face.",
 "Arching the lower back.",
 "Using excessive weight."]
),
"Reverse Pec Deck": (
["Adjust the seat so the handles are around shoulder height.",
 "Face the machine and hold the handles.",
 "Keep a slight bend in your elbows.",
 "Move your arms outward and backward.",
 "Return slowly without letting the weight stack slam."],
["Using momentum.",
 "Shrugging the shoulders excessively.",
 "Using a range of motion that causes shoulder discomfort."]
),
"Front Raise": (
["Stand upright holding dumbbells in front of your thighs.",
 "Keep a slight bend in your elbows.",
 "Raise the dumbbells forward to approximately shoulder height.",
 "Lower them slowly to the starting position."],
["Swinging the dumbbells.",
 "Raising the weights far above shoulder height.",
 "Leaning backward to lift heavier weights."]
),
"Arnold Press": (
["Sit or stand with dumbbells in front of your shoulders.",
 "Start with palms facing your body.",
 "Press upward while rotating your palms forward.",
 "Extend your arms comfortably overhead.",
 "Lower slowly while reversing the rotation."],
["Forcing the shoulder rotation.",
 "Arching the lower back excessively.",
 "Using weights that prevent controlled movement."]
),
"Preacher Curl": (
["Adjust the preacher bench so your upper arms rest securely on the pad.",
 "Hold the bar with an appropriate grip.",
 "Curl the bar toward your shoulders.",
 "Lower slowly without fully relaxing or locking the elbows."],
["Lifting the elbows off the pad.",
 "Dropping the weight quickly.",
 "Using excessive weight and shortening the movement."]
),
"Concentration Curl": (
["Sit on a bench with your legs comfortably apart.",
 "Hold a dumbbell and support your upper arm against your inner thigh.",
 "Curl the dumbbell toward your shoulder.",
 "Lower it slowly while keeping your upper arm stable."],
["Moving the upper arm during the curl.",
 "Swinging the dumbbell.",
 "Twisting the torso to lift the weight."]
),
"Cable Biceps Curl": (
["Attach a suitable handle to a low cable pulley.",
 "Stand upright with your elbows close to your sides.",
 "Curl the handle toward your shoulders.",
 "Lower slowly while maintaining cable tension."],
["Moving the elbows forward and backward.",
 "Leaning backward to lift the weight.",
 "Letting the cable pull the arms down uncontrollably."]
),
"EZ-Bar Curl": (
["Stand upright and hold the EZ bar using a comfortable angled grip.",
 "Keep your elbows close to your torso.",
 "Curl the bar toward your shoulders.",
 "Lower it slowly without swinging."],
["Swinging the torso.",
 "Moving the elbows excessively.",
 "Using a grip that causes wrist discomfort."]
),
"Overhead Triceps Extension": (
["Hold one dumbbell securely with both hands.",
 "Raise it overhead with your elbows pointing upward.",
 "Bend your elbows to lower the dumbbell behind your head.",
 "Extend your elbows to return to the starting position."],
["Flaring the elbows excessively.",
 "Arching the lower back.",
 "Lowering the weight too far or too quickly."]
),
"Skull Crushers": (
["Lie on a bench holding an EZ bar above your chest.",
 "Keep your upper arms relatively stable.",
 "Bend your elbows to lower the bar toward your forehead or just behind it.",
 "Extend your elbows to raise the bar again."],
["Moving the upper arms excessively.",
 "Lowering the bar uncontrollably.",
 "Using heavy weight without safe control."]
),
"Close-Grip Bench Press": (
["Lie on a bench and grip the bar slightly narrower than shoulder-width.",
 "Keep your wrists stacked over your forearms.",
 "Lower the bar toward your lower chest.",
 "Press upward while keeping your elbows reasonably close to your torso."],
["Using an extremely narrow grip.",
 "Allowing the wrists to bend excessively.",
 "Bouncing the bar off the chest."]
),
"Diamond Push-Ups": (
["Start in a push-up position with hands close together beneath your chest.",
 "Keep your body in a straight line.",
 "Bend your elbows and lower your chest toward your hands.",
 "Push through your palms to return to the starting position."],
["Allowing the hips to sag.",
 "Flaring the elbows excessively.",
 "Forcing the hand position if it causes wrist pain."]
),
"Goblet Squat": (
["Hold one dumbbell vertically close to your chest.",
 "Stand with feet around shoulder-width apart.",
 "Bend your hips and knees to squat down comfortably.",
 "Keep your chest lifted and feet planted.",
 "Push through your feet to stand upright."],
["Allowing the heels to lift.",
 "Rounding the back.",
 "Letting the knees collapse inward."]
),
"Bulgarian Split Squat": (
["Stand in front of a bench and place one foot behind you on it.",
 "Keep your front foot firmly planted.",
 "Lower your hips by bending the front knee.",
 "Keep your torso controlled and push through the front foot to rise.",
 "Complete repetitions on both legs."],
["Placing the front foot too close to the bench.",
 "Losing balance through excessive speed.",
 "Allowing the front knee to collapse inward."]
),
"Leg Extension": (
["Adjust the machine so the seat and backrest support you comfortably.",
 "Position the padded roller above your ankles.",
 "Extend your knees to raise the pad.",
 "Pause briefly and lower the weight slowly."],
["Using momentum to kick the weight.",
 "Setting the roller incorrectly.",
 "Dropping the weight stack."]
),
"Seated Leg Curl": (
["Adjust the machine so the knee joint lines up with the machine pivot.",
 "Position the lower-leg pad above your ankles.",
 "Curl your heels downward and backward.",
 "Pause briefly and return slowly."],
["Lifting your hips from the seat.",
 "Using momentum.",
 "Setting the machine incorrectly."]
),
"Lying Leg Curl": (
["Lie face down and position the roller just above your heels.",
 "Keep your hips against the bench.",
 "Curl your heels toward your glutes.",
 "Lower the weight slowly."],
["Lifting the hips off the bench.",
 "Arching the lower back excessively.",
 "Using momentum."]
),
"Hip Thrust": (
["Sit with your upper back supported against a bench.",
 "Position a padded barbell across your hips.",
 "Plant your feet about shoulder-width apart.",
 "Drive through your feet to raise your hips.",
 "Squeeze your glutes at the top without overextending your back.",
 "Lower your hips under control."],
["Hyperextending the lower back at the top.",
 "Placing the feet too far away or too close.",
 "Dropping the hips quickly."]
),
"Standing Calf Raise": (
["Position your shoulders under the machine pads.",
 "Place the balls of your feet on the platform.",
 "Lower your heels for a comfortable calf stretch.",
 "Rise onto your toes as high as comfortably possible.",
 "Lower slowly."],
["Bouncing through repetitions.",
 "Using only a very short range of motion.",
 "Bending the knees excessively."]
),
"Seated Calf Raise": (
["Sit with the balls of your feet on the platform.",
 "Position the padded lever securely above your knees.",
 "Lower your heels for a comfortable stretch.",
 "Raise your heels as high as possible without bouncing.",
 "Lower slowly."],
["Bouncing the heels.",
 "Using excessive weight.",
 "Performing very short repetitions."]
),
"Russian Twist": (
["Sit on the floor with your knees bent.",
 "Lean back slightly while keeping your spine controlled.",
 "Rotate your torso gently from side to side.",
 "Keep the movement controlled and breathe steadily."],
["Rounding the back excessively.",
 "Swinging the arms without rotating the torso.",
 "Using momentum or excessive speed."]
),
"Crunches": (
["Lie on your back with knees bent and feet on the floor.",
 "Place your hands lightly beside your head or across your chest.",
 "Gently curl your shoulders off the floor.",
 "Pause briefly and lower under control."],
["Pulling the head or neck with your hands.",
 "Using momentum.",
 "Trying to lift the entire lower back off the floor."]
),
"Hanging Knee Raise": (
["Hang from a secure pull-up bar with a comfortable grip.",
 "Brace your abdomen and keep your body steady.",
 "Raise your knees toward your chest.",
 "Lower your legs slowly without swinging."],
["Swinging the body for momentum.",
 "Dropping the legs quickly.",
 "Arching the lower back excessively."]
)
}

connection = get_connection()

try:
    updated = 0

    for name, (instructions, mistakes) in GUIDANCE.items():
        cursor = connection.execute("""
            UPDATE exercises
            SET instructions = ?, common_mistakes = ?
            WHERE name = ? AND is_active = 1
        """, ("\n".join(instructions), "\n".join(mistakes), name))

        updated += cursor.rowcount

    connection.commit()

    print("Exercise guidance update completed.")
    print("Exercises with updated guidance:", updated)
    print("Expected exercises:", len(GUIDANCE))

    if updated != len(GUIDANCE):
        print("WARNING: Some exercise names were not found. Check the database.")

finally:
    connection.close()
