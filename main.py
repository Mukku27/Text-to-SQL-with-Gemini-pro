import streamlit as st
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os
import google.generativeai as genai
import plotly.express as px

# Load environment variables
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro model
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text

# Function to generate SQL query using prompt and question
def generate_sql_query(prompt, question):
    full_prompt = f"{prompt}\n{question}"
    sql_query = get_gemini_response(full_prompt).strip()
    return sql_query

# Function to execute an SQL query on the database
def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

# Function to retrieve query results from the database 
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Function to add a column to the database
def add_column_to_db(db_path, column_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE STUDENT ADD COLUMN {column_name} TEXT")
    conn.commit()
    conn.close()

# Function to map Excel columns to database columns using Gemini Pro API
def map_columns(excel_columns, db_columns):
    mappings = {}
    for excel_col in excel_columns:
        prompt = f"Find the best match for the column '{excel_col}' from the following options: {', '.join(db_columns)}"
        best_match = get_gemini_response(prompt).strip()
        mappings[excel_col] = best_match
    return mappings

# Function to process the Excel file and update the database
def process_excel_file(uploaded_file, db_path, action):
    df = pd.read_excel(uploaded_file)
    st.write("Column names in the uploaded file:", df.columns.tolist())

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(STUDENT)")
    existing_columns = [info[1] for info in cursor.fetchall()]

    column_mappings = map_columns(df.columns, existing_columns)

    for excel_col, db_col in column_mappings.items():
        if db_col not in existing_columns:
            add_column_to_db(db_path, db_col)
            existing_columns.append(db_col)

    for index, row in df.iterrows():
        mapped_row = {column_mappings[col]: value for col, value in row.items()}
        
        if action == "remove":
            cursor.execute("DELETE FROM STUDENT WHERE NAME=?", (mapped_row.get('NAME'),))
        
        elif action == "modify":
            set_clause = ", ".join([f"{col}=?" for col in mapped_row.keys()])
            values = tuple(mapped_row.values())
            cursor.execute(f"UPDATE STUDENT SET {set_clause} WHERE NAME=?", values + (mapped_row.get('NAME'),))
        
        else:
            cursor.execute("SELECT * FROM STUDENT WHERE NAME=?", (mapped_row.get('NAME'),))
            existing_student = cursor.fetchone()
            if existing_student:
                set_clause = ", ".join([f"{col}=?" for col in mapped_row.keys()])
                values = tuple(mapped_row.values())
                cursor.execute(f"UPDATE STUDENT SET {set_clause} WHERE NAME=?", values + (mapped_row.get('NAME'),))
            else:
                columns = ", ".join(mapped_row.keys())
                placeholders = ", ".join(["?" for _ in mapped_row])
                values = tuple(mapped_row.values())
                cursor.execute(f"INSERT INTO STUDENT ({columns}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()

# Defining your prompts
sql_prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name STUDENT and has the following columns NAME, CLASS, SECTION, GENDER.

For example:
Example 1: How many entries of records are present?
The SQL command will be something like this: SELECT COUNT(*) FROM STUDENT;

Example 2: Tell me all the students studying in Data Science class?
The SQL command will be something like this: SELECT * FROM STUDENT where CLASS="Data Science";

The SQL code should not have ' in the beginning or end and 'sql' word in output.
"""

modification_prompt = """
You are an expert in converting English commands to SQL queries for database modification!
The SQL database has the name STUDENT and has the following columns NAME, CLASS, SECTION, GENDER.

For example:
Example 1: A new student named John is added to the class 6th, section B, and gender Male.
The SQL command will be something like this: INSERT INTO STUDENT (NAME, CLASS, SECTION, GENDER) VALUES ('John', '6th', 'B', 'Male');

Example 2: Remove the student named John.
The SQL command will be something like this: DELETE FROM STUDENT WHERE NAME='John';

Example 3: Change the class of the student named John to 7th.
The SQL command will be something like this: UPDATE STUDENT SET CLASS='7th' WHERE NAME='John';

The SQL code should not have ' in the beginning or end and 'sql' word in output.
"""

# Streamlit Page Configuration
st.set_page_config(
    page_title="Text to SQL and Student Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    body {
        color: #fff;
        background-color: #0e1117;
    }
    .main {
        background-color: #1a1b21;
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        color: #1DB954;
        text-align: center;
        font-size: 2.5em;
    }
    .input-section, .dashboard-section, .modification-section, .upload-section {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-section {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
    }
    .error {
        background-color: #2c2f36;
        padding: 15px;
        border-radius: 10px;
        color: #d32f2f;
    }
    .stTextInput>div>div>input {
        background-color: #3c404a;
        color: #fff;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #1DB954;
        color: #fff;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1ed760;
        color: #fff;
    }
    .metric-card {
        background-color: #3c404a;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #1DB954;
    }
    .metric-label {
        font-size: 0.9em;
        color: #a0a0a0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Menu")
st.sidebar.markdown("Navigate through the options:")
page = st.sidebar.selectbox("Choose a page", ["Text to SQL", "Student Dashboard", "Modify Student Data"])

if page == "Text to SQL":
    # Streamlit App for Text to SQL
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Text to SQL</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    question = st.text_input("Enter your question:")
    if st.button("Submit"):
        if question:
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.write("Generating SQL query...")
            sql_query = generate_sql_query(sql_prompt, question)
            st.write(f"Generated SQL query: {sql_query}")
            
            st.write("Fetching data from the database...")
            db_path = 'student.db'
            try:
                results = read_sql_query(sql_query, db_path)
                if not results.empty:
                    st.write("Query Results:")
                    st.dataframe(results)
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

elif page == "Student Dashboard":
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Student Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    db_path = 'student.db'
    
    if st.button("Refresh Data"):
        st.experimental_rerun()
    
    try:
        conn = sqlite3.connect(db_path)
        st.write("Connected to database successfully!")
        st.write("Fetching data from the database...")
        sql = "SELECT * FROM STUDENT"
        results = read_sql_query(sql, db_path)
        if not results.empty:
            st.write("Students Data:")
            st.dataframe(results)

            # Plotting insights
            st.write("Class Distribution:")
            class_count = results['CLASS'].value_counts().reset_index()
            class_count.columns = ['CLASS', 'COUNT']
            fig = px.bar(class_count, x='CLASS', y='COUNT', title="Class Distribution")
            st.plotly_chart(fig)

            st.write("Gender Distribution:")
            gender_count = results['GENDER'].value_counts().reset_index()
            gender_count.columns = ['GENDER', 'COUNT']
            fig = px.pie(gender_count, names='GENDER', values='COUNT', title="Gender Distribution")
            st.plotly_chart(fig)
            
        else:
            st.write("No data available.")
    except Exception as e:
        st.markdown('<div class="error">', unsafe_allow_html=True)
        st.write(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Modify Student Data":
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Modify Student Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="modification-section">', unsafe_allow_html=True)

    modification_type = st.radio("Select Modification Type", ["Add Student", "Remove Student", "Update Student"])

    if modification_type == "Add Student":
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        question = st.text_input("Enter your command to add a student:")
        if st.button("Submit Add Command"):
            if question:
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.write("Generating SQL query...")
                sql_query = generate_sql_query(modification_prompt, question)
                st.write(f"Generated SQL query: {sql_query}")

                st.write("Executing SQL command...")
                db_path = 'student.db'
                try:
                    execute_sql_query(sql_query, db_path)
                    st.success("Student data added successfully!")
                except Exception as e:
                    st.markdown('<div class="error">', unsafe_allow_html=True)
                    st.write(f"Error: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Please enter a command.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("Please ensure your Excel file has columns matching the database (NAME, CLASS, SECTION, GENDER).")
        uploaded_file = st.file_uploader("Upload Excel file to add students", type=['xls', 'xlsx'])
        if uploaded_file:
            try:
                process_excel_file(uploaded_file, 'student.db', action="add")
                st.success("Data updated successfully!")
            except Exception as e:
                st.error(f"Error processing Excel file: {str(e)}")
        else:
            st.write("Please upload an Excel file.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif modification_type == "Remove Student":
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        question = st.text_input("Enter your command to remove a student:")
        if st.button("Submit Remove Command"):
            if question:
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.write("Generating SQL query...")
                sql_query = generate_sql_query(modification_prompt, question)
                st.write(f"Generated SQL query: {sql_query}")

                st.write("Executing SQL command...")
                db_path = 'student.db'
                try:
                    execute_sql_query(sql_query, db_path)
                    st.success("Student data removed successfully!")
                except Exception as e:
                    st.markdown('<div class="error">', unsafe_allow_html=True)
                    st.write(f"Error: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Please enter a command.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("Please ensure your Excel file has a column named 'NAME' with the names of students to remove.")
        uploaded_file = st.file_uploader("Upload Excel file to remove students", type=['xls', 'xlsx'])
        if uploaded_file:
            try:
                process_excel_file(uploaded_file, 'student.db', action="remove")
                st.success("Data updated successfully!")
            except Exception as e:
                st.error(f"Error processing Excel file: {str(e)}")
        else:
            st.write("Please upload an Excel file.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif modification_type == "Update Student":
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        question = st.text_input("Enter your command to update a student:")
        if st.button("Submit Update Command"):
            if question:
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.write("Generating SQL query...")
                sql_query = generate_sql_query(modification_prompt, question)
                st.write(f"Generated SQL query: {sql_query}")

                st.write("Executing SQL command...")
                db_path = 'student.db'
                try:
                    execute_sql_query(sql_query, db_path)
                    st.success("Student data updated successfully!")
                except Exception as e:
                    st.markdown('<div class="error">', unsafe_allow_html=True)
                    st.write(f"Error: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Please enter a command.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("Please ensure your Excel file has columns matching the database (NAME, CLASS, SECTION, GENDER).")
        uploaded_file = st.file_uploader("Upload Excel file to update students", type=['xls', 'xlsx'])
        if uploaded_file:
            try:
                process_excel_file(uploaded_file, 'student.db', action="modify")
                st.success("Data updated successfully!")
            except Exception as e:
                st.error(f"Error processing Excel file: {str(e)}")
        else:
            st.write("Please upload an Excel file.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
