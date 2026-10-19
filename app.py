import streamlit as st
import os
import sqlite3
import pandas as pd
from datetime import datetime, date
import random
import qrcode
from PIL import Image
from io import BytesIO
conn = sqlite3.connect("hospital.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS patients(patient_id TEXT, name TEXT, dob TEXT, gender TEXT, aadhaar TEXT, address TEXT, payment_type TEXT, phone TEXT, department TEXT, visit_type TEXT, photo_path TEXT, registration_time TEXT)""")
conn.commit()
st.set_page_config(page_title="Smart Hospital Information System", layout ="wide")
st.title("Smart Hospital Information System")
menu = st.radio("Select Option",["Dashboard","New Registration","Search Patient","View ALL Patients","Update Patient","Delete Patient","AI Admission Assistant","Document Center","Document History"])
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
        department_count = cursor.execute("""
        SELECT department, COUNT(*) FROM patients GROUP BY department
        """).fetchall()
        if department_count:
            dept_df = pd.DataFrame(
                department_count,
                columns=["Department", "Patients"]
            )
            st.subheader("Department Wise Patients")
            st.bar_chart(dept_df.set_index("Department"))
        else:
            st.info("No department data available")
if menu == "New Registration":
    patient_id = "PAT" + str(random.randint(1000,9999))
    st.write("Patient ID:", patient_id)

    st.subheader("Patient Registration Form")

    name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth", min_value=date(1940,1,1),max_value=date.today())
    gender = st.selectbox("Gender",["Male","Female","Others"])
    aadhaar = st.text_input("Aadhaar Number")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    photo = st.file_uploader("Upload Patient Photo",type = ["jpg","jpeg","png"])
    if photo is not None:
        st.image(photo,caption="Patient Photo",width=200)
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
   if not name.strip() or not phone.strip():
            st.error("Patient name and phone are required.")
      else:
            existing_patient = cursor.execute(
                "SELECT * FROM patients WHERE phone=?",
                (phone.strip(),)
            ).fetchone()

            if existing_patient:
                st.warning("Patient already registered.")
            else:
                photo_path = ""

                if photo is not None:
                    os.makedirs("documents/photos", exist_ok=True)
                    photo_name = os.path.basename(photo.name)
                    photo_path = (
                        f"documents/photos/{patient_id}_{photo_name}"
                    )
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                cursor.execute(
                    """INSERT INTO patients VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        patient_id, name.strip(), str(dob),
                        gender, aadhaar.strip(), address,
                        payment_type, phone.strip(), department,
                        visit_type, photo_path, str(datetime.now())
                    )
                )
                conn.commit()
                st.success(f"Patient registered: {patient_id}")

                qr_data = f"Patient ID: {patient_id}\nName: {name}"
                qr = qrcode.make(qr_data)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                st.image(buffer.getvalue(), caption="Patient QR Code")
       
     



  
            

                    file_path = f"documents/{file}"

                    if file.endswith((".png", ".jpg", ".jpeg")):
                        st.image(file_path, width=300)

                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"Download {file}",
                                data=f.read(),
                                file_name=file
                            )

            else:
                st.warning("No Documents Found")

        except Exception as e:
            st.error(f"Error: {e}")
                                     
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























