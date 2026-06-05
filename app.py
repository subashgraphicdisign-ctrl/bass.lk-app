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
st.markdown("""<style>.stApp { background-color: #f8f9fa; } .stMarkdown, .stText, label, p { color: #000000 !important; }</style>""", unsafe_allow_html=True)

ALL_CATS = ["🚰 Plumber", "⚡ Welder", "❄️ AC Technician", "📱 Mobile Technician", 
            "💻 Laptop Technician", "🪵 Wood Worker", "🛒 E-Commerce", "✏️ Other"]
ECOMM_ITEMS = ["Car", "Van", "Bike", "Lorry", "Bus", "Three-wheeler", "Land Vehicle", "Electronic", "Hardware", "Cloth", "Cosmetic"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "Login"
if "notepad" not in st.session_state: st.session_state.notepad = pd.DataFrame(columns=["Job", "Price"])

# --- LOGIN / REGISTER PAGE ---
if not st.session_state.logged_in:
    st.title("🔐 BASS.LK APP")
    col1, col2, col3 = st.columns(3)
    if col1.button("Login"): st.session_state.page = "Login"
    if col2.button("Register"): st.session_state.page = "Register"
    if col3.button("Forgot Password"): st.session_state.page = "Forgot Password"

    if st.session_state.page == "Login":
        l_phone = st.text_input("Phone Number")
        l_pwd = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            res = supabase.table("user_profiles").select("*").eq("phone", l_phone).eq("password", l_pwd).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.username = res.data[0]['username']
                st.session_state.phone = l_phone
                st.session_state.category = res.data[0]['category']
                st.session_state.city = res.data[0].get('city', 'N/A') # City load කිරීම
                st.rerun()
            else: st.error("Invalid Phone or Password!")

    elif st.session_state.page == "Register":
        with st.form("reg_form"):
            r_name = st.text_input("Name")
            r_phone = st.text_input("Phone")
            r_city = st.text_input("City") # අලුතින් එකතු කළ City
            r_nic = st.text_input("ID Number")
            r_cat = st.selectbox("Category", ALL_CATS)
            r_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("REGISTER"):
                supabase.table("user_profiles").insert({
                    "username": r_name, "phone": r_phone, "city": r_city, "nic": r_nic, 
                    "category": r_cat, "password": r_pwd
                }).execute()
                st.success("Account Created! Now click Login.")
    # (Forgot password logic same) ...
    elif st.session_state.page == "Forgot Password":
        f_phone = st.text_input("Enter Phone Number")
        if st.button("Get Password"):
            res = supabase.table("user_profiles").select("password").eq("phone", f_phone).execute()
            if res.data: st.info(f"Your Password: {res.data[0]['password']}")
            else: st.error("Phone number not found!")

else:
    # --- APP CONTENT ---
    with st.sidebar:
        st.write(f"### 👤 {st.session_state.username}")
        st.info(f"📍 {st.session_state.city}")
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()
        
        tab1, tab2, tab3 = st.tabs(["📝 Notepad", "➕ Post", "💰 Wallet"])
        with tab1:
            with st.form("n_form"):
                j = st.text_input("Job Name"); p = st.text_input("Price")
                if st.form_submit_button("Add"): st.session_state.notepad = pd.concat([st.session_state.notepad, pd.DataFrame([[j, p]], columns=["Job", "Price"])])
            st.table(st.session_state.notepad)
            
        with tab2:
            with st.form("p_form", clear_on_submit=True):
                desc = st.text_area("Description")
                app_link = st.text_input("Appliance Link")
                item = st.selectbox("Item Type", ECOMM_ITEMS) if st.session_state.category == "🛒 E-Commerce" else "N/A"
                file = st.file_uploader("Upload Image", type=['png', 'jpg'])
                if st.form_submit_button("Post"):
                    img_url = None
                    if file:
                        fn = f"{uuid.uuid4()}.jpg"
                        supabase.storage.from_("posts").upload(fn, file.getvalue())
                        img_url = supabase.storage.from_("posts").get_public_url(fn)
                    # මෙතනට City එක insert කිරීම
                    supabase.table("user_posts").insert({
                        "name": st.session_state.username, 
                        "phone": st.session_state.phone, 
                        "category": st.session_state.category,
                        "city": st.session_state.city, 
                        "item_type": item, 
                        "text_content": desc, 
                        "image_url": img_url, 
                        "link": app_link
                    }).execute()
                    st.rerun()

        with tab3:
            st.metric("Balance", "Rs. 0")
            amt = st.number_input("Top-up Amount", min_value=50, step=50)
            if st.button("Confirm Top-up"): st.success("Admin අමතන්න!")

   # --- Home Feed & Search Logic ---
    st.title("🏠 Home Feed")
    
    # 1. Database එකෙන් ඔක්කොම පෝස්ට් ටික ගමු
    res = supabase.table("user_posts").select("*").execute()
    posts = res.data if res.data else []
    
    # 2. Database එකේ තියෙන සියලුම Unique City නම් ටික හොයාගමු
    all_cities = sorted(list(set([p.get('city') for p in posts if p.get('city')])))
    
    # 3. Search options වලට City ලැයිස්තුවත් එකතු කරමු
    search_options = ["All"] + ALL_CATS + ECOMM_ITEMS + all_cities
    
    # 4. Search bar එක
    search = st.selectbox("🔍 Search by Category / City / Item", search_options)
    
    # 5. Search Logic එක
    cols = st.columns(3)
    for i, p in enumerate(reversed(posts)):
        # මෙතනදී පෝස්ට් එකේ Category, Item_type හෝ City එක search එකට match වෙයිද බලනවා
        if search == "All" or p.get('category') == search or p.get('item_type') == search or p.get('city') == search:
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(p.get('name'))
                    st.caption(f"📍 {p.get('city', 'Unknown')} | 📦 {p.get('item_type', '')}")
                    st.write(p.get('text_content', ''))
                    if p.get('image_url'): st.image(p['image_url'], use_container_width=True)
                    st.markdown(f'<a href="tel:{p.get("phone", "")}" style="display:block; text-align:center; background-color:#007bff; color:white; padding:10px; border-radius:10px; text-decoration:none;">📞 Call {p.get("phone", "")}</a>', unsafe_allow_html=True)