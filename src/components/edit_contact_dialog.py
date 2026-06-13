from datetime import date, datetime

import streamlit as st

from src.database.db import (
    check_contact_exists_for_admin,
    update_contact
)


CONTACT_STATUSES = [
    "New",
    "Contacted",
    "Interested",
    "Follow Up",
    "Site Visit",
    "Negotiation",
    "Booked",
    "Lost"
]


def parse_followup_date(value):
    if not value:
        return date.today()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return date.today()


@st.dialog("✏️ Edit Contact")
def edit_contact_dialog(contact):
    contact_id = contact["contact_id"]
    admin_id = st.session_state.admin["admin_id"]

    name = st.text_input(
        "Name *",
        value=contact.get("name") or "",
        key=f"edit_name_{contact_id}"
    )
    phone = st.text_input(
        "Phone *",
        value=contact.get("phone") or "",
        key=f"edit_phone_{contact_id}"
    )
    email = st.text_input(
        "Email",
        value=contact.get("email") or "",
        key=f"edit_email_{contact_id}"
    )
    discussion = st.text_area(
        "Discussion",
        value=contact.get("short_discussion") or "",
        key=f"edit_discussion_{contact_id}"
    )

    current_status = contact.get("status") or "New"
    status_index = (
        CONTACT_STATUSES.index(current_status)
        if current_status in CONTACT_STATUSES
        else 0
    )
    status = st.selectbox(
        "Status",
        CONTACT_STATUSES,
        index=status_index,
        key=f"edit_status_{contact_id}"
    )

    next_followup = st.date_input(
        "Next Follow-Up Date",
        value=parse_followup_date(contact.get("next_followup_at")),
        key=f"edit_next_followup_{contact_id}"
    )

    if st.button("Update Contact", key=f"update_contact_{contact_id}"):
        if not name:
            st.error("Name is required")
            return

        if not phone:
            st.error("Phone is required")
            return

        existing_contact = check_contact_exists_for_admin(
            phone=phone,
            email=email,
            admin_id=admin_id,
            exclude_contact_id=contact_id
        )

        if existing_contact:
            st.toast(
                "Another contact/lead already uses this phone or email.",
                icon="⚠️"
            )
            st.warning("Duplicate contact/lead found.")
            st.write("Already created contact:")
            st.dataframe(
                [existing_contact],
                use_container_width=True,
                hide_index=True
            )
            return

        update_contact(
            contact_id=contact_id,
            admin_id=admin_id,
            name=name,
            phone=phone,
            email=email,
            discussion=discussion,
            status=status,
            next_followup_at=str(next_followup)
        )

        st.success("Contact updated successfully")
        st.rerun()
