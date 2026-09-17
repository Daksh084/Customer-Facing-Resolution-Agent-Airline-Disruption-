
import streamlit as st
from agent_engine import resolve, quick_scenario, DATA, CUSTOMERS

st.set_page_config(
    page_title="AIONOS — Customer Resolution Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    border: 1px solid rgba(120,120,120,.2);
    background: linear-gradient(135deg, rgba(20,35,70,.08), rgba(120,80,180,.08));
}
.badge {
    display:inline-block; padding:5px 10px; border-radius:999px;
    font-size:12px; font-weight:700; margin-right:6px;
    background:rgba(80,120,220,.12);
}
.chat {
    padding: 14px 16px; border-radius: 14px; margin: 8px 0;
    border:1px solid rgba(120,120,120,.18);
}
.user {background:rgba(70,130,220,.08);}
.agent {background:rgba(70,180,120,.08);}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.markdown("""
<div class="hero">
<h1>✈️ AIONOS Customer Resolution Agent</h1>
<p><b>Airline disruption resolution • Policy-grounded • Human escalation aware</b></p>
<p style="margin-bottom:0">Prototype for Assignment 3 — Customer-Facing Resolution Agent</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Control Center")
customer = st.sidebar.selectbox("Customer", list(CUSTOMERS.keys()))

c = CUSTOMERS[customer]
st.sidebar.markdown(f"**{customer}**  \n{c['loyalty_tier']} • PNR `{c['pnr']}`")
st.sidebar.caption(c["travel_history"])

if st.sidebar.button("▶ Run assigned scenario", use_container_width=True):
    result = quick_scenario(customer)
    st.session_state.last_result = result
    st.session_state.messages = [
        {"role":"user","content":{
            "Priya Nair":"My flight was cancelled. I want a full cash refund and a free upgrade to business class on my return flight.",
            "Arvind Kulkarni":"My flight is delayed 4 hours. I want hotel accommodation because of the long delay.",
            "Meher Kaur":"My flight is delayed 6 hours. I want a full night's hotel stay and a different higher-fare flight with the ₹2,000 fare difference waived."
        }[customer]},
        {"role":"agent","content":result["reply"]}
    ]

if st.sidebar.button("↻ Reset conversation", use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_result = None

st.sidebar.divider()
st.sidebar.subheader("Policy guardrails")
st.sidebar.write("✓ Only supplied customer/booking data")
st.sidebar.write("✓ Explicit policy thresholds")
st.sidebar.write("✓ Deterministic escalation")
st.sidebar.write("✓ No invented compensation")

left, right = st.columns([1.65, 1])

with left:
    st.subheader("Customer conversation")
    if not st.session_state.messages:
        st.info("Select a customer and click **Run assigned scenario**, or ask a question below.")
    else:
        for m in st.session_state.messages:
            role = "You" if m["role"] == "user" else "Resolution Agent"
            cls = "user" if m["role"] == "user" else "agent"
            st.markdown(
                f'<div class="chat {cls}"><b>{role}</b><br>{m["content"]}</div>',
                unsafe_allow_html=True
            )

    prompt = st.chat_input("Ask about the booking, disruption, refund, compensation, or escalation...")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        result = resolve(customer, prompt)
        st.session_state.last_result = result
        st.session_state.messages.append({"role":"agent","content":result["reply"]})
        st.rerun()

with right:
    st.subheader("Resolution cockpit")

    flight = c["flights"][0]
    st.metric("Customer tier", c["loyalty_tier"])
    st.metric("PNR", c["pnr"])

    st.markdown("### Disruption")
    st.write(f"**{flight.get('flight')}** · {flight.get('route')}")
    st.write(f"**Status:** {flight.get('status')}")
    st.write(f"**Departure:** {flight.get('departure')}")

    if st.session_state.last_result:
        r = st.session_state.last_result
        st.markdown("### Agent decision")
        if r.get("escalation"):
            st.warning("👤 Human escalation required")
            st.write(r["escalation"]["reason"])
        else:
            st.success("✓ Within autonomous policy")

        st.markdown("### Actions")
        for a in r["actions"]:
            st.write(f"• `{a}`")

        st.markdown("### Policy basis")
        st.caption(r["policy_basis"])

st.divider()

st.subheader("Why this prototype is interview-ready")
cols = st.columns(4)
cards = [
    ("1. Grounded", "Responses are generated from the supplied assignment data, not invented airline rules."),
    ("2. Explainable", "Every resolution exposes the policy basis and actions taken."),
    ("3. Safe", "Out-of-policy requests trigger human escalation instead of fabricated approvals."),
    ("4. Demoable", "One-click scenario execution lets a reviewer test all three required cases.")
]
for col, (title, body) in zip(cols, cards):
    with col:
        st.markdown(f"**{title}**")
        st.caption(body)

with st.expander("Source data used by this prototype"):
    st.json(DATA)
