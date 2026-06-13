import streamlit as st
import supabase


def public_lead_form(agent_id):

    st.title("Inquiry")

    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    requirement = st.text_area("Requirement")

    if st.button("Submit Inquiry"):

        
        existing = (
            supabase.table("contacts")
            .select("contact_id")
            .eq("phone", phone)
            .eq("created_by", int(agent_id))
            .execute()
        )

        if existing.data:
            st.warning("We already have your inquiry on record.")
            st.stop()
        
        
        
        supabase.table("contacts").insert({
            "name": name,
            "phone": phone,
            "email": email,
            "short_discussion": requirement,
            "created_by": int(agent_id),
            "lead_source": "QR Code",
            "status": "New"
        }).execute()

        st.success("Thank you! We will contact you soon.")