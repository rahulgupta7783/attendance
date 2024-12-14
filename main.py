import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import os
import pandas as pd


# Function to initialize database and CSV file
import sqlite3
import os

# Function to initialize database and CSV file
def init_db():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Create the table with the required schema if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        employee_name TEXT,
        selfie_name TEXT,
        timestamp TEXT  -- Add timestamp column
    )
    """)

    conn.commit()
    conn.close()

    # Create or load the CSV file
    if not os.path.exists("attendance.csv"):
        df = pd.DataFrame(columns=["employee_id", "employee_name", "selfie_name", "timestamp"])
        df.to_csv("attendance.csv", index=False)

# Initialize database
init_db()




# Function to check if attendance is already marked
def has_attended_today(employee_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT timestamp FROM attendance 
    WHERE employee_id = ? ORDER BY timestamp DESC LIMIT 1
    """, (employee_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        last_attendance_time = datetime.fromisoformat(result[0])
        if datetime.now() - last_attendance_time < timedelta(days=1):
            return True
    return False


# Function to save attendance
def mark_attendance(employee_id, employee_name, selfie_path):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    selfie_name = os.path.basename(selfie_path)

    # Insert into database
    cursor.execute("""
    INSERT INTO attendance (employee_id, employee_name, selfie_name, timestamp) 
    VALUES (?, ?, ?, ?)
    """, (employee_id, employee_name, selfie_name, timestamp))
    conn.commit()
    conn.close()

    # Update the CSV file
    df = pd.read_csv("attendance.csv")
    new_row = {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "selfie_name": selfie_name,
        "timestamp": timestamp
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("attendance.csv", index=False)


# Initialize database and CSV file
init_db()

# Streamlit UI
st.title("Employee Attendance System")

# Get user input
employee_id = st.text_input("Enter Employee ID")
employee_name = st.text_input("Enter Employee Name")
uploaded_file = st.file_uploader("Upload your selfie", type=["png", "jpg", "jpeg"])

if st.button("Mark Attendance"):
    if not employee_id or not employee_name:
        st.error("Please enter both Employee ID and Employee Name.")
    elif not uploaded_file:
        st.error("Please upload a selfie.")
    else:
        # Save selfie locally
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        selfie_name = f"{employee_id}_{timestamp}.jpg"
        selfie_path = os.path.join("selfies", selfie_name)
        os.makedirs("selfies", exist_ok=True)

        # Save the selfie file
        with open(selfie_path, "wb") as f:
            f.write(uploaded_file.read())

        # Check if attendance is already marked
        if has_attended_today(employee_id):
            st.warning("You have already marked attendance today.")
        else:
            # Mark attendance
            mark_attendance(employee_id, employee_name, selfie_path)
            st.success("Attendance marked successfully!")

# Show attendance data (for admin purposes)
if st.checkbox("Show Attendance Data"):
    # Load data from the CSV file
    if os.path.exists("attendance.csv"):
        df = pd.read_csv("attendance.csv")
        st.dataframe(df)
    else:
        st.warning("No attendance data available.")
