"
# Text to SQL with Streamlit and Google Generative AI

## Introduction

This repository provides a Python application that leverages Streamlit and Google Generative AI (Gemini Pro) to convert natural language questions into SQL queries. Users can interact with the application through a web interface to get real-time results from a sample SQLite database.

## Key Features

- **Natural Language to SQL Conversion:** Ask questions about the student data in plain English, and the system will automatically generate the corresponding SQL query.
- **Interactive Web Interface:** Streamlit creates a user-friendly web interface for easy interaction and visualization of results.
- **Database Integration:** Connects to a sample student database (`student.db`) for retrieving and displaying data.
- **Error Handling:** Provides informative messages in case of invalid input or database errors.

## Requirements

- Python 3.7 or Above ([Download Python](https://www.python.org/downloads/))
- Streamlit ([Installation Guide](https://docs.streamlit.io/get-started/installation))
- Google Generative AI ([More Information](https://www.xda-developers.com/google-generative-ai-expands-beta-testing/))
- Python Dotenv ([PyPI Link](https://pypi.org/project/dotenv/))

## Installation

### Clone this repository:

```bash
git clone https://github.com/your-username/text-to-sql.git
cd text-to-sql
```

### Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
```

### Install the required dependencies:

```bash
pip install -r requirements.txt
```

## API Key Setup

1. Create a Google Cloud Project and enable the Generative AI API ([Google Cloud Guide](https://cloud.google.com/ai/generative-ai)).
2. Create an API key and store it in a secure environment variable named `GOOGLE_API_KEY`. You can use a `.env` file for this:

    ```plaintext
    GOOGLE_API_KEY=your_api_key
    ```

   Note: Refer to the [Google Generative AI documentation](https://cloud.google.com/ai/generative-ai) for detailed instructions.

## Running the Application

### Navigate to the project directory:

```bash
cd text-to-sql
```

### Start the Streamlit app:

```bash
streamlit run main.py
```

### Open [http://localhost:8501/](http://localhost:8501/) in your web browser to access the application.

## Usage

1. Enter your natural language question in the text input field.
2. Click the "Submit" button.
3. The application will generate the corresponding SQL query and display it.
4. If successful, it will also fetch and display the query results from the student database.

### Example

- **Question:** "Which students are in the 10th class?"
- **Generated SQL Query:** `SELECT * FROM STUDENT WHERE CLASS="10th";`

## Additional Notes

- The sample student database (`student.db`) is included in the repository.
- This is a basic implementation and may require further customization for complex queries or large datasets.
- Consider exploring more advanced techniques for natural language processing and SQL generation.

## Contributing

Contributions are welcome! Please create a pull request with your proposed changes.

## Authors

Mukesh Vemulapalli

## Contact

For any questions or feedback, please contact vemulapallimukesh@gmail.com.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.