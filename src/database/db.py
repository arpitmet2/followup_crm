from src.database.config import supabase
import bcrypt
from datetime import datetime, date, timedelta
import random


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_admin_email_exists(email):
    response = (
        supabase.table("admins")
        .select("email")
        .eq("email", email)
        .execute()
    )

    return len(response.data) > 0


def check_admin_user_name_exists(username):
    response = (
        supabase.table("admins")
        .select("username")
        .eq("username", username)
        .execute()
    )

    return len(response.data) > 0

def create_admin(name, email, username, password):
    try:
        data = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "username": username.strip(),
            "password": hash_pass(password)
        }

        response = (
            supabase
            .table("admins")
            .insert(data)
            .execute()
        )

        return {
            "success": True,
            "data": response.data,
            "message": "Admin created successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": str(e)
        }
    
def check_admin_credentials(username, password):
    try:
        response = (
            supabase
            .table("admins")
            .select("*")
            .eq("username", username.strip())
            .execute()
        )

        if len(response.data) == 0:
            return False
        
        admin = response.data[0]
        if check_pass(password, admin['password']):
            return admin

    except Exception as e:
        print("Error checking admin credentials:", str(e))
        return False
    

def get_admin_by_id(admin_id):

    response = (
        supabase
        .table("admins")
        .select("*")
        .eq("admin_id", admin_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def check_contact_exists_for_admin(phone, email, admin_id, exclude_contact_id=None):
    phone = phone.strip()
    email = email.strip().lower() if email else ""

    phone_query = (
        supabase
        .table("contacts")
        .select("contact_id, name, phone, email")
        .eq("created_by", admin_id)
        .eq("phone", phone)
    )

    if exclude_contact_id:
        phone_query = phone_query.neq("contact_id", exclude_contact_id)

    phone_response = phone_query.execute()

    if phone_response.data:
        return phone_response.data[0]

    if email:
        email_query = (
            supabase
            .table("contacts")
            .select("contact_id, name, phone, email")
            .eq("created_by", admin_id)
            .eq("email", email)
        )

        if exclude_contact_id:
            email_query = email_query.neq("contact_id", exclude_contact_id)

        email_response = email_query.execute()

        if email_response.data:
            return email_response.data[0]

    return None


def create_contact(
    name,
    phone,
    email,
    discussion,
    next_followup_at,
    admin_id
):

    data = {
        "name": name,
        "phone": phone,
        "email": email,
        "short_discussion": discussion,
        "status": "New",
        "next_followup_at": next_followup_at,
        "created_by": admin_id
    }

    response = (
        supabase
        .table("contacts")
        .insert(data)
        .execute()
    )

    return response.data

def get_contact_by_id(contact_id, admin_id):

    response = (
        supabase
        .table("contacts")
        .select("*")
        .eq("contact_id", contact_id)
        .eq("created_by", admin_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None

from datetime import date

def update_contact(
    contact_id,
    name,
    phone,
    email,
    short_discussion,
    status,
    next_followup_at
):

    response = (
        supabase
        .table("contacts")
        .update({
            "name": name,
            "phone": phone,
            "email": email,
            "short_discussion": short_discussion,
            "status": status,
            "next_followup_at": next_followup_at,
            "last_followup_at": str(date.today())
        })
        .eq("contact_id", contact_id)
        .execute()
    )

    return response

def delete_contact(contact_id, admin_id):

    response = (
        supabase
        .table("contacts")
        .delete()
        .eq("contact_id", contact_id)
        .eq("created_by", admin_id)
        .execute()
    )

    return response.data

def get_contacts(admin_id):

    response = (
        supabase
        .table("contacts")
        .select("*")
        .eq("created_by", admin_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

def get_total_contacts(admin_id):

    response = (
        supabase
        .table("contacts")
        .select("contact_id")
        .eq("created_by", admin_id)
        .execute()
    )

    return len(response.data)

def get_today_followups(admin_id):

    today = date.today()

    response = (
        supabase
        .table("contacts")
        .select("contact_id")
        .eq("created_by", admin_id)
        .gte(
            "next_followup_at",
            f"{today} 00:00:00"
        )
        .lte(
            "next_followup_at",
            f"{today} 23:59:59"
        )
        .execute()
    )

    return len(response.data)






def get_overdue_contacts(admin_id):

    now = datetime.now().isoformat()

    response = (
        supabase
        .table("contacts")
        .select("contact_id")
        .eq("created_by", admin_id)
        .lt("next_followup_at", now)
        .neq("status", "Booked")
        .neq("status", "Lost")
        .execute()
    )

    return len(response.data)




def get_followup_history(contact_id):

    response = (
        supabase
        .table("followups")
        .select("*")
        .eq("contact_id", contact_id)
        .order("followup_date", desc=True)
        .execute()
    )

    return response.data


def create_followup(
    contact_id,
    discussion,
    status,
    next_followup_at,
    created_by
):

    response = (
        supabase
        .table("followups")
        .insert({
            "contact_id": contact_id,
            "discussion": discussion,
            "status": status,
            "next_followup_at": next_followup_at,
            "created_by": created_by
        })
        .execute()
    )

    return response


def get_admin_by_email(email):
    response = (
        supabase
        .table("admins")
        .select("*")
        .eq("email", email.lower())
        .execute()
    )

    if response.data:
        return response.data[0]

    return None




def create_password_reset_otp(email):

    otp = str(random.randint(100000, 999999))

    supabase.table(
        "password_reset_tokens"
    ).insert({
        "email": email,
        "otp": otp,
        "expires_at": (
            datetime.now() + timedelta(minutes=10)
        ).isoformat()
    }).execute()

    return otp

def verify_reset_otp(email, otp):

    response = (
        supabase
        .table("password_reset_tokens")
        .select("*")
        .eq("email", email)
        .eq("otp", otp)
        .eq("is_used", False)
        .execute()
    )

    return len(response.data) > 0


def update_admin_password(email, password):

    response = (
        supabase
        .table("admins")
        .update({
            "password": hash_pass(password)
        })
        .eq("email", email)
        .execute()
    )

    return response
