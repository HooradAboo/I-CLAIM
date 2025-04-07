# ReadMe:
# 

USE_SAME_SEED = False

import json
import random

# Load feature data
with open("face_features.json", "r") as file:
    data = json.load(file)

# Constants
base_instruction = (
    "Create a 1024x1024 pixel portrait (1:1 ratio) of a single subject with a white background. "
    "The subject should have no accessories or make-up, with hair pulled back and wearing a white T-shirt. "
    "The photo should be taken under indoor lighting using a standard lens, captured from a frontal view 6 feet away, "
    "with the subject looking straight ahead."
)

# Helper function to get random feature from a category
def get_random_features(feature_dict):
    return {k: random.choice(v) for k, v in feature_dict.items()}

# Prompt generator
def generate_prompts(n):
    prompts = []
    for i in range(n):
        # Gather random features
        shape = get_random_features(data["Shape"])
        structure = get_random_features(data["Structure"])
        texture = get_random_features(data["Texture & Features"])
        color = get_random_features(data["Color"])
        expression = get_random_features(data["Expression"])

        # Compose the main description
        description = (
            f"The subject’s facial features are characterized by a {shape['Face']} face shape, "
            f"{shape['Eye']} eyes, and {shape['Eyebrow']} eyebrows, complemented by a {shape['Nose']} nose, "
            f"{shape['Lips']} lips, {shape['Cheek']} cheeks, a {shape['Chin']} chin, and a {shape['Hairline']} hairline. "
            f"In terms of structure, the subject has {structure['Eye']} eyes, {structure['Eyebrow']} eyebrows, "
            f"a {structure['Nose']} nose, and a {structure['Jawline']} jawline. "
            f"Their skin appears {texture['Skin Texture']} and {texture['Skin Features']}, with {texture['Cheek']} cheeks "
            f"and {texture['Lips']} lips. The subject’s eyes are {color['Eye']}, the skin tone is {color['Skin Tone']}, "
            f"and {color['Skin Undertones']} undertones enhance the overall appearance. "
            f"The expression includes {expression['Eye']} eyes, {expression['Eyebrow']} eyebrows, and {expression['Lips']} lips. "
        )

        # Combine with base instruction
        full_prompt = description + base_instruction

        # Generate two prompts with seeds (optional - here just appending seed as info)
        if USE_SAME_SEED:
            seed = random.randint(10000, 99999)
            prompts.append((
                f"Seed {seed}: {full_prompt}",
                f"Seed {seed}: {full_prompt}"
            ))
        else:
            seed1 = random.randint(10000, 99999)
            seed2 = random.randint(10000, 99999)
            prompts.append((
                f"Seed {seed1}: {full_prompt}",
                f"Seed {seed2}: {full_prompt}"
            ))


    return prompts

# Example usage: generate 10 prompts
num_prompts = 2
generated_prompts = generate_prompts(num_prompts)

# Output the prompts
for i, (prompt1, prompt2) in enumerate(generated_prompts, 1):
    print(f"Prompt {i} - Image 1:\n{prompt1}\n")
    print(f"Prompt {i} - Image 2:\n{prompt2}\n")
    print("=" * 80)
