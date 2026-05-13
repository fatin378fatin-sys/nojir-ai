import streamlit as st
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Secret Admin Panel", page_icon="🔐", layout="centered")

# ==========================================
# 📧 ইমেইল নোটিফিকেশন ফাংশন (ইউজারের জন্য)
# ==========================================
ADMIN_EMAIL = "fatin.shikkha@gmail.com" 
APP_PASSWORD = "keue dkyl zgtp krhc" # আপনার অ্যাপ পাসওয়ার্ডটি এখানে আছে

def send_user_notification(user_email, user_name, status, amount, trx_id, reason= None):
    try:
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = user_email
        
        if status == "Approved":
            msg['Subject'] = "✅ পেমেন্ট অ্যাপ্রুভ করা হয়েছে - নজির.এআই"
            body = f"প্রিয় {user_name},\n\nআপনার ৳{amount} (TrxID: {trx_id}) পেমেন্টটি সফলভাবে অ্যাপ্রুভ করা হয়েছে এবং আপনার অ্যাকাউন্টে ক্রেডিট যুক্ত হয়েছে।\n\nধন্যবাদ,\nনজির.এআই টিম"
        else:
            msg['Subject'] = "❌ পেমেন্ট ডিক্লাইন (Decline) করা হয়েছে - নজির.এআই"
            body = f"প্রিয় {user_name},\n\nদুঃখিত, আপনার ৳{amount} (TrxID: {trx_id}) পেমেন্ট রিকোয়েস্টটি ডিক্লাইন করা হয়েছে।\n\nকারণ: Invalid trx id\n\nআপনার যদি কোনো প্রশ্ন থাকে, দয়া করে আমাদের সাথে যোগাযোগ করুন।\n\nধন্যবাদ,\nনজির.এআই টিম"
        
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_EMAIL, APP_PASSWORD)
        server.sendmail(ADMIN_EMAIL, user_email, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"ইমেইল পাঠাতে সমস্যা হয়েছে: {e}")

# ==========================================
# 🔐 Admin Login System
# ==========================================
ADMIN_PASSWORD = "Fatin378@"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔐 Admin Login")
    password_input = st.text_input("Enter Admin Password:", type="password")
    if st.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("❌ Wrong Password!")
    st.stop()

# ==========================================
# 🗄️ Database Connection
# ==========================================
DB_URL = "postgresql://fatin1_user:SrXReBhReO5hMV42DZBVtOnXKblHvGCH@dpg-d827iiv7f7vs73dshujg-a.ohio-postgres.render.com/fatin1"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# ==========================================
# ⚙️ Admin Dashboard
# ==========================================
st.title("🔐 Secret Admin Panel")

if st.sidebar.button("Logout"):
    st.session_state.admin_logged_in = False
    st.rerun()

st.divider()

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.id, u.name, u.phone, u.email, p.amount, p.trx_id, p.user_id 
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.status = 'pending'
    """)
    pending_requests = cur.fetchall()
    
    if pending_requests:
        st.warning(f"🔔 {len(pending_requests)} টি নতুন পেমেন্ট রিকোয়েস্ট আছে!")
        
        for req in pending_requests:
            payment_id, u_name, u_phone, u_email, p_amount, p_trx, u_id = req
            
            with st.container(border=True):
                st.write(f"**User Name:** {u_name} | **Email:** {u_email}")
                st.write(f"**Amount:** ৳{p_amount} | **TrxID:** `{p_trx}`")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{payment_id}"):
                        cur.execute("SELECT value FROM settings WHERE key_name='rate_per_100_tk'")
                        rate_res = cur.fetchone()
                        current_rate = int(rate_res[0]) if rate_res else 10
                        added_credits = (p_amount // 100) * current_rate
                        
                        cur.execute("UPDATE payments SET status='success' WHERE id=%s", (payment_id,))
                        cur.execute("UPDATE users SET credits = credits + %s WHERE id=%s", (added_credits, u_id))
                        conn.commit()
                        
                        # ইউজারকে কনফার্মেশন মেইল পাঠানো
                        send_user_notification(u_email, u_name, "Approved", p_amount, p_trx)
                        
                        st.success(f"Approved and Email Sent to {u_name}!")
                        st.rerun()
                
                with col2:
                    decline_reason = st.text_input("Decline Reason:", placeholder="যেমন: TrxID ভুল", key=f"reason_{payment_id}")
                    if st.button(f"❌ Decline", key=f"decline_{payment_id}"):
                        if decline_reason:
                            # স্ট্যাটাস 'declined' করা (পেন্ডিং লিস্ট থেকে চলে যাবে, ডাটাবেস ক্লিন থাকবে)
                            cur.execute("UPDATE payments SET status='declined' WHERE id=%s", (payment_id,))
                            conn.commit()
                            
                            # ইউজারকে কারণসহ মেইল পাঠানো
                            send_user_notification(u_email, u_name, "Declined", p_amount, p_trx, decline_reason)
                            
                            st.error(f"Declined and Email Sent to {u_name}!")
                            st.rerun()
                        else:
                            st.warning("দয়া করে ডিক্লাইন করার কারণ লিখুন।")
                            
    else:
        st.info("🎉 এই মুহূর্তে কোনো পেন্ডিং রিকোয়েস্ট নেই।")
        
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Database error: {e}")