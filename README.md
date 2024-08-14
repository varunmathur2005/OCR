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
