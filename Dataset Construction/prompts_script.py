import os
import requests
import csv
import json
import random
import base64
import fal_client
from fal_client import InProgress



# 1) Configs & Paths (unchanged) ...
MODEL_ID = "FLUX"
OUTPUT_ROOT = "ProjectRoot"
NUM_PROMPTS = 1
NUM_EXPRESSIONS = 20
SEED_PAD = 6
PROMPT_PAD = 5
EXPR_PAD = 3

# 2) Load face_features.json (unchanged) ...
with open("face_features.json", "r") as file:
    data = json.load(file)

# 3) Base instruction (unchanged) ...
base_instruction = (
    "Create a 1024x1024 pixel portrait (1:1 ratio) of a single subject with a white background. "
    "The subject should have no accessories or make-up, with hair pulled back and wearing a white T-shirt. "
    "The photo should be taken under indoor lighting using a standard lens, captured from a frontal view 6 feet away, "
    "with the subject looking straight ahead."
)

# 4) Helper functions (unchanged except for adding zero_pad, etc.) ...
def zero_pad(num, length):
    return str(num).zfill(length)

def get_random_features(feature_dict):
    return {k: random.choice(v) for k, v in feature_dict.items()}

def generate_main_description():
    shape = get_random_features(data["Shape"])
    structure = get_random_features(data["Structure"])
    texture = get_random_features(data["Texture & Features"])
    color = get_random_features(data["Color"])
    desc = (
        f"The subject's facial features are characterized by a {shape['Face']} face shape, "
        f"{shape['Eye']} eyes, and {shape['Eyebrow']} eyebrows, complemented by a {shape['Nose']} nose, "
        f"{shape['Lips']} lips, {shape['Cheek']} cheeks, a {shape['Chin']} chin, and a {shape['Hairline']} hairline. "
        f"In terms of structure, the subject has {structure['Eye']} eyes, {structure['Eyebrow']} eyebrows, "
        f"a {structure['Nose']} nose, and a {structure['Jawline']} jawline. "
        f"Their skin appears {texture['Skin Texture']} and {texture['Skin Features']}, with {texture['Cheek']} cheeks "
        f"and {texture['Lips']} lips. The subject's eyes are {color['Eye']}, the skin tone is {color['Skin Tone']}, "
        f"and {color['Skin Undertones']} undertones enhance the overall appearance. "
    )
    return desc

def generate_expression_description():
    expression = get_random_features(data["Expression"])
    return (
        f"The expression includes {expression['Eye']} eyes, "
        f"{expression['Eyebrow']} eyebrows, and {expression['Lips']} lips."
    )

def on_queue_update(update):
    """
    Callback if you want to see progress logs from fal_client.
    This is optional; feel free to remove if not needed.
    """
    if isinstance(update, InProgress):
        for log_msg in update.logs:
            print(log_msg["message"])

def generate_flux_image(prompt):
    """
    Calls fal_client.subscribe, which returns a JSON object containing a URL to the image.
    We then download that image from the URL and return the raw bytes.
    """
    # 1) Subscribe to the model
    result = fal_client.subscribe(
        "fal-ai/flux-pro/v1.1-ultra",  # model as first arg
        arguments={"prompt": prompt},
        with_logs=True,
        on_queue_update=on_queue_update
    )

    print("[DEBUG] Full result:", result)

    # 2) Ensure "images" exists
    if "images" not in result or not result["images"]:
        raise ValueError("No images found in the fal_client response.")

    # 3) The first image is a dict with a 'url' key
    first_image_dict = result["images"][0]
    print("[DEBUG] First image dict:", first_image_dict)

    # We expect something like:
    # {
    #   'url': 'https://fal.media/files/...',
    #   'width': 2752,
    #   'height': 1536,
    #   'content_type': 'image/jpeg'
    # }

    if "url" not in first_image_dict:
        raise ValueError("No 'url' key found for the image. Cannot download.")

    image_url = first_image_dict["url"]

    # 4) Download the image from this URL
    response = requests.get(image_url)
    response.raise_for_status()  # Raises an error if the download failed
    image_bytes = response.content  # This is the raw JPEG/PNG/etc. data

    # 5) Return the raw bytes
    return image_bytes

def main():
    model_dir = os.path.join(OUTPUT_ROOT, MODEL_ID)
    os.makedirs(model_dir, exist_ok=True)

    prompts_csv_path = os.path.join(model_dir, "prompts.csv")
    prompts_csv_exists = os.path.isfile(prompts_csv_path)
    with open(prompts_csv_path, "w", newline="", encoding="utf-8") as prompts_csv:
        writer = csv.writer(prompts_csv)
        if not prompts_csv_exists:
            writer.writerow(["PromptID", "SeedID", "Prompt"])

        # Generate each prompt
        for p_idx in range(1, NUM_PROMPTS + 1):
            seed_val = random.randint(0, 99999)
            seed_str = zero_pad(seed_val, SEED_PAD)
            prompt_str = zero_pad(p_idx, PROMPT_PAD)

            # Build main prompt
            main_desc = generate_main_description()
            full_prompt_text = main_desc + base_instruction

            writer.writerow([prompt_str, seed_str, full_prompt_text])

            # Create subfolder
            folder_name = f"SID{seed_str}_PID{prompt_str}"
            prompt_folder = os.path.join(model_dir, folder_name)
            os.makedirs(prompt_folder, exist_ok=True)

            expressions_csv_path = os.path.join(prompt_folder, "expressions.csv")
            expressions_csv_exists = os.path.isfile(expressions_csv_path)
            with open(expressions_csv_path, "a", newline="", encoding="utf-8") as expr_csv:
                expr_writer = csv.writer(expr_csv)
                if not expressions_csv_exists:
                    expr_writer.writerow(["ExpressionID", "ExpressionText"])

                # Generate N expressions
                for e_idx in range(1, NUM_EXPRESSIONS + 1):
                    expr_str = zero_pad(e_idx, EXPR_PAD)
                    expr_description = generate_expression_description()
                    expr_writer.writerow([expr_str, expr_description])

                    final_prompt_for_image = f"{full_prompt_text} {expr_description}"

                    # **** HERE IS THE KEY CHANGE: call the API ****
                    try:
                        image_data = generate_flux_image(final_prompt_for_image)
                    except Exception as e:
                        print(f"Error generating image for prompt: {final_prompt_for_image}\n{e}")
                        

                    # Save to .jpg
                    image_filename = os.path.join(prompt_folder, f"exp{expr_str}.jpg")
                    with open(image_filename, "wb") as img_file:
                        img_file.write(image_data)

    print(f"Done! Generated {NUM_PROMPTS} prompts, each with {NUM_EXPRESSIONS} expressions under: {model_dir}")

if __name__ == "__main__":
    main()
