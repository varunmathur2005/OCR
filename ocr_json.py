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
import pandas as pd

# Start the timer to measure script execution time
start_time = time.time()

# Load the OpenAI API key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define the prompt as a variable that can be easily edited by the user
user_prompt = """
You are an accountant for a company. Your job is to extract expense information from the provided image document. Return the information in JSON format using the specified keys. If the information is not available, use null:
1. totalAmount: total purchase amount without currency 
2. currency: Currency code (ISO 4217)
3. date: Carefully extract the date of purchase, receipt date, or invoice date in DD-MM-YYYY format. Return null if no date is present.
4. time: Purchase time in HH:mm:ss format (24-hour)
5. vatAmount: VAT amount charged
6. supplierTrnNumber: Supplier's VAT number
7. allDatesInReceipts: All dates in the document with their descriptions
8. descriptionOfReceipt: A concise, single-line description of the expense with User-specific information (For example: Pre-Approval for work permit for Awab Yaqoob).
9. suggestionForUploader: Suggestions to improve the image for AI extraction, if needed. Examples: "Please upload receipts instead of email or SMS confirmations," "Upload the actual invoice instead of a screenshot," "Only part of the image is visible; please upload the complete picture," "There is a smaller image on top of the document; please upload them separately," "Upload a clear picture"
                        """


def process_csv(file_path):
    """Processes the CSV file by replacing NULL values and extracting image filenames."""
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Replace NULL and null with empty blanks
    df.replace(["NULL", "null"], "", inplace=True)

    # Extract the image filename from the 'images' column and create a new column 'image_path'
    df["image_path"] = df["images"].apply(
        lambda x: x.split("/")[-1] if isinstance(x, str) else ""
    )

    # Overwrite the existing CSV file with the updated DataFrame
    df.to_csv(file_path, index=False)

    print(f"Processing complete. The file {file_path} has been updated.")
    return file_path


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
    """Processes each transaction, sends API requests, and saves the results to a JSON file."""
    processed_file = process_csv(input_file)  # Process the CSV before using it
    transactions = []

    with open(processed_file, "r", newline="") as csvfile:
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

    # Write combined data to result.json
    with open(output_file, "w") as jsonfile:
        json.dump(result_data, jsonfile, indent=4)

    print(
        f"Processed {len(result_data)} out of {len(transactions)} files successfully."
    )
    print(f"Total execution time: {time.time() - start_time} seconds")


# Define input and output paths
image_directory = ""
input_file = ""
output_file = ""

# Process transactions with the user-defined prompt
process_transactions(input_file, image_directory, output_file, user_prompt)
