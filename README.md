### **Description**

This project automates the extraction of expense information from image-based receipts using AI. The script processes images or PDFs, encodes them in base64, and sends them to the OpenAI API for analysis. It returns structured JSON data with details such as total amount, date, time, VAT, and itemized purchases. This tool is particularly useful for accountants or finance teams who need to process large volumes of receipts efficiently.

### **Features:**
- **Image & PDF Support:** Handles both image files and PDFs, converting them as needed.
- **AI-Powered Analysis:** Uses OpenAI's GPT-4o model to extract key details from receipts.
- **JSON Output:** Returns data in a structured JSON format for easy integration with other tools.
- **Error Handling:** Gracefully handles file processing errors and API response issues.
- **Batch Processing:** Processes multiple receipts at once from a CSV file and outputs results to a new CSV.

## Requirements
To run this project, you will need to install the following Python packages:
- `requests`
- `python-dotenv`
- `pdf2image`
- `Pillow`

```bash
pip install -r requirements.txt

```


### **Steps to Use the Project**

1. **Clone the Repository:**
   
   ```bash
   git clone https://github.com/varunmathur2005/OCR.git
   cd OCR
   ```

3. **Set Up the Environment:**
4. 
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Configure API Key:**
   -Create a `.env` file in the root of the project directory and add OpenAI API key as shown below:

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

6. **Run the Script:**
   - Once everything is set up, they can run the main script that processes images and extracts data.

   ```bash
   python main.py
   ```

8. **Modify the Prompt:**
   - If you want to customize what information is extracted, they can modify the `prompt` variable in the script to change the criteria.

9. **View Results:**
   - The script will process the images and save the extracted data to a CSV file (as per your code).

### **Common Use Case Flow**

1. **Prepare Input Files:**
   - Users should have the images or PDFs they want to process stored in the specified directory.
   - They should also prepare the CSV file that contains details about the images.

2. **Customize and Execute:**
   - If they have specific needs (e.g., different fields to extract), they can modify the prompt within the script and then run it.

3. **Review Output:**
   - The output will be generated in the specified CSV file, which they can then use for further analysis or processing.

### **Troubleshooting**

- **Error Handling:** The script has basic error handling to inform users if something goes wrong, like if a file is missing or if the API fails.
- **Dependencies:** Ensure that all required dependencies are installed, especially if they encounter import errors.
- **API Issues:** If there are issues with the OpenAI API, users should check their API key and usage limits.
