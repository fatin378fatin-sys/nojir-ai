import streamlit as st
import requests
import psycopg2 
from streamlit_javascript import st_javascript
import hashlib
import extra_streamlit_components as stx

# ==========================================
# ⚙️ ইউজার কন্ট্রোল প্যানেল 
# ==========================================
SITE_TITLE = "নজির.এআই (Nojir.ai)"
SITE_SUBTITLE = "আপনার স্মার্ট লিগ্যাল রিসার্চ অ্যাসিস্ট্যান্ট - Powered by নজির-১"
PAGE_ICON = "logo.jpg" 
CHAT_PLACEHOLDER = "আপনার আইনি প্রশ্ন বা নজির খুঁজুন... (যেমন: চেক ডিজঅনার মামলার নজির)"
LOGO_FILE = "logo.jpg" 

# n8n Webhook Link
WEBHOOK_URL = "https://nrmckgwe.rpcld.co/webhook/nojir"

st.set_page_config(page_title=SITE_TITLE, page_icon=PAGE_ICON, layout="centered")

# ==========================================
# 🗄️ ডাটাবেস কানেকশন লজিক
# ==========================================
# ==========================================
# 🗄️ ডাটাবেস কানেকশন লজিক
# ==========================================
DB_URL = "postgresql://fatin1_user:SrXReBhReO5hMV42DZBVtOnXKblHvGCH@dpg-d827iiv7f7vs73dshujg-a.ohio-postgres.render.com/fatin1"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@st.cache_resource
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

@st.cache_data(ttl=60) # প্রতি ৬০ সেকেন্ড পর পর ডাটাবেস থেকে আপডেট নিবে
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
            reg_name = st.text_input("আপনার নাম:")
            reg_email = st.text_input("ইমেইল অ্যাড্রেস:")
            reg_phone = st.text_input("ফোন নাম্বার (এটি আপনার পাসওয়ার্ড হিসেবে কাজ করবে):")
            reg_address = st.text_input("চেম্বার/ঠিকানা:")
            
            # জাভাস্ক্রিপ্ট দিয়ে ব্রাউজারের ইউনিক তথ্য আনা হচ্ছে
            browser_info = st_javascript("navigator.userAgent + screen.width + 'x' + screen.height + navigator.language")
            
            # ব্রাউজার ইনফোকে একটি ছোট ইউনিক আইডিতে (Hash) রূপান্তর করা
            if browser_info:
                fingerprint_id = hashlib.md5(str(browser_info).encode()).hexdigest()
            else:
                fingerprint_id = f"{reg_email}_{reg_phone}" 
            
            if st.button("সাইনআপ করুন"):
                if reg_name and reg_email and reg_phone:
                    with st.spinner("আপনার অ্যাকাউন্ট তৈরি হচ্ছে, দয়া করে অপেক্ষা করুন..."):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # চেক করবে ইমেইল, ফোন নাম্বার বা ফিঙ্গারপ্রিন্ট আগে থেকেই আছে কি না
                            cur.execute("SELECT * FROM users WHERE email=%s OR phone=%s OR fingerprint=%s", (reg_email, reg_phone, fingerprint_id))
                            existing_user = cur.fetchone()
                            
                            if existing_user:
                                st.error("⚠️ দুঃখিত! এই ইমেইল, ফোন নাম্বার অথবা ডিভাইস দিয়ে ইতিমধ্যে অ্যাকাউন্ট খোলা হয়েছে।")
                            else:
                                # নতুন ইউজার সেভ করা (প্রাথমিক ১০ ক্রেডিট সহ)
                                cur.execute("""
                                    INSERT INTO users (name, email, phone, address, fingerprint, credits) 
                                    VALUES (%s, %s, %s, %s, %s, 10)
                                """, (reg_name, reg_email, reg_phone, reg_address, fingerprint_id))
                                conn.commit()
                                st.success("✅ অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে! দয়া করে 'লগইন করুন' ট্যাব থেকে লগইন করুন।")
                            
                            cur.close()
                            conn.close()
                        except Exception as e:
                            st.error(f"সাইনআপে সমস্যা হয়েছে: {e}")
                else:
                    st.warning("দয়া করে নাম, ইমেইল এবং ফোন নাম্বার অবশ্যই পূরণ করুন।")

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

st.sidebar.header("🔍 অ্যাডভান্সড ফিল্টার")
division = st.sidebar.selectbox("বিভাগ (Division)", ["সিলেক্ট করুন (সব)", "Appellate Division (AD)", "High Court Division (HCD)"])
case_year = st.sidebar.text_input("মামলার সাল (Year)", placeholder="যেমন: 2024")
case_type = st.sidebar.text_input("মামলার ধরন (Case Type)", placeholder="যেমন: Civil Appeal")

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
                        cur.close()
                        conn.close()
                    except Exception as e:
                        st.error("ডাটাবেস এরর!")
            else:
                st.warning("দয়া করে ট্রানজেকশন আইডি দিন।")

st.sidebar.divider()


# পুরনো চ্যাট দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
                    ai_reply = f"সার্ভার এরর! n8n কানেকশনে সমস্যা হচ্ছে। Status Code: {response.status_code}"
                    
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