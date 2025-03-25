import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image

# Page Config
st.set_page_config(page_title="UCTP Scheduler", layout="wide")

# 🌈 Custom Styling and Background Theme
st.markdown("""
    <style>
    .main {
        background-color: #fffaf0;
    }
    h1, h2, h3, h4 {
        color: #4b0082;
    }
    .stButton > button {
        background-color: #8a2be2;
        color: white;
        padding: 8px 20px;
        border-radius: 10px;
        font-weight: bold;
    }
    .stDownloadButton > button {
        background-color: #20b2aa;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- University Logo and Name (Top-Left) ---
logo_path = "C:/Users/DELL/Desktop/Basic model/unfc.png"
logo = Image.open(logo_path)
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image(logo, width=120)
with col_title:
    st.markdown("## 🏛️ UNF University\n### 🎓 University Course Timetabling Problem (UCTP) Scheduler")

# --- State Management ---
if "step" not in st.session_state:
    st.session_state.step = "Splash"
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "tables" not in st.session_state:
    st.session_state.tables = {}

# --- Simulated Model Function ---
def run_uctp_model(tables):
    lecturers_df = tables['Lecturers']
    courses_df = tables['Courses']
    rooms_df = tables['Rooms']
    days_df = tables['Days']
    times_df = tables['Time Periods']

    lecturers = lecturers_df['Lecturer Name'].tolist()
    days = days_df['Day'].tolist()
    time_periods = times_df['Time Period'].tolist()
    rooms = rooms_df['Room Number'].tolist()

    course_sections = []
    course_map = {}
    for _, row in courses_df.iterrows():
        code = row['Course Code']
        num_sections = int(row['Number of Sections'])
        for sec in range(1, num_sections + 1):
            cs = f"{code}-{sec}"
            course_sections.append(cs)
            course_map[cs] = code

    schedule_data = []
    for i, cs in enumerate(course_sections):
        course = course_map[cs]
        lecturer = lecturers[i % len(lecturers)]
        room = rooms[i % len(rooms)]
        day = days[i % len(days)]
        period = time_periods[i % len(time_periods)]
        start, end = [datetime.strptime(p, "%H:%M") for p in period.split("-")]
        duration = end - start
        base_day = datetime(2024, 1, 1) + timedelta(days=i % len(days))
        start_dt = datetime.combine(base_day.date(), start.time())
        end_dt = start_dt + duration

        building = rooms_df.loc[rooms_df['Room Number'] == room, 'Building'].values[0]
        location = rooms_df.loc[rooms_df['Room Number'] == room, 'Location'].values[0]

        schedule_data.append({
            'Course': course,
            'Course Section': cs,
            'Lecturer': lecturer,
            'Room': room,
            'Building': building,
            'Location': location,
            'Day': day,
            'Time Period': period,
            'Start': start_dt,
            'End': end_dt
        })

    return pd.DataFrame(schedule_data)

# --- App Pages ---
if st.session_state.step == "Splash":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("👋 Welcome to the UCTP Scheduler!")
        st.markdown("""
            This fun & functional app helps you solve the **University Course Timetabling Problem** 🎓📅
            - 📂 Upload your Excel input file
            - 🛠️ Review and tweak your data
            - 🧠 Run the smart scheduler
            - 📊 Download and explore your timetable
        """)
        st.image("C:/Users/DELL/Desktop/Basic model/giphy.webp", width=150)
        if st.button("🚀 Start Scheduling"):
            st.session_state.step = "Step 1"

    with col2:
        st.image("C:/Users/DELL/Desktop/Basic model/professor.jpg", width=250)
        st.markdown("<h4 style='text-align: left-aligned;'>Hany Osman</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: left-aligned;'>Associate Professor of Data Analytics</p>", unsafe_allow_html=True)

elif st.session_state.step == "Step 1":
    st.header("🧾 Step 1: Upload UCTP Input File")
    uploaded_file = st.file_uploader("Upload your Excel (.xlsx) file", type=["xlsx"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.tables = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        st.success("✅ File uploaded and sheets extracted!")

    st.subheader("👨‍💻 Meet the Developers")
    cols = st.columns(4)
    devs = [
        ("Dev", r"C:/Users/DELL/Desktop/Basic model/dev.png"),
        ("Catherine", r"C:/Users/DELL/Desktop/Basic model/Catherine.png"),
        ("Miko", r"C:/Users/DELL/Desktop/Basic model/Miko.png"),
        ("Rosario", r"C:/Users/DELL/Desktop/Basic model/Rose.png")
    ]
    for col, (name, img_path) in zip(cols, devs):
        image = Image.open(img_path).resize((250, 250))
        col.image(image, caption=name)

    if uploaded_file and st.button("➡️ Next: Edit & Confirm Data"):
        st.session_state.step = "Step 2"

elif st.session_state.step == "Step 2":
    st.header("📋 Step 2: Review & Edit Input Data")
    for name, df in st.session_state.tables.items():
        st.subheader(f"📝 {name}")
        edited = st.data_editor(df, num_rows="dynamic", key=name)
        st.session_state.tables[name] = edited
    if st.button("✅ Run Scheduler & View Results"):
        st.session_state.step = "Step 3"

elif st.session_state.step == "Step 3":
    st.header("📅 Step 3: Schedule Results")

    schedule_df = run_uctp_model(st.session_state.tables)
    st.success("✅ Schedule successfully generated!")

    st.subheader("📋 Generated Timetable")
    st.dataframe(schedule_df)

    towrite = io.BytesIO()
    schedule_df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    st.download_button("📥 Download Timetable as Excel", towrite, file_name="generated_schedule.xlsx")

    st.subheader("📊 Gantt Chart")
    fig = px.timeline(
        schedule_df,
        x_start='Start',
        x_end='End',
        y='Course Section',
        color='Lecturer',
        hover_name='Room',
        text='Course',
        title='Course Schedule'
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📚 Input Tables")
    for name, df in st.session_state.tables.items():
        st.markdown(f"**{name}**")
        st.dataframe(df)

    if st.button("🔁 Start Over"):
        st.session_state.step = "Splash"