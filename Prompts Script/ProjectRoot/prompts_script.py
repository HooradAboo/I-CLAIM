import os, csv, json, random, requests
import fal_client
from fal_client import InProgress


# 1) Configs & Paths (unchanged) ...
MODEL_ID = "FLUX"
OUTPUT_ROOT = "ProjectRoot"
NUM_PROMPTS = 2
NUM_EXPRESSIONS = 5
SEED_PAD = 6
PROMPT_PAD = 5
EXPR_PAD = 3
FAL_MODEL = "fal-ai/flux-pro/v1.1-ultra"

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

def next_pid(csv_path: str, pad: int = 5) -> str:
    """Return a zero‑padded PID that has never been used before."""
    if not os.path.isfile(csv_path):
        return zero_pad(1, pad)
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = sum(1 for _ in f) - 1      # minus header
    return zero_pad(rows + 1, pad)


def on_queue_update(update):
    """
    Callback if you want to see progress logs from fal_client.
    This will only print if `update.logs` is a non‑empty iterable of dicts.
    """
    if isinstance(update, InProgress) and update.logs:
        for log_msg in update.logs:
            # ensure we have a dict with a "message" key
            if isinstance(log_msg, dict) and "message" in log_msg:
                print(log_msg["message"])


def generate_flux_image(prompt, seed):
    # 1) Subscribe to the model
    """
    Call Flux and return the raw image bytes.
    The same seed yields deterministic output for that prompt.
    """
    result = fal_client.subscribe(
        FAL_MODEL,
        arguments={
            "prompt": prompt,
            "seed": int(seed)          # <- force Flux to reuse this seed
        },
        with_logs=False,
        on_queue_update=on_queue_update
    )

    first = result["images"][0]          # dict with a URL
    img = requests.get(first["url"], timeout=30)
    img.raise_for_status()
    return img.content

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
    csv_exists = os.path.isfile(prompts_csv_path)

    # 1) Count how many prompts are already on disk
    if csv_exists:
        with open(prompts_csv_path, newline="", encoding="utf-8") as f:
            existing_rows = sum(1 for _ in f) - 1   # subtract header
    else:
        existing_rows = 0

    # 1a) Ensure prompts.csv ends with a newline so we append on a new row
    if csv_exists:
        with open(prompts_csv_path, "rb+") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(-1, os.SEEK_END)
                last = f.read(1)
                if last not in (b"\n", b"\r"):
                    f.write(b"\n")

    # 2) Now open in append mode *after* counting
    with open(prompts_csv_path, "a", newline="", encoding="utf-8") as prompts_csv:
        writer = csv.writer(prompts_csv)

        if not csv_exists:
            writer.writerow(["PID", "SID", "Prompt"])

        # 3) Generate your new prompts
        for i in range(NUM_PROMPTS):
            # Always pick the next unused PID
            prompt_index = existing_rows + i + 1
            prompt_str  = zero_pad(prompt_index, PROMPT_PAD)   # e.g. "00003" or "00004"
            seed_val     = random.randint(0, 99999)
            seed_str     = zero_pad(seed_val, SEED_PAD)
            prefixed_pid = f"P{prompt_str}"
            prefixed_sid = f"S{seed_str}"

            # build prompt text and write one row
            main_desc        = generate_main_description()
            full_prompt_text = main_desc + base_instruction
            writer.writerow([prefixed_pid, prefixed_sid, full_prompt_text])

            # 4) Create the folder for this seed+prompt
            folder_name = f"SID{seed_str}_PID{prompt_str}"
            prompt_folder = os.path.join(model_dir, folder_name)
            os.makedirs(prompt_folder, exist_ok=True)

            # 5) Open (or create) expressions.csv for this prompt
            expressions_csv_path = os.path.join(prompt_folder, "expressions.csv")
            is_new_expr = not os.path.isfile(expressions_csv_path)
            with open(expressions_csv_path, "a", newline="", encoding="utf-8") as expr_csv:
                expr_writer = csv.writer(expr_csv)
                if is_new_expr:
                    expr_writer.writerow(["ExpressionID", "ExpressionText"])

                # 6) Generate each expression variation
                for e_idx in range(1, NUM_EXPRESSIONS + 1):
                    expr_str    = zero_pad(e_idx, EXPR_PAD)     # e.g. "001"
                    prefixed_e  = f"E{expr_str}"                # e.g. "E001"
                    expr_text   = generate_expression_description()
                    expr_writer.writerow([prefixed_e, expr_text])

                    # now call the API with that same expr_text…
                    final_prompt = f"{full_prompt_text} {expr_text}"
                    try:
                        image_data = generate_flux_image(final_prompt, seed_val)
                        image_filename = os.path.join(prompt_folder, f"{prefixed_e}.jpg")
                        with open(image_filename, "wb") as img_file:
                            img_file.write(image_data)
                    except Exception as e:
                        print(f"[ERROR] Prompt {prompt_str} Expr {prefixed_e}: {e}")


    print(f"Done! Generated {NUM_PROMPTS} prompts, each with {NUM_EXPRESSIONS} expressions under: {model_dir}")


if __name__ == "__main__":
    main()
