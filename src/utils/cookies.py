from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st

cookies = EncryptedCookieManager(
    prefix="real_estate_crm/",
    password=st.secrets["COOKIE_PASSWORD"]
)

if not cookies.ready():
    st.stop()