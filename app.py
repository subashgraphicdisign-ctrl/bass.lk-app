import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# --- Supabase Config ---
SUPABASE_URL = "https://vgqutvglgfqvxcywlkkd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZncXV0dmdsZ2ZxdnhjeXdsa2tkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MzE2OTQsImV4cCI6MjA5NjEwNzY5NH0.gQhVgbp8vtFYtKFRPQwc8_kyn-uLXxEvhCvBdfhztRc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- UI DESIGN ---
st.set_page_config(page_title="BASS.lk Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div.stButton > button { background-color: #007bff; color: white; border-radius: 10px; }
    h1, h2, h3 { color: #007bff; }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

ALL_CATS = ["All Categories", "🚰 Plumber", "⚡ Welder", "❄️ AC Technician", "📱 Mobile Technician", 
            "💻 Laptop Technician", "🪵 Wood Worker", "🛒 E-Commerce", "✏️ Other"]
ECOMM_ITEMS = ["Car", "Van", "Bike", "Three-wheeler", "Tractor", "Electronic Items", "Hardware Items", "Other"]

if "registered" not in st.session_state: st.session_state.registered = False
if "notepad" not in st.session_state: st.session_state.notepad = pd.DataFrame(columns=["Job", "Price"])

# --- Registration ---
if not st.session_state.registered:
    st.title("🚀 JOIN BASS.LK NETWORK")
    with st.form("reg"):
        st.session_state.username = st.text_input("Name")
        st.session_state.phone = st.text_input("Phone")
        st.session_state.nic = st.text_input("ID Number")
        st.session_state.category = st.selectbox("Category", ALL_CATS[1:])
        if st.form_submit_button("REGISTER"):
            st.session_state.registered = True
            st.rerun()
else:
    with st.sidebar:
        st.write(f"### 👤 {st.session_state.username}")
        st.info(f"💼 {st.session_state.category}")
        
        tab1, tab2, tab3 = st.tabs(["📝 Notepad", "➕ New Post", "💰 Wallet"])
        
        with tab1:
            with st.form("n_form"):
                j = st.text_input("Job Name"); p = st.text_input("Price")
                if st.form_submit_button("Add"):
                    st.session_state.notepad = pd.concat([st.session_state.notepad, pd.DataFrame([[j, p]], columns=["Job", "Price"])])
            st.table(st.session_state.notepad)
            
        with tab2:
            with st.form("p_form", clear_on_submit=True):
                desc = st.text_area("Description")
                item = st.selectbox("Item Type", ECOMM_ITEMS) if st.session_state.category == "E-Commerce" else "N/A"
                uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("Post (Rs. 5)"):
                    res = supabase.table("user_profiles").select("balance").eq("phone", st.session_state.phone).execute()
                    if res.data:
                        bal = res.data[0]['balance']
                        if bal >= 5:
                            img_url = None
                            if uploaded_file:
                                fn = f"{uuid.uuid4()}.jpg"
                                supabase.storage.from_("posts").upload(fn, uploaded_file.getvalue())
                                img_url = supabase.storage.from_("posts").get_public_url(fn)
                            
                            supabase.table("user_posts").insert({
                                "name": st.session_state.username, "phone": st.session_state.phone,
                                "category": st.session_state.category, "text_content": desc,
                                "item_type": item, "image_url": img_url
                            }).execute()
                            supabase.table("user_profiles").update({"balance": bal - 5}).eq("phone", st.session_state.phone).execute()
                            st.success("පෝස්ට් කළා! Rs. 5ක් කැපුණා.")
                            st.rerun()
                        else:
                            st.error("ශේෂය මදි!")

        with tab3:
            res = supabase.table("user_profiles").select("balance").eq("phone", st.session_state.phone).execute()
            bal = res.data[0]['balance'] if res.data else 0
            st.metric("Balance", f"Rs. {bal}")
            amt = st.number_input("Top-up Amount", min_value=50, step=50)
            if st.button("Confirm Top-up"):
                supabase.table("user_profiles").update({"balance": bal + amt}).eq("phone", st.session_state.phone).execute()
                st.success(f"Rs. {amt} එකතු කළා!")
                st.rerun()

    st.title("🏠 Home Feed")
    cat_filter = st.selectbox("🔍 Search Categories", ALL_CATS)
    response = supabase.table("user_posts").select("*").execute()
    cols = st.columns(3)
    for i, p in enumerate(reversed(response.data)):
        if cat_filter == "All Categories" or p.get('category') == cat_filter:
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(p.get('name', 'User'))
                    if p.get('item_type') != "N/A": st.caption(f"📦 {p['item_type']}")
                    st.write(p.get('text_content', ''))
                    if p.get('image_url'): st.image(p['image_url'], use_container_width=True)
                    st.markdown(
                        f"""<a href="tel:{p.get('phone', '')}" style="display:block; text-align:center; background-color:#007bff; color:white; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold;">📞 Call {p.get('phone', '')}</a>""", 
                        unsafe_allow_html=True
                    )

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Engineered by Peshala Subash</p>", unsafe_allow_html=True)