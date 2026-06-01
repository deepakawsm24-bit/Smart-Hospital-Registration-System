import streamlit as st
st.title("Smart Hospital Registration System")

st.header("Patient Registration Form")

name = st.text_input("Patient Name")
dob = st.text_input("Date of Birth")
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
aadhaar = st.text_input("Aadhaar Number")
phone = st.text_input("Phone Number")
address = st.text_area("Address")

if st.button("Register Patient"):
    st.success("Patient Registered Successfully")

    st.write("### Patient Details")
    st.write("Name:",name)
    st.write("DOB:",dob)
    st.write("Gender:",gender)
    st.write("Aadhaar:",aadhaar)
    st.write("Phone:",phone)
    st.write("Address:",address)
