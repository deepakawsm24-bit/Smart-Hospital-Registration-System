import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random
conn = sqlite3.connect("hospital.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS patients(patient_id TEXT, name TEXT, dob TEXT, gender TEXT, aadhaar TEXT, phone TEXT, address TEXT, phone TEXT, department TEXT, visit_type TEXT, registration_time TEXT)""")
conn.commit()
st.set_page_config(page_title="Smart Hospital Registration System", layout ="wide")
st.title("Smart Hospital Registration & Admission System")
patient_id = "PAT" + str(random.randint(1000,9999))
st.subheader("Patient Registration Form")
name = st.text_input("Patient Name")
dob = st.date_input("Date of Birth")
gender = st.selectbox("Gender",["Male","Female","Others"])
aadhaar = st.text_input("Aadhaar Number")
phone = st.text_input("Phone Number")
address = st.text_area("Address")
department = st.selectbox("Department",["Cardiology","Orthopedic","Neurology","General Medicine","Pediatrics"])
visit_type = st.radio("Visit Type",["OPD","IPD"])
if st.button("Register Patient"):
    cursor.execute("INSERT INTO patients VALUES
(?,?,?,?,?,?,?,?,?)",
    (
        patient_id,
        str(name),
        str(dob),
        str(gender),
        str(aadhaar),
        str(phone),
        str(address),
        str(department),
        str(visit_type),
        str(datetime.now()))       
    conn.commit()                                                                        
    st.success("Patient Registered Successfully")
    st.write("##Registration Details")
    st.write("Patient ID:",patient_id)
    st.write("Name:", name)
    st.write("DOB:", dob)
    st.write("Gender:", gender)
    st.write("Aadhaar:", aadhaar)
    st.write("Phone:", phone)
    st.write("Address:", address)
    st.write("Department:", department)
    st.write("Visit Type:", visit_type)
    st.write("Registration Time:", datetime.now())
