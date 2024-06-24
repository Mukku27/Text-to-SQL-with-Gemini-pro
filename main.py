import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro model
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    return response.text 

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
    .input-section, .dashboard-section, .modification-section {
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
            sql_query = get_gemini_response(question, sql_prompt).strip()
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

    # Load data
    db_path = 'student.db'
    df = read_sql_query("SELECT * FROM STUDENT", db_path)

    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df.shape[0]:,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Students</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["CLASS"].nunique():,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Classes</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["SECTION"].nunique():,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Sections</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        avg_class_size = df.groupby('CLASS').size().mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{avg_class_size:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Avg Class Size</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["GENDER"].nunique()}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Genders</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("Gender Distribution")
        gender_counts = df['GENDER'].value_counts()
        fig = px.pie(values=gender_counts.values, names=gender_counts.index, hole=0.3)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("Section-wise Distribution")
        section_counts = df['SECTION'].value_counts()
        fig = px.pie(values=section_counts.values, names=section_counts.index, hole=0.3)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("Students per Class")
    class_counts = df['CLASS'].value_counts().sort_values(ascending=True)
    fig = px.bar(x=class_counts.values, y=class_counts.index, orientation='h')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Number of Students",
        yaxis_title="Class"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Existing functionality
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    
    # Display all students
    st.subheader("All Students")
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No students found.")

    # Search for students by name
    st.subheader("Search Students by Name")
    name = st.text_input("Enter student name:")
    if st.button("Search"):
        search_results = df[df['NAME'].str.contains(name, case=False, na=False)]
        if not search_results.empty:
            st.dataframe(search_results)
        else:
            st.write("No students found.")

    # Filter students by class or section
    st.subheader("Filter Students by Class or Section")
    filter_class = st.text_input("Enter class:")
    filter_section = st.text_input("Enter section:")
    if st.button("Filter"):
        filter_results = df[(df['CLASS'].str.contains(filter_class, case=False, na=False)) & 
                            (df['SECTION'].str.contains(filter_section, case=False, na=False))]
        if not filter_results.empty:
            st.dataframe(filter_results)
        else:
            st.write("No students found.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Modify Student Data":
    # Streamlit App for Modifying Student Data
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Modify Student Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="modification-section">', unsafe_allow_html=True)

    modification_prompt_text = st.text_area("Enter your modification prompt (e.g., 'A new student named John is added to the class 6th, section B, and gender Male.'):")
    if st.button("Execute"):
        if modification_prompt_text:
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.write("Generating SQL modification query...")
            modification_sql_query = get_gemini_response(modification_prompt_text, modification_prompt).strip()
            st.write(f"Generated SQL query: {modification_sql_query}")
            
            st.write("Executing SQL query on the database...")
            db_path = 'student.db'
            try:
                execute_sql_query(modification_sql_query, db_path)
                st.write("Database modification executed successfully.")
            except Exception as e:
                st.markdown('<div class="error">', unsafe_allow_html=True)
                st.write(f"Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write("Please enter a modification prompt.")
    else:
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)