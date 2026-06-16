import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random
conn = sqlite3.connect("hospital.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS patients(patient_id TEXT, name TEXT, dob TEXT, gender TEXT, aadhaar TEXT, address TEXT, payment_type TEXT, phone TEXT, department TEXT, visit_type TEXT, registration_time TEXT)""")
conn.commit()
st.set_page_config(page_title="Smart Hospital Registration System", layout ="wide")
st.title("Smart Hospital Registration & Admission System")
menu = st.radio("Select Option",["Dashboard","New Registration","Search Patient","View ALL Patients","Update Patient","Delete Patient","AI Admission Assistant"])
if menu == "AI Admission Assistant":
    st.subheader("AI Admission Assistant")
    symptoms = st.text_area("Enter Patient Symptoms")
    if st.button("Analyze Symptoms"):
        symptoms = symptoms.lower()
        if "fever" in symptoms or "cough" in symptoms:
            st.success("Recommended Department: General Medicine")
        elif " chest pain" in symptoms:
            st.success("Recommended Department: Cardiology")
        elif "bone" in symptoms or "fracture" in symptoms:
            st.success ("Recommended Department: Orthopedic")
        elif "skin" in symptoms or "allergy" in symptoms:
            st.success("Recommended Department: Dermatology")
        else: 
            st.warning("Please Consult General Physician")

if menu =="Dashboard":
    st.subheader("Hospital Dashboard")
    total_patients = cursor.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    male_patients = cursor.execute("SELECT COUNT(*) FROM patients WHERE gender='Male'").fetchone()[0]
    female_patients = cursor.execute("SELECT COUNT(*) FROM patients WHERE gender ='Female'").fetchone()[0]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients",total_patients)
    with col2:
        st.metric("Male Patients",male_patients)
    with col3:
        st.metric("Female Patients",female_patients)
        today_patients = cursor.execute(""" SELECT COUNT(*) FROM patients WHERE date(registration_time)=date('now')""").fetchone()[0]
        st.metric("Today's Registration",today_patients)
        st.markdown("_ _ _ ")
        st.subheader("Patient Distribution")
        chart_data = pd.DataFrame({"Category":["Male","Female"],"Count":[male_patients,female_patients]})
        st.bar_chart(chart_data.set_index("Category"))
        st.markdown("_ _ _")
        st.subheader("Recent Patients")
        df = pd.read_sql_query("SELECT patient_id, name, gender FROM patients",conn)
        st.dataframe(df)
        department_count = cursor.execute(""" SELECT department, COUNT(*) FROM patients GROUP BY department """).fetchall()
        if department_count : dept_df = pd.DataFrame(department_count,columns=["Department","Patients"])
        st.subheader("Department Wise Patients")
        st.bar_chart(dept_df.set_index("Department"))
        
if menu == "New Registration":
    patient_id = "PAT" + str(random.randint(1000,9999))
    st.write("Patient ID:", patient_id)

    st.subheader("Patient Registration Form")

    name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender",["Male","Female","Others"])
    aadhaar = st.text_input("Aadhaar Number")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    payment_type = st.selectbox(
        "Payment Type",
        ["Cash","Insurance","Corporate","PSU","ECHS"]
    )

    department = st.selectbox(
        "Department",
        ["Cardiology","Orthopedic","Neurology",
         "General Medicine","Pediatrics"]
    )

    visit_type = st.radio("Visit Type",["OPD","IPD"])

    if st.button("Register Patient"):

        existing_patient = cursor.execute(
            "SELECT * FROM patients WHERE aadhaar=? OR phone=?",
            (aadhaar, phone)
        ).fetchone()

        if existing_patient:
            st.warning("Patient Already Registered")

        else:
            cursor.execute(
                "INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    patient_id,
                    str(name),
                    str(dob),
                    str(gender),
                    str(aadhaar),
                    str(address),
                    str(payment_type),
                    str(phone),
                    str(department),
                    str(visit_type),
                    str(datetime.now())
                )
            )

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
if  st.button("View All Patients"):
    df = pd.read_sql_query("SELECT * FROM patients",conn)
    st.dataframe(df)
    excel = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Patient Records", data=excel,file_name="Patients.csv",mime="text/csv")
    st.subheader("Search Patient")
    search_id = st.text_input("Enter Patient ID")
    if st.button("Search Patient"):
        result = cursor.execute("SELECT * FROM patients WHERE patient_id=?",(search_id,)).fetchone()
        if result:
            st.success("Patient Found")
            st.write(result)
        else:
            st.error("Patient Not Found")


if menu == "Delete Patient":
    st.subheader("Delete Patient")

    delete_id = st.text_input("Enter Patient ID")

    if st.button("Delete Patient"):
        cursor.execute(
            "DELETE FROM patients WHERE patient_id=?",
            (delete_id,)
        )
        conn.commit()

        st.success("Patient Deleted Successfully")

if menu == "Update Patient":

    st.subheader("Update Patient")

    update_id = st.text_input("Enter Patient ID")

    if update_id:

        result = cursor.execute(
            "SELECT * FROM patients WHERE patient_id=?",
            (update_id,)
        ).fetchone()

        if result:

            new_name = st.text_input("Patient Name", result[1])
            new_phone = st.text_input("Phone", result[8])

            if st.button("Save Changes"):

                cursor.execute(
                    "UPDATE patients SET name=?, phone=? WHERE patient_id=?",
                    (new_name, new_phone, update_id)
                )

                conn.commit()

                st.success("Patient Updated Successfully")

        else:
            st.error("Patient ID not found")























