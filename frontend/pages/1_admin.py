import streamlit as st
from frontend.utils.auth import init_session_state, is_authenticated, is_hr, logout, LOCATIONS
from frontend.utils.api import client
import pandas as pd

st.set_page_config(page_title="Admin Panel", layout="wide")

init_session_state()

# Check authentication and role
if not is_authenticated():
    st.error("Please sign in first")
    st.stop()

if not is_hr():
    st.error("You do not have permission to access this page")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("Admin Panel")
    st.write(f"**{st.session_state.name}**")

    if st.button("← Back to Chat"):
        st.switch_page("pages/app.py")

    if st.button("Logout"):
        logout()

st.title("HR Admin Panel")

# Tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["Policies", "Employees", "Documents"])

# ========== TAB 1: POLICIES ==========
with tab1:
    st.header("HR Policies")

    # Fetch and display policies
    try:
        policies_data = client.get_policies()
        policies = policies_data.get("policies", [])

        if policies:
            st.write(f"**Total Policies: {len(policies)}**")

            for policy in policies:
                with st.expander(f"📌 {policy['title']} ({policy['category']})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Category:** {policy['category']}")
                        st.write(f"**Locations:** {', '.join(policy['locations'])}")
                        st.write("**Content:**")
                        st.write(policy["content"][:500] + "..." if len(policy["content"]) > 500 else policy["content"])

                    with col2:
                        if st.button("Edit", key=f"edit_{policy['id']}"):
                            st.info("Edit functionality coming soon")

                        if st.button("Delete", key=f"delete_{policy['id']}"):
                            client.delete_policy(policy["id"])
                            st.success("Policy deleted!")
                            st.rerun()
        else:
            st.info("No policies yet")

    except Exception as e:
        st.error(f"Error loading policies: {str(e)}")

    st.divider()
    st.subheader("Add New Policy")

    with st.form("add_policy_form"):
        title = st.text_input("Policy Title")
        category = st.selectbox(
            "Category",
            ["Leave & Attendance", "Compensation & Benefits", "Compliance & Legal",
             "Code of Conduct", "Recruitment & Onboarding", "Performance & Development",
             "Health & Safety", "Remote Work", "Other"]
        )
        content = st.text_area("Policy Content", height=300)
        locations = st.multiselect("Applicable Locations", options=LOCATIONS)

        submit = st.form_submit_button("Create Policy")

        if submit:
            if not title or not content or not locations:
                st.error("Please fill in all required fields")
            else:
                try:
                    client.create_policy(
                        title=title,
                        category=category,
                        content=content,
                        locations=locations
                    )
                    st.success("Policy created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating policy: {str(e)}")


# ========== TAB 2: EMPLOYEES ==========
with tab2:
    st.header("Employee Management")

    st.write("Upload an employee list (CSV or Excel) to update employees for specific locations.")
    st.write("**Required columns:** Name, Email, Location, Role")

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("Preview:")
            st.dataframe(df)

            location = st.selectbox("Update location:", options=LOCATIONS)

            if st.button("Upload Employees"):
                # Save file temporarily and upload
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(suffix=uploaded_file.name, delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name

                try:
                    result = client.upload_employees(tmp_path, location)
                    st.success(f"Uploaded {result['count']} employees")
                    st.rerun()
                finally:
                    os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


# ========== TAB 3: DOCUMENTS ==========
with tab3:
    st.header("Document Management")

    # Display uploaded documents
    try:
        docs_data = client.get_documents()
        documents = docs_data.get("documents", [])

        if documents:
            st.write(f"**Total Documents: {len(documents)}**")

            for doc in documents:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"📄 **{doc['title']}**")
                    st.caption(f"{doc['category']} • {', '.join(doc['locations'])}")

                with col2:
                    if st.button("Download", key=f"download_{doc['id']}"):
                        st.write(f"[Click to download]({doc['file_url']})")

                with col3:
                    if st.button("Delete", key=f"delete_doc_{doc['id']}"):
                        client.delete_document(doc["id"])
                        st.success("Document deleted!")
                        st.rerun()
        else:
            st.info("No documents uploaded yet")

    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

    st.divider()
    st.subheader("Upload New Document")

    with st.form("upload_doc_form"):
        title = st.text_input("Document Title")
        category = st.selectbox(
            "Category",
            ["Health Insurance", "Claims & Reimbursement", "Onboarding",
             "Payroll & Tax", "Compliance", "General"]
        )
        locations = st.multiselect("Applicable Locations", options=LOCATIONS)
        uploaded_file = st.file_uploader("Choose file", type=["pdf", "docx", "doc", "txt"])

        submit = st.form_submit_button("Upload Document")

        if submit:
            if not title or not locations or not uploaded_file:
                st.error("Please fill in all required fields")
            else:
                try:
                    import tempfile
                    import os

                    with tempfile.NamedTemporaryFile(suffix=uploaded_file.name, delete=False) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name

                    try:
                        result = client.upload_document(
                            file_path=tmp_path,
                            title=title,
                            category=category,
                            locations=locations
                        )
                        st.success("Document uploaded successfully!")
                        st.rerun()
                    finally:
                        os.unlink(tmp_path)

                except Exception as e:
                    st.error(f"Error uploading document: {str(e)}")
