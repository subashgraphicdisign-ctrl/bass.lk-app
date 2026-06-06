import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# --- Supabase Config ---
SUPABASE_URL = "https://vgqutvglgfqvxcywlkkd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZncXV0dmdsZ2ZxdnhjeXdsa2tkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MzE2OTQsImV4cCI6MjA5NjEwNzY5NH0.gQhVgbp8vtFYtKFRPQwc8_kyn-uLXxEvhCvBdfhztRc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BASS.lk", page_icon="icon.png")

st.markdown("""
    <link rel="manifest" href="https://raw.githubusercontent.com/subashgraphicdisign-ctrl/bass.lk-app/main/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="BASS.lk">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/subashgraphicdisign-ctrl/bass.lk-app/main/icon.png">
""", unsafe_allow_html=True)
def set_style(bg_img):
    st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("{bg_img}");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* බටන් වල පාට */
        div.stButton > button {{
            background-color: #fcc200 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }}
        /* අකුරු වල පාට */
        .stMarkdown, .stText, p, label, .stMetric {{
            color: #100c08 !important;
            font-weight: bold !important;
        }}
        /* Tab වල පාට */
        div[data-testid="stTabs"] {{
            background-color: rgba(0, 128, 0, 0.7);
            padding: 10px;
            border-radius: 10px;
        }}
        /* Container background */
        div[data-testid="stContainer"] {{
            background-color: rgba(0, 128, 0, 0.8) !important;
            border: 2px solid #fcc200 !important;
            border-radius: 20px !important;
            padding: 20px !important;
        }}
        h1 {{
            color: #FFD700 !important; 
            text-shadow: 4px 4px 8px #000000;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- APP STATE & CONSTANTS ---
ALL_CATS = ["🚰 Plumber", "⚡ Welder", "❄️ AC Technician", "📱 Mobile Technician", 
            "💻 Laptop Technician", "🪵 Wood Worker", "🛒 E-Commerce", "✏️ Other"]
ECOMM_ITEMS = ["Car", "Van", "Bike", "Lorry", "Bus", "Three-wheeler", "Land Vehicle", "Electronic", "Hardware", "Cloth", "Cosmetic"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "Login"
if "notepad" not in st.session_state: st.session_state.notepad = pd.DataFrame(columns=["Job", "Price"])
if "viewing_profile" not in st.session_state: st.session_state.viewing_profile = None

# --- LOGIN / REGISTER PAGE ---
if not st.session_state.logged_in:
    set_style("https://png.pngtree.com/png-clipart/20230913/original/pngtree-mechanical-engineering-vector-png-image_11079731.png")
    st.title("🔐 බාස්.LK APP")
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
                st.session_state.city = res.data[0].get('city', 'N/A')
                st.rerun()
            else: st.error("Invalid Phone or Password!")

    elif st.session_state.page == "Register":
        with st.form("reg_form"):
            r_name = st.text_input("Name"); r_phone = st.text_input("Phone"); r_city = st.text_input("City")
            r_nic = st.text_input("ID Number"); r_cat = st.selectbox("Category", ALL_CATS); r_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("REGISTER"):
                supabase.table("user_profiles").insert({
                    "username": r_name, "phone": r_phone, "city": r_city, "nic": r_nic, 
                    "category": r_cat, "password": r_pwd, "balance": 50
                }).execute()
                st.success("Account Created! You got 50 Balance.")

    elif st.session_state.page == "Forgot Password":
        f_phone = st.text_input("Enter Phone Number")
        if st.button("Get Password"):
            res = supabase.table("user_profiles").select("password").eq("phone", f_phone).execute()
            if res.data: st.info(f"Your Password: {res.data[0]['password']}")
            else: st.error("Phone number not found!")

else:
    # --- APP CONTENT ---
    bal_res = supabase.table("user_profiles").select("balance").eq("phone", st.session_state.phone).execute()
    current_bal = bal_res.data[0]['balance'] if bal_res.data else 0

    with st.sidebar:
        st.write(f"### 👤 {st.session_state.username}")
        st.info(f"📍 {st.session_state.city}")
        st.metric("Wallet Balance", f"Rs. {current_bal}")
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
        
        tab1, tab2, tab3 = st.tabs(["📝 Notepad", "➕ Post", "💰 Wallet"])
        with tab1:
            with st.form("n_form"):
                j = st.text_input("Job Name"); p = st.text_input("Price")
                if st.form_submit_button("Add"): 
                    st.session_state.notepad = pd.concat([st.session_state.notepad, pd.DataFrame([[j, p]], columns=["Job", "Price"])])
            st.table(st.session_state.notepad)
            
        with tab2:
            with st.form("p_form", clear_on_submit=True):
                desc = st.text_area("Description")
                app_link = st.text_input("Appliance Link")
                item = st.selectbox("Item Type", ECOMM_ITEMS) if st.session_state.category == "🛒 E-Commerce" else "N/A"
                file = st.file_uploader("Upload Image", type=['png', 'jpg'])
                if st.form_submit_button("Post"):
                    if current_bal >= 5:
                        img_url = None
                        if file:
                            fn = f"{uuid.uuid4()}.jpg"
                            supabase.storage.from_("posts").upload(fn, file.getvalue())
                            img_url = supabase.storage.from_("posts").get_public_url(fn)
                        supabase.table("user_posts").insert({
                            "name": st.session_state.username, "phone": st.session_state.phone, 
                            "category": st.session_state.category, "city": st.session_state.city, 
                            "item_type": item, "text_content": desc, "image_url": img_url, "link": app_link
                        }).execute()
                        supabase.table("user_profiles").update({"balance": current_bal - 5}).eq("phone", st.session_state.phone).execute()
                        st.success("Post success! Rs. 5 deducted.")
                        st.rerun()
                    else:
                        st.error("Balance මදි!")
                        st.markdown(f'[📲 Top-up සඳහා Admin අමතන්න (WhatsApp)](https://wa.me/94723960976)')

        with tab3:
            st.metric("Balance", f"Rs. {current_bal}")
            st.write("Top-up කිරීමට පහත අංකයට WhatsApp කරන්න:")
            st.markdown(f'[📞 WhatsApp: 0723960976](https://wa.me/94723960976)')

    # --- Home Feed & Profile logic ---
    if st.session_state.viewing_profile:
        set_style("https://as1.ftcdn.net/v2/jpg/01/64/54/22/1000_F_164542289_ShBLPzJcUkOQ9HFEn8sUTdZEw0sqHwea.jpg")
        phone = st.session_state.viewing_profile
        user_data = supabase.table("user_profiles").select("*").eq("phone", phone).execute().data
        if user_data:
            st.title(f"👤 {user_data[0]['username']}'s Profile")
            st.write(f"⭐ Rating: {user_data[0].get('rating', 0)}")
            st.write(f"📍 City: {user_data[0].get('city', 'N/A')} | 📞 Phone: {phone}")
            st.subheader("Posts")
            p_res = supabase.table("user_posts").select("*").eq("phone", phone).execute()
            for p in p_res.data: 
                st.info(p['text_content'])
            if st.button("⬅️ Back to Home"): 
                st.session_state.viewing_profile = None
                st.rerun()
    else:
        set_style("https://wallpapers.com/images/hd/white-texture-pictures-8m8jckljr6eb7icp.jpg")
        st.title("🏠 BUSSINESS GIGS")
        
        res = supabase.table("user_posts").select("*").execute()
        posts = res.data if res.data else []
        all_cities = sorted(list(set([p.get('city') for p in posts if p.get('city')])))
        
        search = st.selectbox("🔍 Search by Category / City / Item", ["All"] + ALL_CATS + ECOMM_ITEMS + all_cities)
        
        filtered = [p for p in reversed(posts) if search == "All" or p.get('category') == search or p.get('item_type') == search or p.get('city') == search]
        
        cols = st.columns(3)
        for i, p in enumerate(filtered):
            with cols[i % 3]:
                with st.container(border=True):
                    # Profile එකට යන බටන් එක
                    if st.button(f"👤 {p.get('name', 'User')}", key=f"user_btn_{i}"):
                        st.session_state.viewing_profile = p.get('phone')
                        st.rerun()
                        
                    st.caption(f"📍 {p.get('city', 'Unknown')} | 📦 {p.get('item_type', '')}")
                    st.write(p.get('text_content', ''))
                    if p.get('link'): 
                        st.markdown(f"[🔗 Link]({p['link']})")
                    if p.get('image_url'): 
                        st.image(p['image_url'], use_container_width=True)
                    
                    # Like සහ Call බටන් දෙක
                    col_l, col_c = st.columns(2)
                    with col_l:
                        if st.button(f"👍 Like", key=f"like_btn_{i}"):
                            u_data = supabase.table("user_profiles").select("rating").eq("phone", p['phone']).execute().data
                            if u_data:
                                new_rating = (u_data[0].get('rating', 0) or 0) + 1
                                supabase.table("user_profiles").update({"rating": new_rating}).eq("phone", p['phone']).execute()
                                st.rerun()
                    with col_c:
                        st.markdown(f'<a href="tel:{p.get("phone", "")}" style="display:block; text-align:center; background-color:#007bff; color:white; padding:10px; border-radius:10px; text-decoration:none;">📞 Call</a>', unsafe_allow_html=True)