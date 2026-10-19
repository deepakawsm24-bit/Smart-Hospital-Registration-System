
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import date, datetime
from supabase import create_client

st.set_page_config(
    page_title="Smart Hospital Information System",
    layout="wide"
)

# ---------- SUPABASE CONNECTION ----------
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

st.title("Smart Hospital Information System")

try:
    supabase = get_supabase()
    # Verify that the table exists and is accessible.
    supabase.table("patients").select("patient_id").limit(1).execute()
except Exception as e:
    st.error("Supabase connection failed. Check your secrets and table name.")
    st.caption(str(e))
    st.stop()

TABLE = "patients"

MENU = [
    "Dashboard",
    "New Registration",
    "Search Patient",
    "View All Patients",
    "Update Patient",
    "Delete Patient",
    "AI Admission Assistant",
    "Document Center",
    "Document History"
]

menu = st.sidebar.radio("Select Option", MENU)


# ---------- HELPERS ----------
def get_patients():
    result = supabase.table(TABLE).select("*").execute()
    return result.data or []


def find_patient(patient_id):
    result = (
        supabase.table(TABLE)
        .select("*")
        .eq("patient_id", patient_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def upload_document(patient_id, uploaded_file):
    # Requires a private Supabase Storage bucket named patient-documents.
    safe_name = uploaded_file.name.replace("/", "_").replace("\\", "_")
    path = f"{patient_id}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"

    supabase.storage.from_("patient-documents").upload(
        path,
        uploaded_file.getvalue(),
        {"content-type": uploaded_file.type or "application/octet-stream"}
    )
    return path


# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("Hospital Dashboard")

    try:
        patients = get_patients()
        df = pd.DataFrame(patients)

        if df.empty:
            st.info("No patient records found.")
        else:
            total = len(df)
            male = int((df["gender"] == "Male").sum()) if "gender" in df else 0
            female = int((df["gender"] == "Female").sum()) if "gender" in df else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Patients", total)
            c2.metric("Male Patients", male)
            c3.metric("Female Patients", female)

            st.subheader("Recent Patients")
            st.dataframe(df.tail(10), use_container_width=True)

            if "department" in df:
                st.subheader("Department-wise Patients")
                st.bar_chart(df["department"].value_counts())

    except Exception as e:
        st.error(f"Dashboard error: {e}")


# ---------- NEW REGISTRATION ----------
elif menu == "New Registration":
    st.subheader("Patient Registration Form")

    with st.form("registration_form"):
        name = st.text_input("Patient Name")
        dob = st.date_input(
            "Date of Birth",
            min_value=date(1940, 1, 1),
            max_value=date.today()
        )
        gender = st.selectbox("Gender", ["Male", "Female", "Others"])
        aadhaar = st.text_input("Aadhaar Number")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")

        payment_type = st.selectbox(
            "Payment Type",
            ["Cash", "Insurance", "Corporate", "PSU", "ECHS"]
        )
        department = st.selectbox(
            "Department",
            [
                "Cardiology", "Orthopedic", "Neurology",
                "General Medicine", "Pediatrics"
            ]
        )
        visit_type = st.radio("Visit Type", ["OPD", "IPD"])

        photo = st.file_uploader(
            "Upload Patient Photo",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button("Register Patient")

    if submitted:
        if not name.strip() or not phone.strip():
            st.error("Patient name and phone number are required.")
        else:
            try:
                existing = (
                    supabase.table(TABLE)
                    .select("patient_id")
                    .eq("phone", phone.strip())
                    .limit(1)
                    .execute()
                )

                if existing.data:
                    st.warning("This phone number is already registered.")
                else:
                    patient_id = (
                        "PAT-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
                    )

                    photo_path = None
                    if photo is not None:
                        photo_path = upload_document(patient_id, photo)

                    record = {
                        "patient_id": patient_id,
                        "name": name.strip(),
                        "dob": str(dob),
                        "gender": gender,
                        "aadhaar": aadhaar.strip() or None,
                        "address": address.strip(),
                        "payment_type": payment_type,
                        "phone": phone.strip(),
                        "department": department,
                        "visit_type": visit_type,
                        "photo_path": photo_path,
                        "registration_time": datetime.now().astimezone().isoformat()
                    }

                    supabase.table(TABLE).insert(record).execute()

                    st.success(f"Patient registered successfully: {patient_id}")

                    qr = qrcode.make(
                        f"Patient ID: {patient_id}\nName: {name}"
                    )
                    buffer = BytesIO()
                    qr.save(buffer, format="PNG")
                    st.image(buffer.getvalue(), caption="Patient QR Code")

            except Exception as e:
                st.error("Registration failed. Check the table columns and Storage setup.")
                st.caption(str(e))


# ---------- SEARCH PATIENT ----------
elif menu == "Search Patient":
    st.subheader("Search Patient")
    search_id = st.text_input("Enter Patient ID")

    if st.button("Search"):
        if search_id.strip():
            try:
                patient = find_patient(search_id.strip())
                if patient:
                    st.success("Patient Found")
                    st.json(patient)
                else:
                    st.warning("Patient not found.")
            except Exception as e:
                st.error(f"Search failed: {e}")


# ---------- VIEW ALL PATIENTS ----------
elif menu == "View All Patients":
    st.subheader("All Patient Records")

    try:
        patients = get_patients()
        df = pd.DataFrame(patients)

        if df.empty:
            st.info("No patient records found.")
        else:
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download Patient Records CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="patients.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Unable to load patients: {e}")


# ---------- UPDATE PATIENT ----------
elif menu == "Update Patient":
    st.subheader("Update Patient")
    update_id = st.text_input("Enter Patient ID")

    if st.button("Find Patient"):
        try:
            patient = find_patient(update_id.strip())
            if patient:
                st.session_state["edit_patient"] = patient
            else:
                st.session_state.pop("edit_patient", None)
                st.warning("Patient ID not found.")
        except Exception as e:
            st.error(f"Lookup failed: {e}")

    patient = st.session_state.get("edit_patient")

    if patient:
        with st.form("update_form"):
            new_name = st.text_input("Patient Name", patient.get("name") or "")
            new_phone = st.text_input("Phone", patient.get("phone") or "")
            new_address = st.text_area("Address", patient.get("address") or "")
            save = st.form_submit_button("Save Changes")

        if save:
            try:
                supabase.table(TABLE).update({
                    "name": new_name.strip(),
                    "phone": new_phone.strip(),
                    "address": new_address.strip()
                }).eq("patient_id", patient["patient_id"]).execute()

                st.session_state.pop("edit_patient", None)
                st.success("Patient updated successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")


# ---------- DELETE PATIENT ----------
elif menu == "Delete Patient":
    st.subheader("Delete Patient")
    st.warning("Deletion is permanent unless a backup is available.")

    delete_id = st.text_input("Enter Patient ID to delete")
    confirm = st.checkbox("I confirm that I want to permanently delete this record.")

    if st.button("Delete Patient", type="primary"):
        if not confirm:
            st.warning("Please confirm before deleting.")
        elif not delete_id.strip():
            st.warning("Enter a Patient ID.")
        else:
            try:
                patient = find_patient(delete_id.strip())
                if not patient:
                    st.warning("Patient not found.")
                else:
                    supabase.table(TABLE).delete().eq(
                        "patient_id", delete_id.strip()
                    ).execute()
                    st.success("Patient record deleted.")
            except Exception as e:
                st.error(f"Deletion failed: {e}")


# ---------- AI ADMISSION ASSISTANT ----------
elif menu == "AI Admission Assistant":
    st.subheader("AI Admission Assistant")
    symptoms = st.text_area("Enter symptoms")

    if st.button("Suggest Department"):
        text = symptoms.lower()

        if any(word in text for word in ["chest pain", "chest pressure"]):
            st.warning("Chest pain can be an emergency. Seek urgent medical assessment.")
            st.info("Possible department: Emergency / Cardiology")
        elif any(word in text for word in ["fever", "cough"]):
            st.info("Possible department: General Medicine")
        elif any(word in text for word in ["bone", "fracture"]):
            st.info("Possible department: Orthopedic")
        elif any(word in text for word in ["skin", "allergy"]):
            st.info("Possible department: Dermatology")
        else:
            st.info("Please consult a qualified clinician for assessment.")


# ---------- DOCUMENT CENTER ----------
elif menu == "Document Center":
    st.subheader("Patient Document Upload")
    patient_id = st.text_input("Patient ID")
    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if st.button("Upload Document"):
        if not patient_id.strip() or uploaded_file is None:
            st.warning("Enter a Patient ID and select a document.")
        else:
            try:
                patient = find_patient(patient_id.strip())
                if not patient:
                    st.error("Patient ID not found.")
                else:
                    path = upload_document(patient_id.strip(), uploaded_file)

                    # Store document metadata in Supabase.
                    supabase.table("patient_documents").insert({
                        "patient_id": patient_id.strip(),
                        "file_name": uploaded_file.name,
                        "storage_path": path,
                        "uploaded_at": datetime.now().astimezone().isoformat()
                    }).execute()

                    st.success("Document uploaded successfully.")
            except Exception as e:
                st.error("Upload failed. Check Storage bucket and patient_documents table.")
                st.caption(str(e))


# ---------- DOCUMENT HISTORY ----------
elif menu == "Document History":
    st.subheader("Patient Document History")
    patient_id = st.text_input("Enter Patient ID")

    if st.button("Show Documents"):
        try:
            docs = (
                supabase.table("patient_documents")
                .select("*")
                .eq("patient_id", patient_id.strip())
                .execute()
            )

            if not docs.data:
                st.info("No documents found.")
            else:
                for doc in docs.data:
                    st.write(doc.get("file_name", "Document"))
                    if st.button(
                        f"Create download link: {doc.get('file_name')}",
                        key=f"download_{doc.get('id', doc.get('storage_path'))}"
                    ):
                        link = supabase.storage.from_(
                            "patient-documents"
                        ).create_signed_url(doc["storage_path"], 60)
                        st.link_button(
                            "Download document",
                            link["signedURL"]
                        )
        except Exception as e:
            st.error("Could not load document history.")
            st.caption(str(e))
