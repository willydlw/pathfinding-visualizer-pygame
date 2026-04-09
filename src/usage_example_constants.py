from constants import Animation_Mode

# Usage examples
print(f"=== Class Anim_Mode Example Usage ===\n")
print(f"label: {Animation_Mode.SINGLE_STEP.label}")
print(f"name:  {Animation_Mode.SINGLE_STEP.name}")
print(f"value: {Animation_Mode.SINGLE_STEP.value}")

print(f"Reproduction: {repr(Animation_Mode.SINGLE_STEP)}")
print(f"list_labels: {Animation_Mode.list_labels()}\n")



# Use from_label() to search for string
search_str = "single step"
match = Animation_Mode.from_label("single Step")
print(f"search_str: {search_str}, from_label{search_str} returned match: {match}\n")



# Create the dictionary once
# This is O(n) once, but every search after is 0(1)
mode_map = Animation_Mode.get_lookup() 
current_mode_str = "Single Step"
current_mode = mode_map.get(current_mode_str)

print("Dictonary building usage, get_lookup({current_mode_str})")

if current_mode: 
    print(f"current_mode.name: {current_mode.name} (Value: {int(current_mode)})")
else:
    print(f"Error, ui_choice: {current_mode_str} uknown animation mode.")

