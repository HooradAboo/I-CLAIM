# README

## Overview
This Python script is designed to generate random portrait descriptions (prompts) based on predefined categories and features stored in a JSON file. Each description is then combined with a base instruction for creating a specific type of image (a 1024x1024 pixel portrait with certain constraints). The script can output multiple variations of these descriptions, each optionally tagged with a unique or shared random seed.

## What This Script Does

1. **Reads in feature data** from a JSON file called `face_features.json` (which contains categorized lists of facial features, such as eye shapes, nose types, skin textures).
2. **Generates random prompts** that describe a subject’s face. These prompts combine:
   - Randomly selected facial shapes, structures, textures, and colors.
   - A specified expression (eyes, eyebrows, lips, etc.).
   - A fixed base instruction describing the image composition (1024x1024 resolution, white background, no accessories).
3. **Optionally utilizes random seeds.** By default, each of the two prompts in a pair has a different seed. If `USE_SAME_SEED` is set to `True`, both prompts in the pair share the same seed.

## How to Work With This Script

### Prerequisites
- Python 3.x installed
- A valid `face_features.json` file placed in the same directory as the script

### Set up `face_features.json`
The JSON file should have a top-level structure with keys matching the categories `"Shape"`, `"Structure"`, `"Texture & Features"`, `"Color"`, and `"Expression"`. Each of these keys should map to a dictionary containing lists of possible features. For example:

```json
{
  "Shape": {
    "Face": ["round", "oval", "square"],
    "Eye": ["large", "medium", "small"],
    "Eyebrow": ["thin", "thick"],
    "Nose": ["button", "aquiline"],
    "Lips": ["thin", "full"],
    "Cheek": ["slender", "rounded"],
    "Chin": ["pointed", "rounded"],
    "Hairline": ["high", "low"]
  },
  "Structure": {
    "Eye": ["wide-set", "close-set"],
    "Eyebrow": ["arched", "straight"],
    "Nose": ["straight", "crooked"],
    "Jawline": ["strong", "soft"]
  },
  "Texture & Features": {
    "Skin Texture": ["smooth", "textured"],
    "Skin Features": ["freckled", "clear"],
    "Cheek": ["rosy", "pale"],
    "Lips": ["dry", "moist"]
  },
  "Color": {
    "Eye": ["brown", "blue", "green"],
    "Skin Tone": ["fair", "medium", "dark"],
    "Skin Undertones": ["warm", "cool"]
  },
  "Expression": {
    "Eye": ["bright", "narrow"],
    "Eyebrow": ["raised", "furrowed"],
    "Lips": ["smiling", "neutral"]
  }
}

Using the flux1.1 pro API:

1. Calling the API
Setup your API Key: (Account-> api key-> add key)
Set FAL_KEY as an environment variable in your runtime.
export FAL_KEY="YOUR_API_KEY"

Submit a request:
The client API handles the API submit protocol. It will handle the request status updates and return the result when the request is completed.

response=$(curl --request POST \
  --url https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra \
  --header "Authorization: Key $FAL_KEY" \
  --header "Content-Type: application/json" \
  --data '{
     "prompt": "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture."
   }')
REQUEST_ID=$(echo "$response" | grep -o '"request_id": *"[^"]*"' | sed 's/"request_id": *//; s/"//g')


2. Authentication
The API uses an API Key for authentication. It is recommended you set the FAL_KEY environment variable in your runtime when possible.


Fetch request status: (can also check online browser if its complete or not as well)
You can fetch the status of a request to check if it is completed or still in progress.

curl --request GET \
  --url https://queue.fal.run/fal-ai/flux-pro/requests/$REQUEST_ID/status \
  --header "Authorization: Key $FAL_KEY"


3. Get the result
Once the request is completed, you can fetch the result

curl --request GET \
  --url https://queue.fal.run/fal-ai/flux-pro/requests/$REQUEST_ID \
  --header "Authorization: Key $FAL_KEY"


4. Schema
Input:

prompt (string)
The prompt to generate an image from.

seed (integer)
The same seed and the same prompt given to the same version of the model will output the same image every time.

aspect_ratio Enum (string)
The aspect ratio of the generated image. Default value: 16:9
Possible enum values: 21:9, 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16, 9:21


output_format OutputFormatEnum
The format of the generated image. Default value: "jpeg"
Possible enum values: jpeg, png

{
  "prompt": "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture.",
  "num_images": 1,
  "enable_safety_checker": true,
  "safety_tolerance": "2",
  "output_format": "jpeg",
  "aspect_ratio": "16:9"
}


For more info on accepting file URLS as input, more scheme eg: enable_safety_checker, sync_mode, ImageSize etc go to:
https://fal.ai/models/fal-ai/flux-pro/v1.1-ultra/api?platform=http