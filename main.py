import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import sqlite3

# Load environment variables
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro model
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    return response.text 

# Function to retrieve query from the database 
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Defining your prompt
prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name STUDENT and has the following columns NAME, CLASS, 
SECTION.

For example:
Example 1: How many entries of records are present?
The SQL command will be something like this: SELECT COUNT(*) FROM STUDENT;

Example 2: Tell me all the students studying in Data Science class?
The SQL command will be something like this: SELECT * FROM STUDENT
where CLASS="Data Science";

The SQL code should not have ' in the beginning or end and 'sql' word in output.
"""

# Streamlit Page Configuration
st.set_page_config(
    page_title="Text to SQL",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="auto",
)

# Streamlit App
st.title("Text to SQL")

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        color: #4CAF50;
        text-align: center;
        font-size: 2.5em;
    }
    .input-section {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-section {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
    }
    .error {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        color: #d32f2f;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown('<div class="title">Text to SQL</div>', unsafe_allow_html=True)

st.markdown('<div class="input-section">', unsafe_allow_html=True)
question = st.text_input("Enter your question:")
if st.button("Submit"):
    if question:
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.write("Generating SQL query...")
        sql_query = get_gemini_response(question, prompt).strip()
        st.write(f"Generated SQL query: `{sql_query}`")
        
        st.write("Fetching data from the database...")
        db_path = 'student.db'
        try:
            results = read_sql_query(sql_query, db_path)
            if results:
                st.write("Query Results:")
                for row in results:
                    st.write(row)
            else:
                st.write("No results found.")
        except Exception as e:
            st.markdown('<div class="error">', unsafe_allow_html=True)
            st.write(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("Please enter a question.")
else:
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
