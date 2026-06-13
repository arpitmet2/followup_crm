import streamlit as st

from src.utils.cookies import cookies
from src.database.db import get_admin_by_id
from src.components.public_lead_form import public_lead_form


from src.screens.admin_panel import (
    admin_panel,
    admin_dashboard
)
from src.ui.base_layout import show_app_header


st.set_page_config(
    page_title="FollowUp CRM",
    page_icon="🎯",
    layout="wide"
)


st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)






agent_id = st.query_params.get("join-code")

if agent_id:
    public_lead_form(agent_id)
    st.stop()


def restore_session():

    if "admin" not in st.session_state:

        admin_id = cookies.get("admin_id")

        if admin_id:

            admin = get_admin_by_id(admin_id)

            if admin:

                st.session_state.admin = admin
                st.session_state.page = "dashboard"


def main():

    restore_session()

    if "page" not in st.session_state:

        if "admin" in st.session_state:
            st.session_state.page = "dashboard"
        else:
            st.session_state.page = "home"

    # HOME PAGE
    if st.session_state.page == "home":

        
        show_app_header()
        

        if st.button(
            "👨‍💼 Admin Portal",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.page = "admin"
            st.rerun()

    # LOGIN PAGE
    elif st.session_state.page == "admin":

        admin_panel()

    # DASHBOARD
    elif st.session_state.page == "dashboard":

        admin_dashboard()
   
    


if __name__ == "__main__":
    main()