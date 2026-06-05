import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# --- Supabase Config ---
SUPABASE_URL = "https://vgqutvglgfqvxcywlkkd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZncXV0dmdsZ2ZxdnhjeXdsa2tkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MzE2OTQsImV4cCI6MjA5NjEwNzY5NH0.gQhVgbp8vtFYtKFRPQwc8_kyn-uLXxEvhCvBdfhztRc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- UI DESIGN ---
st.set_page_config(page_title="BASS.lk Pro", layout="centered") # ෆෝන් එකට ගැළපෙන්න centered කළා
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    div.stButton > button { background-color: #007bff; color: white; border-radius: 10px; width: 100%; }
    h1, h2, h3 { color: #007bff; }
    .css-1544g2n { color: black !important; }
    </style>
""", unsafe_allow_html=True)

ALL_CATS = ["All Categories", "🚰 Plumber", "⚡ Welder", "❄️ AC Technician", "📱 Mobile Technician", 
            "💻 Laptop Technician", "🪵 Wood Worker", "🛒 E-Commerce", "✏️ Other"]
ECOMM_ITEMS = ["Car", "Van", "Bike", "Three-wheeler", "Tractor", "Electronic Items", "Hardware Items", "Other"]

if "registered" not in st.session_state: st.session_state.registered = False

# --- Registration ---
if not st.session_state.registered:
    st.title("🚀 JOIN BASS.LK")
    with st.form("reg"):
        st.session_state.username = st.text_input("Name")
        st.session_state.phone = st.text_input("Phone (Use this to Login)")
        st.session_state.category = st.selectbox("Category", ALL_CATS[1:])
        if st.form_submit_button("REGISTER"):
            # Profile එකක් නැත්නම් අලුතින් හදනවා
            check = supabase.table("user_profiles").select("*").eq("phone", st.session_state.phone).execute()
            if not check.data:
                supabase.table("user_profiles").insert({"username": st.session_state.username, "phone": st.session_state.phone, "balance": 0}).execute()
            st.session_state.registered = True
            st.rerun()
else:
    with st.sidebar:
        st.write(f"### 👤 {st.session_state.username}")
        tab1, tab2 = st.tabs(["➕ New Post", "💰 Wallet"])
        
        with tab1:
            with st.form("p_form", clear_on_submit=True):
                desc = st.text_area("Job Description")
                uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
                if st.form_submit_button("Post (Rs. 5)"):
                    res = supabase.table("user_profiles").select("balance").eq("phone", st.session_state.phone).execute()
                    if res.data and res.data[0]['balance'] >= 5:
                        img_url = None
                        if uploaded_file:
                            fn = f"{uuid.uuid4()}.jpg"
                            supabase.storage.from_("posts").upload(fn, uploaded_file.getvalue())
                            img_url = supabase.storage.from_("posts").get_public_url(fn)
                        supabase.table("user_posts").insert({"name": st.session_state.username, "phone": st.session_state.phone, "text_content": desc, "image_url": img_url}).execute()
                        supabase.table("user_profiles").update({"balance": res.data[0]['balance'] - 5}).eq("phone", st.session_state.phone).execute()
                        st.success("Post Success!")
                        st.rerun()
                    else: st.error("Balance low!")

        with tab2:
            res = supabase.table("user_profiles").select("balance").eq("phone", st.session_state.phone).execute()
            bal = res.data[0]['balance'] if res.data else 0
            st.metric("Balance", f"Rs. {bal}")
            amt = st.number_input("Top-up Amount", min_value=50, step=50)
            if st.button("Confirm Top-up"):
                supabase.table("user_profiles").update({"balance": bal + amt}).eq("phone", st.session_state.phone).execute()
                st.rerun()

    st.title("🏠 Home Feed")
    response = supabase.table("user_posts").select("*").execute()
    for p in reversed(response.data):
        with st.container(border=True):
            st.subheader(p.get('name', 'User'))
            st.write(p.get('text_content', ''))
            if p.get('image_url'): st.image(p['image_url'], use_container_width=True)
            st.markdown(f'<a href="tel:{p.get("phone", "")}" style="display:block; text-align:center; background-color:#007bff; color:white; padding:10px; border-radius:10px; text-decoration:none;">📞 Call {p.get("phone", "")}</a>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #888;'>Engineered by Peshala Subash</p>", unsafe_allow_html=True)