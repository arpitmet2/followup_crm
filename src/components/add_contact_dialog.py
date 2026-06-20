import streamlit as st
from src.database.db import (
   create_contact,
   check_contact_exists_for_admin
)
from datetime import datetime

@st.dialog("➕ Add New Contact")
def add_contact_dialog():

    name = st.text_input("Name *")
    phone = st.text_input("Phone *")
    email = st.text_input("Email")
    discussion = st.text_area("Discussion")


    followup_date = st.date_input("Next Follow-Up Date")
    followup_time = st.time_input("Next Follow-Up Time")

    next_followup = datetime.combine(
        followup_date,
        followup_time
    )

    if st.button("Save Contact"):

        if not name:
            st.error("Name is required")
            return

        if not phone:
            st.error("Phone is required")
            return

        admin_id = st.session_state.admin["admin_id"]

        existing_contact = check_contact_exists_for_admin(
            phone=phone,
            email=email,
            admin_id=admin_id
        )

        if existing_contact:
            st.toast(
                "Contact/lead already created for this login user.",
                icon="⚠️"
            )
            st.warning("Contact/lead already exists.")
            st.write("Already created contact:")
            st.dataframe(
                [existing_contact],
                use_container_width=True,
                hide_index=True
            )
            return

        create_contact(
            name=name,
            phone=phone,
            email=email,
            discussion=discussion,
            next_followup_at=str(next_followup),
            admin_id=admin_id
        )

        st.success("Contact created successfully")
        st.rerun()
