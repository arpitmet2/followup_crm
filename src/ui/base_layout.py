import streamlit as st


def show_app_header():

    st.markdown(
        """
        <h1 style='text-align:center;'>
            📞 FollowUp CRM
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h4 style='text-align:center;color:gray;'>
            Simple Lead & Follow-up Management
        </h4>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align:center; max-width:800px; margin:auto;'>
            Never miss a customer follow-up again.<br>
            Track leads, schedule follow-ups, manage conversations,
            and stay organized without the complexity of a traditional CRM.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("📋 Lead Tracking")
        st.caption("Capture and organize all leads.")

    with col2:
        st.info("📅 Follow-up Reminders")
        st.caption("Know who needs attention today.")

    with col3:
        st.warning("📈 Status Management")
        st.caption("Track progress from Lead to Deal.")

    st.markdown("")

    st.info(
        "✨ Designed for Real Estate, Insurance, Loans, Recruitment, Freelancers and Small Businesses."
    )