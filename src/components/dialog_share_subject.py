import streamlit as st

import segno
import io


@st.dialog("Share  Link")
def share_subject_dialog(subject_name, admin_id, name):
    app_domain = "followupcrm"
    join_url = f"{app_domain}/?join-code={admin_id}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(name, language="text")

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption='QRCODE for class joining')

        