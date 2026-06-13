import streamlit as st
from datetime import date, datetime
from src.database.db import (
    get_contact_by_id,
    get_followup_history,
    update_contact,
    create_followup,
    check_contact_exists_for_admin
)



st.set_page_config(page_title="Contact Details", layout="wide")

if "selected_contact_id" not in st.session_state:
    st.error("No contact selected.")
    st.stop()

contact_id = st.session_state.selected_contact_id
admin_id = st.session_state.selected_contact_admin_id

contact = get_contact_by_id(contact_id,admin_id)

if not contact:
    st.error("Contact not found.")
    st.stop()

st.title("📋 Contact Details")

left_col, right_col = st.columns([1, 1])

# =====================================
# LEFT SIDE
# =====================================

with left_col:

    st.subheader("Contact Information")

    name = st.text_input(
        "Name",
        value=contact["name"]
    )

    phone = st.text_input(
        "Phone",
        value=contact["phone"]
    )

    email = st.text_input(
        "Email",
        value=contact["email"] or ""
    )

    discussion = st.text_area(
        "New Discussion",
        value=contact["short_discussion"] or "",
        height=150
    )

    status_options = [
        "New",
        "Contacted",
        "Interested",
        "Follow Up",
        "Booked",
        "Lost"
    ]

    current_status_index = (
        status_options.index(contact["status"])
        if contact["status"] in status_options
        else 0
    )

    status = st.selectbox(
        "Status",
        status_options,
        index=current_status_index
    )

    next_followup = st.date_input(
        "Next Follow-Up Date",
        value=contact["next_followup_at"] or date.today()
    )

    if st.button(
        "💾 Save Follow-Up",
        use_container_width=True
    ):

        # Save activity history        
        
        # =====================================
        # CREATE ACTIVITY ONLY IF CHANGED
        # =====================================

        
        
        
        old_discussion = contact.get("short_discussion") or ""
        old_status = contact.get("status") or "New"
        old_next_followup = str(contact.get("next_followup_at") or "")

        new_discussion = discussion
        new_status = status
        new_next_followup = str(next_followup)

        activity_logs = []

        # Status Changed
        if old_status != new_status:
            activity_logs.append(
                f"🎯 Status changed: {old_status} → {new_status}"
            )

        # Followup Date Changed
        if old_next_followup != new_next_followup:
            old_date = (
                datetime.fromisoformat(old_next_followup).strftime("%d-%b-%Y")
                if old_next_followup
                else "Not Set"
            )

            new_date = next_followup.strftime("%d-%b-%Y")

            activity_logs.append(
                f"📅 Next Follow-Up changed: {old_date} → {new_date}"
            )

        # Discussion Changed
        if old_discussion != new_discussion and new_discussion:
            activity_logs.append(
                f"📝 Discussion Updated:\n{new_discussion}"
            )

        # Create Timeline Entry Only If Something Changed
        if activity_logs:

            activity_note = "\n\n".join(activity_logs)

            create_followup(
                contact_id=contact_id,
                discussion=activity_note,
                status=new_status,
                next_followup_at=new_next_followup,
                created_by=admin_id
            )

        # Update latest lead snapshot
        

        
        admin_id = st.session_state.admin["admin_id"]

        existing_contact = check_contact_exists_for_admin(
            phone=phone,
            email=email,
            admin_id=admin_id
        )

        
        if existing_contact and existing_contact["contact_id"] != contact_id:
            st.warning("Another contact already uses this phone or email.")
            st.write("Conflicting contact:")
            st.dataframe(
                [existing_contact],
                use_container_width=True,
                hide_index=True
            )


        elif not name:
            st.warning("Name is required")

        elif not phone:
            st.warning("Phone is required")
            

        
        
        else:
        
            update_contact(
                contact_id=contact_id,
                name=name,
                phone=phone,
                email=email,
                short_discussion=discussion,
                status=status,
                next_followup_at=str(next_followup)
            )

            st.success("Follow-Up Saved")
            st.rerun()

# =====================================
# RIGHT SIDE
# =====================================

with right_col:

    st.subheader("📜 Activity Timeline")

    history = get_followup_history(contact_id)

    if not history:
        st.info("No activity found.")

    for item in history:

        with st.container(border=True):

            followup_dt = datetime.fromisoformat(
                item["followup_date"]
            )

            st.caption(
                f"📅 {followup_dt.strftime('%d-%b-%Y | %H:%M:%S')}"
            )

            st.write(
                f"🎯 Status: {item['status']}"
            )

            st.write(
                item["discussion"]
            )

            if item["next_followup_at"]:
                status = item.get("status", "")

                followup_messages = {
                    "New": "📅 First follow-up scheduled for",
                    "Contacted": "📞 Next conversation planned for",
                    "Interested": "👍 Follow-up with interested contact scheduled for",
                    "Follow Up": "🔄 Follow-up reminder set for",
                    "Booked": "🎉 Successfully completed on",
                    "Lost": "📁 Follow-up closed on"
                }

                
                next_followup_dt = datetime.fromisoformat(
                    item["next_followup_at"]
                )
                st.write(
                    f"{followup_messages.get(status, '📅 Next Action')}: "
                    f"{next_followup_dt.strftime('%d-%b-%Y | %H:%M:%S')}"
                )