from pathlib import Path
import uuid
import streamlit as st
from workflow import Scheduler, WARDS

st.set_page_config(page_title="Roster Studio", page_icon="📋", layout="centered")
st.markdown(
    """<style>
.block-container{max-width:900px;padding-top:3rem}h1,h2,h3{font-family:Georgia,serif!important;letter-spacing:-.035em}h1{font-size:3rem!important}div[data-testid="stForm"]{background:#fffdf7;border:1px solid #d5d9cb;border-radius:18px;padding:25px}button{border-radius:8px!important}div[data-testid="stAlert"]{border-radius:12px}@media(max-width:600px){h1{font-size:2rem!important}.block-container{padding-top:1.5rem}}
</style>""",
    unsafe_allow_html=True,
)
st.title("Roster Studio")
st.caption("Fictional assignment workflow · local demonstration")
st.warning(
    "Human-selected fictional routes only. This is not clinical triage or a real hospital scheduling system. Do not enter real patient information."
)
folder = Path(__file__).resolve().parent
(folder / "data").mkdir(exist_ok=True)
scheduler = Scheduler(folder / "data/demo.sqlite3")
scheduler.import_roster(folder / "doctors.example.csv")
if st.button("Start a new request"):
    st.session_state["request_id"] = str(uuid.uuid4())
if "request_id" not in st.session_state:
    st.session_state["request_id"] = str(uuid.uuid4())
request_id = st.session_state["request_id"]
st.caption("Request ID: " + request_id)
with st.form("assignment_form"):
    ward = st.selectbox("Human-selected route", sorted(WARDS))
    submitted = st.form_submit_button("Assign fictional doctor", type="primary")
if submitted:
    try:
        result = scheduler.assign(ward, request_id)
        if result["status"] == "ASSIGNED":
            st.success(f"{result['doctor']} assigned to {result['ward']}.")
        else:
            st.info(result["reason"])
    except ValueError as error:
        st.error(
            str(error) + ". Start a new request to change an already assigned route."
        )
st.subheader("How the demo works")
st.write(
    "Availability is stored in SQLite. Retrying an unchanged request returns the same assignment. A new request cannot take a doctor already assigned. Re-importing the fictional roster does not reset availability."
)
st.caption(
    "No live LLM calls, clinical classification or patient records. The original Colab notebook remains separate."
)
