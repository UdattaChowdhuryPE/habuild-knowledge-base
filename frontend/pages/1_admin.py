import streamlit as st
from frontend.utils.auth import init_session_state, is_authenticated, is_hr, logout, LOCATIONS
from frontend.utils.api import client
from frontend.utils.styles import inject_global_styles, page_header, section_header, sidebar_brand, sidebar_user_card
import pandas as pd

st.set_page_config(page_title="Admin Panel", layout="wide")

inject_global_styles()
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
    sidebar_brand()
    sidebar_user_card(st.session_state.name, "", "HR Admin")

    if st.button("← Back to Chat", use_container_width=True):
        st.switch_page("app.py")

    if st.button("Logout", use_container_width=True):
        logout()

page_header("⚙️", "HR Admin Panel", "Manage policies, employees, and documents")

# Tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["Policies", "Employees", "Documents"])

# ========== TAB 1: POLICIES ==========
with tab1:
    section_header("HR Policies")

    # Fetch and display policies
    try:
        policies_data = client.get_policies()
        policies = policies_data.get("policies", [])

        if policies:
            st.markdown(f'<span class="hb-badge">📌 {len(policies)} policies</span>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)

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

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    section_header("Add New Policy")
    st.markdown('<div class="hb-card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


# ========== TAB 2: EMPLOYEES ==========
with tab2:
    section_header("Employee Management")

    st.markdown("""
    <div class="hb-card">
    <p style="margin:0;color:#5A7A7A;font-size:0.875rem">Upload an employee list (CSV or Excel) to update employees for specific locations.<br>
    <strong style="color:#003E50">Required columns:</strong> Name, Email, Location, Role</p>
    </div>
    """, unsafe_allow_html=True)

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
    section_header("Document Management")

    # Display uploaded documents
    try:
        docs_data = client.get_documents()
        documents = docs_data.get("documents", [])

        if documents:
            st.markdown(f'<span class="hb-badge">📄 {len(documents)} documents</span>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)

            for doc in documents:
                st.markdown('<div class="hb-card" style="padding:0.75rem 1rem">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No documents uploaded yet")

    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    section_header("Upload New Document")
    st.markdown('<div class="hb-card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)
