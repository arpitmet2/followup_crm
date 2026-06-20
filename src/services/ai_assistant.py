from openai import OpenAI
from src.database.config import supabase
import streamlit as st

client = OpenAI(
    base_url=st.secrets["BASE_URL"],
    api_key=st.secrets["NVIDIA_API_KEY"]
)


def get_ai_lead_suggestion(contact_id, admin_id):

    response = (
        supabase.table("contacts")
        .select("*")
        .eq("contact_id", contact_id)
        .eq("created_by", admin_id)
        .execute()
    )

    if not response.data:
        return "Lead not found."

    lead = response.data[0]
    followup_response = (
    supabase.table("followups")
        .select(
            "discussion, status, followup_date, next_followup_at"
        )
        .eq("contact_id", contact_id)
        .order("followup_date")
        .execute()
    )


    discussion_history = ""

    for row in followup_response.data:
        discussion_history += f"""
    Date: {row.get('followup_date')}
    Status: {row.get('status')}
    Discussion: {row.get('discussion')}

    """

    prompt = f"""
    You are an expert CRM and sales assistant.

    Lead Information:
    Name: {lead.get('name')}
    Phone: {lead.get('phone')}
    Email: {lead.get('email')}
    Current Status: {lead.get('status')}
    Next Follow Up: {lead.get('next_followup_at')}

    Complete Follow-up History:
    {discussion_history}

    Instructions:

    1. Read the ENTIRE follow-up history.
    2. Create a short customer summary.
    3. Summarize all discussions in 3-5 bullet points.
    4. Suggest next action.
    5. Generate a professional WhatsApp follow-up message in Gujarati.
    6. Use simple Gujarati.
    7. Keep WhatsApp message under 60 words.
    8. Do not use emojis inside WhatsApp message.
    9. Estimate conversion probability from 0-100%.

    Return in exactly this format:

    📋 Lead Summary:
    ...

    📝 Discussion Summary:
    ...

    🎯 Interest Level:
    ...

    🚀 Next Action:
    ...

    📱 WhatsApp Message:
    ...

    📊 Conversion Probability:
    ...
    """

    completion = client.chat.completions.create(
        model="google/gemma-2-2b-it",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return completion.choices[0].message.content