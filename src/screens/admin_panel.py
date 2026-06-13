import streamlit as st

from datetime import datetime


from src.database.db import (
    check_admin_user_name_exists,
    check_admin_email_exists,
    create_admin,
    check_admin_credentials,
    get_contacts,
    get_total_contacts,
    get_today_followups,
    get_overdue_contacts,
    delete_contact
)
from src.utils.cookies import cookies
from src.components.add_contact_dialog import add_contact_dialog
from src.components.edit_contact_dialog import edit_contact_dialog
from src.components.forgot_password_dialog import forgot_password_dialog


from src.components.dialog_share_subject import share_subject_dialog


today = datetime.now().date()


def admin_panel():

    st.header("👨‍💼 Admin Panel")

    col1, col2, col3 = st.columns([1,1,4])

    with col1:
        if st.button("🔐 Login"):
            st.session_state.admin_page = "login"

    with col2:
        if st.button("📝 Register"):
            st.session_state.admin_page = "register"

    with col3:
        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    st.divider()

    

    if st.session_state.get("admin_page") == "login":
        admin_login()

    elif st.session_state.get("admin_page") == "register":
        admin_registration()

    # active after some time
    '''elif st.session_state.get("admin_page") == "forgot_password":
        
        forgot_password_dialog()'''


def admin_dashboard():

    st.title("📊 Admin Dashboard")

    admin_name = st.session_state.admin["name"]

    st.success(f"Welcome {admin_name}")
    admin_id = st.session_state.admin["admin_id"]

    total_contacts = get_total_contacts(admin_id)

    today_followups = get_today_followups(admin_id)

    overdue_contacts = get_overdue_contacts(admin_id)

    contacts = get_contacts(
        st.session_state.admin["admin_id"]
    )
    overdue_contacts_list = []

    for contact in contacts:
        followup = contact.get("next_followup_at")

        if followup:
            followup_date = datetime.fromisoformat(
                followup.replace("Z", "+00:00")
            ).date()

            if followup_date < today:
                overdue_contacts_list.append(contact)

    overdue_contacts = overdue_contacts_list


    col1, col2, col3 = st.columns(3)

    col1.metric("📞 Today's Follow-Ups", today_followups)
    col2.metric("🔥 Overdue Leads", len(overdue_contacts))
    col3.metric("👥 My Total Leads", total_contacts)

    st.divider()

    st.subheader("Quick Actions")

    q1, q2, q3, q4, q5 = st.columns(5)

    with q1:
        if st.button(
            "📋 My Leads",
            use_container_width=True
        ):
            st.session_state.show_my_leads = True

    with q2:
        if st.button(
            "➕ Add Lead",
            use_container_width=True
        ):
            add_contact_dialog()

    with q3:
        if st.button(
            "📞 Today's Follow Ups",
            use_container_width=True
        ):
            st.session_state.show_today_followups = True

    with q4:
        if st.button(
            "🔥 Overdue Leads",
            use_container_width=True
        ):
            st.session_state.show_overdue_leads = True

    with q5:
        if st.button(
            "🎯 Lead QR",
            use_container_width=True
        ):
            share_subject_dialog("Lead QR", st.session_state.admin["admin_id"], st.session_state.admin["name"])
    st.divider()


    if st.session_state.get("show_my_leads"):

        st.session_state.show_today_followups = False
        st.session_state.show_overdue_leads = False

        
        st.session_state.show_my_leads = False

    st.subheader("📋 My Leads")



    if st.session_state.get("show_today_followups"):

        st.session_state.show_my_leads = False
        st.session_state.show_overdue_leads = False

        filtered_contacts = []

        for contact in contacts:

            followup = contact.get("next_followup_at")

            if followup:

                followup_date = datetime.fromisoformat(
                    str(followup)
                ).date()

                if followup_date == today:
                    filtered_contacts.append(contact)

        contacts = filtered_contacts
        st.session_state.show_today_followups = False

    if st.session_state.get("show_overdue_leads"):

        st.session_state.show_my_leads = False
        st.session_state.show_today_followups = False

        filtered_contacts = []

        for contact in contacts:
            followup = contact.get("next_followup_at")

            if followup:
                followup_date = datetime.fromisoformat(
                    followup.replace("Z", "+00:00")
                ).date()

                if followup_date < today:
                    filtered_contacts.append(contact)

        contacts = filtered_contacts
        st.session_state.show_overdue_leads = False
    
    search_col, filter_col = st.columns([3, 1])

    with search_col:
        search_text = st.text_input(
            "🔍 Search Lead",
            placeholder="Search..."
        )

    with filter_col:
        search_field = st.selectbox(
            "Filter",
            [
                "All",
                "Name",
                "Phone",
                "Email",
                "Status",
                #"Lead Source",
                #"Property Type"
            ]
        )


    if search_text:

        search_text = search_text.lower()

        field_map = {
            "Name": "name",
            "Phone": "phone",
            "Email": "email",
            "Status": "status",
            #"Lead Source": "lead_source",
            #"Property Type": "property_type"
        }

        filtered_contacts = []

        for contact in contacts:

            if search_field == "All":

                if any(
                    search_text in str(value).lower()
                    for value in contact.values()
                ):
                    filtered_contacts.append(contact)

            else:

                field_name = field_map.get(search_field)

                if search_text in str(
                    contact.get(field_name, "")
                ).lower():
                    filtered_contacts.append(contact)

        contacts = filtered_contacts

    if contacts:

        table_columns = [
            "",
            #"contact_id",
            "name",
            "phone",
            "email",
            #"lead_source",
            #"property_type",
            #"budget",
            "short_discussion",
            "status",
            "next_followup_at",
            #"last_followup_at",
            "created_at",
            #"updated_at",
            #"created_by",
            ""
        ]
        table_widths = [
            0.5,
            1.5,
            1.2,
            1.8,
            4.0,  # Discussion
            1.2,
            1.3,
            1.3,
            0.7
        ]

        header_cols = st.columns(table_widths)
        for column, header_col in zip(table_columns, header_cols):
            header_col.caption(column)

        selected_contacts = []

        for contact in contacts:
            contact_id = contact["contact_id"]
            row_cols = st.columns(table_widths)

            is_selected = row_cols[0].checkbox(
                "Select",
                label_visibility="collapsed",
                key=f"select_contact_{contact_id}"
            )

            if is_selected:
                selected_contacts.append(contact)

            for index, column in enumerate(table_columns[1:-1], start=1):
                value = contact.get(column)
                row_cols[index].write("" if value is None else value)

            if row_cols[-1].button(
                "✏️",
                key=f"edit_contact_{contact_id}",
                help="Edit this lead/contact"
            ):
                
                st.session_state.selected_contact_id = (
                    contact["contact_id"]
                )
                st.session_state.selected_contact_admin_id = (
                    contact["created_by"]
                )

                st.switch_page(
                    "pages/Follow_Up_Details.py"
               )



               # edit_contact_dialog(contact)

        confirm_delete = st.checkbox(
            "Confirm delete selected lead(s)",
            key="confirm_delete_selected_contacts"
        )

        if st.button(
            "🗑 Delete Selected Lead(s)",
            use_container_width=True
        ):
            if len(selected_contacts) == 0:
                st.warning("Please select at least one lead to delete.")
            elif not confirm_delete:
                st.warning("Please confirm before deleting selected lead(s).")
            else:
                for contact in selected_contacts:
                    delete_contact(
                        contact_id=contact["contact_id"],
                        admin_id=admin_id
                    )

                st.success("Selected contact(s) deleted successfully")
                st.rerun()
    else:
        st.info("📋 No records found.")   


    if st.button("🚪 Logout"):

        st.session_state.pop("admin", None)
        st.session_state.pop("admin_page", None)

        st.session_state.page = "home"


        cookies["admin_id"] = ""
        cookies.save()

        st.session_state.clear()
        st.rerun()


def admin_login():

    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    
    # below four line is also delatchnage/remove/add after add forgot possword option
    st.session_state.warning_type = st.session_state.get("warning_type", None) 
    if st.session_state.warning_type == "forgot_password":
        st.warning("🔐 Please save your username and password in a safe place.")
    #c1, c2, c3 = st.columns(3)
    
    c1, c2 = st.columns(2)
    

    with c1:

        if st.button("Login Now", use_container_width=True):

            if login_admin(username, password):

                st.success("Login Successful")

                st.session_state.page = "dashboard"

                st.rerun()

            else:

                st.error("Invalid Username or Password")

    with c2:

        if st.button("Register Instead", use_container_width=True):

            st.session_state.admin_page = "register"

            st.rerun()

    # all below code is active after some time when forgot password option is added
    '''with c3:

        if st.button("Forgot Password?", use_container_width=True):

            st.session_state.admin_page = "forgot_password"

            st.rerun()'''


def login_admin(username, password):

    admin = check_admin_credentials(username, password)

    if admin:

        st.session_state.admin = admin
        st.session_state.page = "dashboard"

        cookies["admin_id"] = str(admin["admin_id"])
        cookies.save()

        return True

    return False


def admin_registration():

    st.subheader("📝 Admin Registration")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button("Create Account"):

        success, message = register_admin(
            name,
            email,
            username,
            password,
            confirm_password
        )

        if success:

            st.success(message)

            st.session_state.warning_type = "forgot_password" # in future, this line is deleted, but for now, it is used to show the warning message on the login page after successful registration
            st.session_state.admin_page = "login"

            st.rerun()

        else:

            st.error(message)


def register_admin(
    name,
    email,
    username,
    password,
    confirm_password
):

    if not all(
        [
            name,
            email,
            username,
            password,
            confirm_password
        ]
    ):
        return False, "All fields are required"

    if check_admin_email_exists(email):
        return False, "Email already exists"

    if check_admin_user_name_exists(username):
        return False, "Username already exists"

    if password != confirm_password:
        return False, "Passwords do not match"

    try:

        create_admin(
            name=name,
            email=email,
            username=username,
            password=password
        )

        return True, "Account created successfully"

    except Exception as e:

        return False, str(e)

