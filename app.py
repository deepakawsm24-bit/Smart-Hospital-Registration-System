import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random
conn = sqlite3.connect("hospital.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS patients(patient_id TEXT, name TEXT, dob TEXT, gender TEXT, aadhaar TEXT, address TEXT, phone TEXT, department TEXT, visit_type TEXT, registration_time TEXT)""")
conn.commit()
st.set_page_config(page_title="Smart Hospital Registration System", layout ="wide")
st.title("Smart Hospital Registration & Admission System")
menu = st.radio("Select Option",["Dashboard","New Registration","Search Patient","View ALL Patients","Update Patient"])
if menu == "New Registration":
    patient_id = "PAT" + str(random.randint(1000,9999))
    st.subheader("Patient Registration Form")
    name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender",["Male","Female","Others"])
    aadhaar = st.text_input("Aadhaar Number")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    payment_type = st.selectbox("Payment Type",["Cash","Insurance","Corporate","PSU","ECHS"])
    department = st.selectbox("Department",["Cardiology","Orthopedic","Neurology","General Medicine","Pediatrics"])
    visit_type = st.radio("Visit Type",["OPD","IPD"])
if st.button("Register Patient"):
    existing_patient = cursor.execute("SELECT * FROM patients WHERE aadhaar =? or phone =?",(aadhaar, phone)).fetchone()
    if existing_patient:
        st.warning("Patient Already Registered")
        st.write("Patient ID:",existing_patient[0])
        st.write("Name:", existing_patient[1])
        st.write("DOB:", existing_patient[2])
        st.write("Gender:", existing_patient[3])
        st.write("Aadhaar:", existing_patient[4])
        st.write("Phone:", existing_patient[5])
        st.write("Address:", existing_patient[6])
        st.write("Department:", existing_patient[7])
        st.write("Visit Type:", existing_patient[8])
        st.write("Registration Time:", existing_patient[9])
else:
    cursor.execute("INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?)",(patient_id,str(name),str(dob),str(gender),str(aadhaar),str(phone),str(address),str(department),str(visit_type),str(datetime.now())))       
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
    st.subheader("All Patients Records")
    if st.button("View All Patients"):
        df = pd.read_sql_query("SELECT * FROM patients",conn)
        st.dataframe(df)
    st.subheader("Search Patient")
    search_id = st.text_input("Enter Patient ID")
    if st.button("Search Patient"):
        result = cursor.execute("SELECT * FROM patients WHERE patient_id=?",(search_id,)).fetchone()
        if result:
            st.success("Patient Found")
            st.write(result)
        else:
            st.error("Patient Not Found")
