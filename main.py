import csv
import base64
import requests
from dotenv import load_dotenv
import os
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
import json
import time

# Start the timer to measure script execution time
start_time = time.time()

# Load the OpenAI API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define the prompt as a variable that can be easily edited by the user
user_prompt = """

***Add prompt for OCR***

"""


def encode_image_to_base64(image_path):
    """Encodes an image to base64 format."""
    try:
        with open(image_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: File {image_path} not found.")
        return None


def combine_images_into_single_image(images):
    """Combines multiple images into a single image."""
    widths, heights = zip(*(image.size for image in images))

    total_width = sum(widths)
    max_height = max(heights)

    combined_image = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for image in images:
        combined_image.paste(image, (x_offset, 0))
        x_offset += image.width

    return combined_image


def prepare_api_payload(base64_image, prompt):
    """Creates the payload for the API request."""
    return {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "response_format": {"type": "json_object"},
    }


def send_api_request(base64_image, transaction, prompt):
    """Sends the API request to OpenAI and returns the parsed response."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = prepare_api_payload(base64_image, prompt)

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    if response.status_code == 200:
        try:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # Clean and parse the JSON content
            clean_content = content.replace('\\"', '"').replace("\\n", "").strip()

            clean_content = (
                clean_content[:-1] if clean_content.endswith(",") else clean_content
            )
            return {**transaction, **json.loads(clean_content)}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for {transaction['image_path']}: {e}")
            print(f"Response content: {response.content}")
            return None
    else:
        print(f"Error processing file {transaction['image_path']}: {response.text}")
        return None


def process_transactions(input_file, image_directory, output_file, prompt):
    """Processes each transaction, sends API requests, and saves the results to a CSV."""
    transactions = []

    with open(input_file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transactions.append(row)

    result_data = []

    for transaction in transactions:
        image_path = os.path.join(image_directory, transaction["image_path"])
        print(f"Processing file: {image_path}")

        if image_path.lower().endswith((".pdf", ".PDF")):
            try:
                images = convert_from_bytes(open(image_path, "rb").read())
                combined_image = combine_images_into_single_image(images)

                buffered = BytesIO()
                combined_image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            except Exception as e:
                print(f"Error processing PDF {image_path}: {str(e)}")
                continue
        else:
            base64_image = encode_image_to_base64(image_path)

        if base64_image:
            result_row = send_api_request(base64_image, transaction, prompt)
            if result_row:
                result_data.append(result_row)
            else:
                print(f"Failed to process image {image_path}")

    # Extract output fields dynamically from the results
    output_fieldnames = set()
    for data in result_data:
        output_fieldnames.update(data.keys())

    fieldnames = list(output_fieldnames)

    # Write combined data to result.csv
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in result_data:
            writer.writerow(data)

    print(
        f"Processed {len(result_data)} out of {len(transactions)} files successfully."
    )
    print(f"Total execution time: {time.time() - start_time} seconds")


# Define input and output paths
image_directory = "/path/to/image_directory"
input_file = "/path/to/input.csv"
output_file = "/path/to/output.csv"

# Process transactions with the user-defined prompt
process_transactions(input_file, image_directory, output_file, user_prompt)
