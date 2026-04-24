import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load local environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Muneeb's Coffee & Bakery", page_icon="☕", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        .block-container { padding-bottom: 100px; }
        div[data-testid="stChatInput"] { position: fixed; bottom: 20px; z-index: 99; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State (Stored in temporary RAM only)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ORDER BOT SYSTEM INSTRUCTIONS ---
system_instruction = """
You are the Virtual Assistant for 'Muneeb's Coffee & Bakery'. Follow this exact flow:

1. INITIAL STEP: Ask the user: "Welcome! What would you like today? We have Coffee, Cakes, and Cookies."
2. BRANCHING:
   - If user says COFFEE: List types (Espresso, Latte, Cappuccino, Americano) with prices around Rs. 400-600.
   - If user says CAKES: List types (Chocolate Fudge, Red Velvet, Pineapple) with prices around Rs. 1200-1500 per Lb.
   - If user says COOKIES: List types (Almond Biscuits Rs. 800/kg, Chocolate Chip Rs. 1000/kg, Zeera Biscuits Rs. 700/kg).
3. UPSELL: After they pick an item, ask: "Would you like anything else with that?"
4. CONFIRMATION: Once they say "No" or "That's all," provide a final summary of their order and the total price for confirmation.

STRICT RULES:
- Only show the specific list requested.
- Always include prices in Rs.
- Be polite and professional.
"""

# --- Sidebar ---
with st.sidebar:
    st.title("🛒 Shopping Cart")
    st.write("Manage your current order.")
    if st.button("🗑️ Clear Current Order", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main UI ---
st.title("☕ Muneeb's Coffee & Bakery")
st.markdown("#### *Freshly brewed coffee and handmade treats*")

# Display current chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text Input
prompt = st.chat_input("I would like to order...")

# Groq API Setup
api_key = os.getenv("groq_api") or st.secrets.get("groq_api")

if prompt:
    if not api_key:
        st.error("API Key missing! Please add it to Streamlit Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                model="llama-3.1-8b-instant"
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            with st.chat_message("assistant"):
                st.markdown(reply)
                
        except Exception as e:
            st.error(f"Error: {e}")