import streamlit as st

from src.database.db import (
    get_admin_by_email,
    create_password_reset_otp,
    verify_reset_otp,
    update_admin_password
)

@st.dialog("Forgot Password")
def forgot_password_dialog():

    email = st.text_input("Email")

    if st.button("Send OTP"):

        admin = get_admin_by_email(email)

        if not admin:
            st.error("Email not found")
            return

        otp = create_password_reset_otp(email)

        st.session_state.reset_email = email

        st.success(
            f"OTP Generated: {otp}"
        )

    otp = st.text_input("OTP")

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    if st.button("Reset Password"):

        if verify_reset_otp(
            st.session_state.reset_email,
            otp
        ):

            update_admin_password(
                st.session_state.reset_email,
                new_password
            )

            st.success(
                "Password Updated Successfully"
            )

        else:
            st.error("Invalid OTP")