import streamlit as st
import requests
import psycopg2 
from streamlit_javascript import st_javascript
import hashlib
import extra_streamlit_components as stx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# আপনার ইমেইল সেটিংস (অ্যাডমিন ইমেইল)
ADMIN_EMAIL = "fatin.shikkha@gmail.com" 
APP_PASSWORD = "keue dkyl zgtp krhc" # এটি আপনার জিমেইলের App Password

def send_admin_email(user_name, user_phone, amount, trx_id):
    try:
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"🔔 নতুন পেমেন্ট রিকোয়েস্ট: {trx_id}"
        
        body = f"""
        নতুন একটি পেমেন্ট রিকোয়েস্ট এসেছে!
        
        নাম: {user_name}
        ফোন: {user_phone}
        টাকার পরিমাণ: ৳{amount}
        TrxID: {trx_id}
        
        দয়া করে অ্যাডমিন প্যানেলে গিয়ে চেক করুন।
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_EMAIL, APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(ADMIN_EMAIL, ADMIN_EMAIL, text)
        server.quit()
    except Exception as e:
        pass # ইমেইল না গেলেও যেন ওয়েবসাইট ক্র্যাশ না করে

import random

def send_otp_email(user_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = user_email
        msg['Subject'] = "🔒 ইমেইল ভেরিফিকেশন কোড (OTP) - নজির.এআই"
        
        body = f"""
        আপনার নজির.এআই অ্যাকাউন্টের ভেরিফিকেশন কোডটি হলো: {otp_code}
        
        দয়া করে কোডটি ওয়েবসাইটে বসিয়ে আপনার রেজিস্ট্রেশন সম্পন্ন করুন।
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_EMAIL, APP_PASSWORD)
        server.sendmail(ADMIN_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# ==========================================
# ⚙️ ইউজার কন্ট্রোল প্যানেল 
# ==========================================
SITE_TITLE = "নজির.এআই (Nojir.ai)"
SITE_SUBTITLE = "আপনার স্মার্ট লিগ্যাল রিসার্চ অ্যাসিস্ট্যান্ট - Powered by নজির-১"
PAGE_ICON = "logo.jpg" 
CHAT_PLACEHOLDER = "আপনার আইনি প্রশ্ন বা নজির খুঁজুন... (যেমন: চেক ডিজঅনার মামলার নজির)"
LOGO_FILE = "logo.jpg" 

# n8n Webhook Link
WEBHOOK_URL = "https://rahul123321.app.n8n.cloud/webhook/nojir"

st.set_page_config(page_title=SITE_TITLE, page_icon=PAGE_ICON, layout="centered")
st.set_page_config(page_title=SITE_TITLE, page_icon=PAGE_ICON, layout="centered")

# ==========================================
# 🎨 ওয়ার্ল্ড-ক্লাস UI/UX (Premium Black & Gold Theme)
# ==========================================
st.markdown("""
<style>
    /* মেইন ব্যাকগ্রাউন্ড */
    .stApp {
        background-color: #121212 !important;
    }

    /* 🟢 ফিক্স: উপরের সাদা হেডার ট্রান্সপারেন্ট করা এবং ডানদিকের Fork/Menu বাটন গায়েব করা */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    [data-testid="stToolbar"] {
        display: none !important; /* এটি উপরের ডানদিকের সবকিছু লুকিয়ে ফেলবে */
    }

    /* 🟢 ফিক্স: নিচের চ্যাটবক্সের পেছনের একগুঁয়ে সাদা ব্যাকগ্রাউন্ড কালো করা */
    [data-testid="stBottom"], [data-testid="stBottom"] > div, .stAppBottomBlock {
        background-color: #121212 !important;
    }

    /* সব সাধারণ লেখার কালার ঠিক করা */
    .stApp, p, h1, h2, h3, h4, h5, h6, span, label, div {
        color: #E0E0E0 !important;
    }

    /* বাটনের প্রিমিয়াম গোল্ড ডিজাইন */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #121212 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px -1px rgba(212, 175, 55, 0.2) !important;
    }
    .stButton>button:hover {
        background-color: #F3E5AB !important;
        color: #121212 !important;
    }

    /* ইনপুট ফিল্ড এবং চ্যাটবক্সের লেখার অদৃশ্য সমস্যা সমাধান */
    .stTextInput input, .stTextArea textarea, .stChatInputContainer textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: 1px solid #333333 !important;
    }
    
    /* ফোকাস করলে গোল্ডেন বর্ডার */
    .stTextInput input:focus, .stChatInputContainer:focus-within, .stTextArea textarea:focus {
        border: 1px solid #D4AF37 !important;
        box-shadow: 0 0 5px rgba(212, 175, 55, 0.3) !important;
    }

    /* গায়েব হয়ে যাওয়া চ্যাট মেসেজগুলোর ব্যাকগ্রাউন্ড ও টেক্সট ঠিক করা */
    [data-testid="stChatMessage"] {
        background-color: #1E1E1E !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin-top: 10px !important;
    }
    [data-testid="stChatMessage"] * {
        color: #FFFFFF !important;
    }

    /* সাইডবার */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        border-right: 1px solid #333333 !important;
    }

    /* ড্রপডাউন মেনু (Selectbox) ফিক্স */
    div[data-baseweb="select"] > div {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border-color: #333333 !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }

    /* এক্সপ্যান্ডার (Recharge Form) */
    .streamlit-expanderHeader {
        background-color: #242424 !important;
        color: #D4AF37 !important;
        border-radius: 8px !important;
        border: 1px solid #333333 !important;
    }
    
    /* সাকসেস এবং এরর মেসেজের ডিজাইন */
    .stAlert {
        background-color: #1E1E1E !important;
        border-radius: 8px !important;
        border-left: 4px solid #D4AF37 !important;
        color: #E0E0E0 !important;
    }
</style>
""", unsafe_allow_html=True)
# ==========================================
# 🗄️ ডাটাবেস কানেকশন লজিক
# ==========================================
DB_URL = "postgresql://fatin1_user:SrXReBhReO5hMV42DZBVtOnXKblHvGCH@dpg-d827iiv7f7vs73dshujg-a.ohio-postgres.render.com/fatin1"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@st.cache_resource(show_spinner=False)
def setup_settings_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key_name TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        # ডিফল্ট রেট এবং নাম্বার সেট করা (যদি আগে থেকে ডাটাবেসে না থাকে)
        cur.execute("INSERT INTO settings (key_name, value) VALUES ('rate_per_100_tk', '10') ON CONFLICT DO NOTHING")
        cur.execute("INSERT INTO settings (key_name, value) VALUES ('bkash_number', '01684545015') ON CONFLICT DO NOTHING")
        conn.commit()
        cur.close()
        conn.close()
    except:
        pass

setup_settings_table() # অ্যাপ চালু হলেই একবার টেবিলটি চেক করে নিবে

@st.cache_data(ttl=60, show_spinner=False) # প্রতি ৬০ সেকেন্ড পর পর ডাটাবেস থেকে আপডেট নিবে
def get_setting(key_name, default_value):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key_name=%s", (key_name,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res:
            return res[0]
    except:
        pass
    return default_value

# ==========================================
# 🔒 সিকিউরিটি, সাইনআপ এবং লগইন সিস্টেম
# ==========================================
import datetime

cookie_manager = stx.CookieManager(key="nojir_cookie_manager")

# UX Fix: ব্রাউজার থেকে কুকি রিড করার জন্য ওয়েবসাইটকে অন্তত একবার রিরান হতে হয়।
# প্রথমবার লোড হওয়ার সময় আমরা লগইন পেজ হাইড করে রাখব, যাতে ফ্লিকারিং (Flickering) না হয়।
if "first_run_done" not in st.session_state:
    st.session_state.first_run_done = True
    st.write("")
    st.write("")
    with st.spinner("অ্যাকাউন্ট চেক করা হচ্ছে, দয়া করে অপেক্ষা করুন..."):
        st.stop() # এখানে স্টপ করলে কুকি ম্যানেজার নিজে থেকেই কুকি নিয়ে পেজটি আরেকবার রিরান করবে।

# লগইনের পর কুকি সেট করার কমান্ড (st.rerun এর কারণে কুকি সেভ না হওয়ার বাগ ফিক্স)
if "set_cookie_id" in st.session_state:
    expire_date = datetime.datetime.now() + datetime.timedelta(days=30) # ৩০ দিনের মেয়াদ
    cookie_manager.set("nojir_user_id", st.session_state.set_cookie_id, expires_at=expire_date, key="set_login_cookie")
    del st.session_state.set_cookie_id

# ব্রাউজারের কুকি থেকে ইউজার আইডি চেক করা
cached_user_id = cookie_manager.get(cookie="nojir_user_id")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""

# রিফ্রেশ দিলে যদি সেশন মুছে যায়, কিন্তু কুকি থাকে, তবে অটো লগইন হবে
if not st.session_state.logged_in and cached_user_id:
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, credits FROM users WHERE id=%s", (int(cached_user_id),))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.user_name = user[1]
            st.session_state.credits = user[2]
            st.rerun() # কুকি থেকে ডাটা পেলে সাথে সাথে রিফ্রেশ করে মেইন ওয়েবসাইটে নিয়ে যাবে
    except Exception as e:
        pass

if not st.session_state.logged_in:
    st.write("") 
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image(LOGO_FILE, width=100)
        except:
            pass
        if "signup_step" not in st.session_state:
            st.session_state.signup_step = 1
            
        # লগইন এবং সাইনআপের জন্য দুটি আলাদা ট্যাব
        tab1, tab2 = st.tabs(["লগইন করুন", "নতুন অ্যাকাউন্ট খুলুন"])
        
       # --- লগইন ট্যাব ---
        with tab1:
            st.subheader("অ্যাডভোকেট লগইন")
            login_email = st.text_input("ইমেইল (Email):", placeholder="আপনার ইমেইল দিন...")
            login_phone = st.text_input("ফোন নাম্বার (Phone):", type="password", placeholder="পাসওয়ার্ড হিসেবে ফোন নাম্বার দিন...")
            
            if st.button("প্রবেশ করুন"):
                with st.spinner("লগইন চেক করা হচ্ছে, দয়া করে অপেক্ষা করুন..."):
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("SELECT id, name, credits FROM users WHERE email=%s AND phone=%s", (login_email, login_phone))
                        user = cur.fetchone()
                        cur.close()
                        conn.close()
                        
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user[0]
                            st.session_state.user_name = user[1]
                            st.session_state.credits = user[2]
                            
                            # সরাসরি সেট না করে সেশনে আইডি রেখে দেওয়া হলো, যাতে রিরান হওয়ার পর কুকিটি ব্রাউজারে সেভ হয়
                            st.session_state.set_cookie_id = str(user[0])
                            
                            st.rerun()
                        else:
                            st.error("❌ ইমেইল বা ফোন নাম্বার ভুল হয়েছে!")
                    except Exception as e:
                        st.error("ডাটাবেস কানেকশনে সমস্যা হচ্ছে!")
# --- সাইনআপ ট্যাব ---
        with tab2:
            st.subheader("নতুন অ্যাকাউন্ট রেজিস্ট্রেশন")
            
            if st.session_state.signup_step == 1:
                reg_name = st.text_input("আপনার নাম:")
                reg_email = st.text_input("ইমেইল অ্যাড্রেস:")
                reg_phone = st.text_input("ফোন নাম্বার (এটি আপনার পাসওয়ার্ড হিসেবে কাজ করবে):")
                reg_address = st.text_input("চেম্বার/ঠিকানা:")
                
                # জাভাস্ক্রিপ্ট দিয়ে ব্রাউজারের ইউনিক তথ্য আনা হচ্ছে
                browser_info = st_javascript("navigator.userAgent + screen.width + 'x' + screen.height + navigator.language")
                
                if browser_info:
                    fingerprint_id = hashlib.md5(str(browser_info).encode()).hexdigest()
                else:
                    fingerprint_id = f"{reg_email}_{reg_phone}" 
                
                if st.button("OTP পাঠান (Send OTP)"):
                    if reg_name and reg_email and reg_phone:
                        with st.spinner("ইমেইল চেক করা হচ্ছে এবং OTP পাঠানো হচ্ছে..."):
                            try:
                                conn = get_db_connection()
                                cur = conn.cursor()
                                cur.execute("SELECT * FROM users WHERE email=%s OR phone=%s OR fingerprint=%s", (reg_email, reg_phone, fingerprint_id))
                                existing_user = cur.fetchone()
                                cur.close()
                                conn.close()
                                
                                if existing_user:
                                    st.error("⚠️ দুঃখিত! এই ইমেইল, ফোন নাম্বার অথবা ডিভাইস দিয়ে ইতিমধ্যে অ্যাকাউন্ট খোলা হয়েছে।")
                                else:
                                    # ৬-ডিজিটের OTP বানানো এবং মেইল করা
                                    otp = str(random.randint(100000, 999999))
                                    if send_otp_email(reg_email, otp):
                                        st.session_state.generated_otp = otp
                                        st.session_state.reg_details = {
                                            "name": reg_name, "email": reg_email, 
                                            "phone": reg_phone, "address": reg_address, 
                                            "fingerprint": fingerprint_id
                                        }
                                        st.session_state.signup_step = 2
                                        st.rerun()
                                    else:
                                        st.error("❌ ইমেইল পাঠাতে সমস্যা হয়েছে। আপনার ইমেইল অ্যাড্রেসটি কি সঠিক?")
                            except Exception as e:
                                st.error(f"ডাটাবেস এরর: {e}")
                    else:
                        st.warning("দয়া করে নাম, ইমেইল এবং ফোন নাম্বার অবশ্যই পূরণ করুন।")
            
            elif st.session_state.signup_step == 2:
                user_email_sent = st.session_state.reg_details['email']
                st.info(f"📧 **{user_email_sent}** ঠিকানায় একটি ভেরিফিকেশন কোড পাঠানো হয়েছে।")
                
                user_otp_input = st.text_input("৬-ডিজিটের OTP কোডটি লিখুন:")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ ভেরিফাই এবং সাইনআপ"):
                        if user_otp_input == st.session_state.generated_otp:
                            with st.spinner("অ্যাকাউন্ট তৈরি হচ্ছে..."):
                                try:
                                    conn = get_db_connection()
                                    cur = conn.cursor()
                                    d = st.session_state.reg_details
                                    cur.execute("""
                                        INSERT INTO users (name, email, phone, address, fingerprint, credits) 
                                        VALUES (%s, %s, %s, %s, %s, 10)
                                    """, (d["name"], d["email"], d["phone"], d["address"], d["fingerprint"]))
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    
                                    st.success("✅ অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে! দয়া করে 'লগইন করুন' ট্যাব থেকে লগইন করুন।")
                                    # কাজ শেষ, তাই আবার স্টেপ ১ এ পাঠিয়ে দেওয়া হলো
                                    st.session_state.signup_step = 1
                                    st.session_state.generated_otp = None
                                    st.session_state.reg_details = {}
                                except Exception as e:
                                    st.error("অ্যাকাউন্ট সেভ করতে সমস্যা হয়েছে!")
                        else:
                            st.error("❌ OTP ভুল হয়েছে! দয়া করে মেইল চেক করে সঠিক কোডটি দিন।")
                
                with col_btn2:
                    if st.button("🔙 পিছনে যান"):
                        st.session_state.signup_step = 1
                        st.rerun()

    st.stop() # <-- এই লাইনটিই ইন্টারফেসকে আলাদা করে রাখবে
# ==========================================
# 🪙 ক্রেডিট সিস্টেম এবং চ্যাট হিস্ট্রি
# ==========================================
if "credits" not in st.session_state:
    st.session_state.credits = 1  

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 🖥️ ওয়েবসাইটের ডিজাইন (লগইনের পর)
# ==========================================
col1, col2 = st.columns([1, 5]) 
with col1:
    try:
        st.image(LOGO_FILE, width=80) 
    except:
        st.write("লোগো পাওয়া যায়নি")
with col2:
    st.header(SITE_TITLE)
    st.caption(SITE_SUBTITLE)

st.sidebar.markdown("### 🔍 স্মার্ট ফিল্টার")
st.sidebar.caption("আপনার সার্চ আরও নির্দিষ্ট করুন")

division = st.sidebar.selectbox("আদালতের বিভাগ (Division)", ["সিলেক্ট করুন (সব)", "Appellate Division (AD)", "High Court Division (HCD)"])

col1, col2 = st.sidebar.columns(2)
with col1:
    case_year = st.text_input("সাল (Year)", placeholder="যেমন: 2024")
with col2:
    case_type = st.text_input("ধরন (Type)", placeholder="যেমন: Civil")

# ==========================================
# 💳 সাইডবার: ক্রেডিট এবং পেমেন্ট সিস্টেম
# ==========================================
st.sidebar.divider()
st.sidebar.markdown(f"**আপনার বর্তমান ক্রেডিট:** {st.session_state.credits}")

if st.session_state.credits == 0:
    st.sidebar.error("আপনার ক্রেডিট শেষ! দয়া করে রিচার্জ করুন।")

# ডাটাবেস থেকে বর্তমান রেট এবং নাম্বার নিয়ে আসা হচ্ছে
current_rate = get_setting('rate_per_100_tk', '10')
bkash_number = get_setting('bkash_number', '01684545015')

# --- সাধারণ ইউজারদের জন্য রিচার্জ অপশন ---
with st.sidebar.expander("💳 ক্রেডিট রিচার্জ রিকোয়েস্ট দিন"):
    st.info(f"১০০ টাকা = {current_rate} ক্রেডিট\nবিকাশ নম্বর: {bkash_number} (Personal)")
    with st.form("recharge_form"):
        amount = st.number_input("টাকার পরিমাণ:", min_value=100, step=50)
        trx_id = st.text_input("ট্রানজেকশন আইডি (TrxID):", placeholder="যেমন: 8JXXXXXX")
        submitted = st.form_submit_button("সাবমিট রিকোয়েস্ট")
        
        if submitted:
            if trx_id:
                with st.spinner("পেমেন্ট রিকোয়েস্ট পাঠানো হচ্ছে..."):
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("SELECT id FROM payments WHERE trx_id=%s", (trx_id,))
                        
                        if cur.fetchone():
                            st.error("❌ এই ট্রানজেকশন আইডিটি আগে একবার ব্যবহার করা হয়েছে!")
                        else:
                            cur.execute("INSERT INTO payments (user_id, amount, trx_id, status) VALUES (%s, %s, %s, 'pending')", 
                                        (st.session_state.user_id, amount, trx_id))
                            conn.commit()
                            st.success("✅ রিকোয়েস্ট পাঠানো হয়েছে! অ্যাডমিন চেক করে ক্রেডিট যুক্ত করে দিবে।")
                            
                            # অ্যাডমিনকে ইমেইল নোটিফিকেশন পাঠানো হচ্ছে
                            send_admin_email(st.session_state.user_name, "User", amount, trx_id)
                            
                        cur.close()
                        conn.close()
                    except Exception as e:
                        st.error("ডাটাবেস এরর!")
            else:
                st.warning("দয়া করে ট্রানজেকশন আইডি দিন।")
                    

st.sidebar.divider()


st.sidebar.divider()


# পুরনো চ্যাট দেখানো (এই লুপটি ডিলিট হয়ে গিয়েছিল)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# যদি চ্যাট হিস্ট্রি একদম ফাঁকা থাকে, তবে একটি ওয়েলকাম মেসেজ দেখাবে
if len(st.session_state.messages) == 0:
    st.info("👋 **নজির.এআই-তে স্বাগতম!**\n\nআমি আপনার লিগ্যাল রিসার্চ অ্যাসিস্ট্যান্ট। কোনো মামলার রায় বা আইনি নজির খুঁজতে নিচে আপনার প্রশ্নটি লিখুন। (যেমন: *চেক ডিজঅনার মামলায় আসামির জামিন সংক্রান্ত আপিল বিভাগের নজির*)")

# ==========================================
# 🤖 চ্যাটবট এবং n8n লজিক
# ==========================================
if prompt := st.chat_input(CHAT_PLACEHOLDER):
    
    # চেক করবে ক্রেডিট আছে কি না 
    if st.session_state.credits > 0:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("নজির-১ ডেটাবেস থেকে নজির খুঁজছে..."):
            try:
                payload = {
                    "chatInput": prompt,
                    "sessionId": f"user_session_{st.session_state.user_id}",
                    "filters": {
                        "division": division if division != "সিলেক্ট করুন (সব)" else "",
                        "year": case_year,
                        "type": case_type
                    }
                }
                
                response = requests.post(WEBHOOK_URL, json=payload)
                
                if response.status_code == 200:
                    n8n_data = response.json()
                    ai_reply = n8n_data.get("output", "আমি আপনার প্রশ্নটি পেয়েছি, কিন্তু নজির খুঁজে আনতে একটু সমস্যা হচ্ছে।")
                    
                    # N8n থেকে সফলভাবে উত্তর আসার পর ডাটাবেস থেকে ১ ক্রেডিট কেটে নেবে
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE users SET credits = credits - 1 WHERE id = %s", (st.session_state.user_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        st.error("ক্রেডিট আপডেট করতে সমস্যা হয়েছে ডাটাবেসে!")

                    # স্ক্রিনের সেশন স্টেট আপডেট
                    st.session_state.credits -= 1
                else:
                    ai_reply = f"সার্ভার এরর! কানেকশনে সমস্যা হচ্ছে। Status Code: {response.status_code}"
                    
            except Exception as e:
                ai_reply = f"সিস্টেমে একটি কারিগরি ত্রুটি হয়েছে: {e}"

        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    
        st.rerun() # পেজ রিফ্রেশ করে সাইডবারের ক্রেডিট আপডেট করবে

    else:
        # ক্রেডিট ০ হয়ে গেলে এই ব্লক কাজ করবে (n8n এ যাবেই না)
        st.error("⚠️ আপনার ফ্রি ক্রেডিট শেষ হয়ে গেছে!")
        current_rate = get_setting('rate_per_100_tk', '10')
        bkash_number = get_setting('bkash_number', '01684545015')
        
        st.warning(f"""
        **নজির.এআই (Nojir.ai) এর প্রিমিয়াম সার্ভিস চালু করতে রিচার্জ করুন:**
        
        ১. নিচে দেওয়া bKash নাম্বারে **Send Money** করুন।
        ২. **bKash Number:** {bkash_number} (Personal)
        ৩. **প্যাকেজ:** ৳১০০ ({current_rate} ক্রেডিটের জন্য)
        ৪. রেফারেন্স (Reference) এ আপনার ইমেইল বা ফোন নাম্বার দিন।
        
        *টাকা পাঠানোর কিছুক্ষণের মধ্যেই আমরা ম্যানুয়ালি আপনার অ্যাকাউন্টে ক্রেডিট যুক্ত করে দেব।*
        """)