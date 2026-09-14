import csv
import io
import re
from datetime import date

import streamlit as st

st.set_page_config(
    page_title="Zyphron | Education Companion",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "mode" not in st.session_state:
    st.session_state.mode = None
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "previous_page" not in st.session_state:
    st.session_state.previous_page = "Home"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "saved_content" not in st.session_state:
    st.session_state.saved_content = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = None
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []
if "study_session" not in st.session_state:
    st.session_state.study_session = None
if "study_step" not in st.session_state:
    st.session_state.study_step = 0
if "generated_content" not in st.session_state:
    st.session_state.generated_content = {}
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "concepts_mastered" not in st.session_state:
    st.session_state.concepts_mastered = set()
if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = []
if "achievements" not in st.session_state:
    st.session_state.achievements = set()
if "learning_pack" not in st.session_state:
    st.session_state.learning_pack = None
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "flashcard_revealed" not in st.session_state:
    st.session_state.flashcard_revealed = False
if "socratic_step" not in st.session_state:
    st.session_state.socratic_step = 0
if "socratic_topic" not in st.session_state:
    st.session_state.socratic_topic = ""
if "challenge_complete" not in st.session_state:
    st.session_state.challenge_complete = False
if "attendance_students" not in st.session_state:
    st.session_state.attendance_students = []
if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []
if "attendance_last_saved" not in st.session_state:
    st.session_state.attendance_last_saved = None


def go_to(page):
    st.session_state.previous_page = st.session_state.page
    st.session_state.page = page


def go_back():
    st.session_state.page = st.session_state.previous_page


def select_mode(mode):
    st.session_state.mode = mode
    go_to("Teacher" if mode == "Teacher" else "Student")


def save_content(title, content, category):
    st.session_state.saved_content.append({"title": title, "content": content, "category": category})


def content_actions(title, content, category):
    action_columns = st.columns(3, gap="small")
    with action_columns[0]:
        st.download_button("Download", content, file_name=f"{title.lower().replace(' ', '-')}.txt", use_container_width=True, key=f"download_{category}_{title}")
    with action_columns[1]:
        if st.button("Save", use_container_width=True, key=f"save_{category}_{title}"):
            save_content(title, content, category)
            st.success("Saved to your library.")
    with action_columns[2]:
        st.code(content, language=None)
    with st.expander("Remix this"):
        remix_format = st.selectbox("Turn this into", ["Quiz", "Flashcards", "Study plan", "Exam answer"], key=f"remix_format_{category}_{title}")
        if st.button("Create remix", key=f"remix_{category}_{title}", use_container_width=True):
            remixed = remix_text(content, remix_format)
            st.session_state.generated_content[f"remix_{category}"] = remixed
            st.markdown(remixed)
            st.download_button("Download remix", remixed, file_name=f"{title.lower().replace(' ', '-')}-remix.txt", key=f"download_remix_{category}_{title}")


def explain_topic(topic, level):
    level_intro = {
        "Explain like I'm 10": "Imagine it as a simple story: ",
        "Beginner": "Let's start with the main idea: ",
        "Standard": "The core idea is: ",
        "Advanced": "At a deeper level, the key principle is: ",
    }[level]
    return (f"### {topic}\n\n{level_intro}{topic} is easier to understand when we connect its definition to a real situation. "
            f"Break it into three parts: identify the main idea, observe how the parts interact, and test the idea with an example.\n\n"
            f"**Example:** Consider a familiar situation involving {topic}. First describe what changes, then explain why it changes, and finally predict what happens next.\n\n"
            f"**Quick check:** Can you explain {topic} in one sentence and give one example from everyday life?")


def build_quiz(topic, difficulty, count):
    templates = [
        (f"Which statement best describes {topic}?", [f"It explains a key idea in {topic}", "It is unrelated to learning", "It only applies to one person", "It has no observable examples"], 0),
        (f"What is a useful first step when studying {topic}?", ["Memorize without context", f"Define the main idea of {topic}", "Skip every example", "Avoid questions"], 1),
        (f"Which action shows understanding of {topic}?", ["Repeating a title", "Guessing randomly", "Explaining it with an example", "Leaving it blank"], 2),
        (f"How can you strengthen a weak area in {topic}?", ["Retry a similar question and review the reason", "Stop practicing", "Change the subject immediately", "Ignore feedback"], 0),
        (f"What makes a summary of {topic} useful?", ["It includes every word", "It highlights key ideas and examples", "It has no structure", "It avoids important terms"], 1),
    ]
    return [{"question": q, "options": options, "answer": answer, "topic": topic} for q, options, answer in templates[:count]]


def record_quiz_result(topic, score, total):
    st.session_state.quiz_history.append({"topic": topic, "score": score, "total": total})
    if score < total:
        if topic not in st.session_state.weak_topics:
            st.session_state.weak_topics.append(topic)
    else:
        st.session_state.concepts_mastered.add(topic)
    st.session_state.xp += score * 20
    if len(st.session_state.quiz_history) == 1:
        st.session_state.achievements.add("First Quiz")
    if score == total:
        st.session_state.achievements.add("Perfect Score")
    if score >= 5:
        st.session_state.achievements.add("5 Questions Correct")


def make_learning_pack(topic, source):
    notes = source.strip() or f"Core notes about {topic} and its most important ideas."
    summary = f"{topic} becomes clearer when you connect its definition, its main relationships, and one real-world example. Use the notes as a starting point, then explain the idea without looking."
    return {
        "topic": topic,
        "source": notes,
        "summary": summary,
        "key_concepts": [f"Definition and purpose of {topic}", f"The main relationship inside {topic}", f"A practical example of {topic}"],
        "flashcards": [(f"What is the central idea of {topic}?", f"It is the definition, purpose, and key relationship that make {topic} useful."), (f"How would you apply {topic}?", "Describe the situation, identify the changing parts, and explain the result."), (f"How can you check your understanding of {topic}?", "Explain it in your own words and solve one new example.")],
        "study_plan": ["5 min - Read the summary and define the vocabulary", "10 min - Work through the key relationship and example", "10 min - Test yourself with the quiz", "5 min - Review weak points and explain the topic aloud"],
    }


def remix_text(content, format_name):
    if format_name == "Quiz":
        return f"# Remix Quiz\n\n1. What is the central idea?\n2. Give one example.\n3. Explain the most important relationship in your own words.\n\nSource:\n{content}"
    if format_name == "Flashcards":
        return f"# Remix Flashcards\n\nQ: What is the main idea?\nA: Review the definition and purpose.\n\nQ: How would you use it?\nA: Connect it to a new example.\n\nSource:\n{content}"
    if format_name == "Exam answer":
        return f"# Exam-ready answer\n\n{content}\n\nUse the structure: definition, explanation, example, conclusion."
    return f"# Study plan\n\n1. Identify the key idea.\n2. Review the example.\n3. Answer three practice questions.\n4. Revisit the part that felt least certain.\n\nSource:\n{content}"


def parse_student_list(pasted_names, uploaded_csv):
    students = []
    if uploaded_csv is not None:
        rows = csv.DictReader(io.StringIO(uploaded_csv.getvalue().decode("utf-8-sig")))
        for index, row in enumerate(rows, 1):
            normalized = {str(key).strip().lower(): str(value).strip() for key, value in row.items() if key}
            name = normalized.get("name") or normalized.get("student name") or next(iter(normalized.values()), "")
            roll = normalized.get("roll no") or normalized.get("roll") or str(index)
            if name:
                students.append({"roll": roll, "name": name, "present": True})
    else:
        for index, raw_line in enumerate(pasted_names.splitlines(), 1):
            line = raw_line.strip()
            if not line:
                continue
            match = re.match(r"^(\d+)\s*[.)-]\s*(.+)$", line)
            if match:
                roll, name = match.groups()
            else:
                roll, name = str(index), line
            students.append({"roll": roll.strip(), "name": name.strip(), "present": True})
    return students


def attendance_csv(record):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Institution", "Zyphron Classroom"])
    writer.writerow(["Class", record["class_name"]])
    writer.writerow(["Division", record["division"]])
    writer.writerow(["Subject", record["subject"]])
    writer.writerow(["Date", record["date"]])
    writer.writerow(["Period", record["period"]])
    writer.writerow([])
    writer.writerow(["Roll number", "Student name", "Status"])
    for student in record["students"]:
        writer.writerow([student["roll"], student["name"], "Present" if student["present"] else "Absent"])
    writer.writerow([])
    writer.writerow(["Total present", record["present_count"]])
    writer.writerow(["Total absent", record["absent_count"]])
    writer.writerow(["Attendance percentage", f"{record['percentage']:.1f}%"])
    return output.getvalue()


def toggle_attendance(roll):
    for student in st.session_state.attendance_students:
        if student["roll"] == roll:
            student["present"] = not student["present"]
            break


def attendance_record(date_value, class_name, division, subject, period):
    students = [dict(student) for student in st.session_state.attendance_students]
    present_count = sum(student["present"] for student in students)
    absent_count = len(students) - present_count
    return {"date": date_value.isoformat(), "class_name": class_name, "division": division, "subject": subject, "period": period, "students": students, "present_count": present_count, "absent_count": absent_count, "percentage": (present_count / len(students) * 100) if students else 0}


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Mono:wght@400;700&display=swap');

    :root {
        --ink: #f2edda;
        --muted: #a9b3a2;
        --lavender: #f2bd5d;
        --violet: #68d391;
        --purple: #68d391;
        --deep: #0b0f0e;
        --glass: #111917;
        --line: #3c5548;
        --cyan: #82d9df;
        --danger: #ef7168;
    }

    .stApp {
        min-height: 100vh;
        color: var(--ink);
        background-color: #0b0f0e;
        background-image: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.018) 0, rgba(255, 255, 255, 0.018) 1px, transparent 1px, transparent 4px);
        font-family: 'Space Mono', monospace;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        position: relative;
        z-index: 1;
        max-width: 1180px;
        padding: 1.4rem clamp(1rem, 3vw, 2.2rem) 2rem;
    }

    .hero {
        position: relative;
        max-width: 830px;
        margin: 0 auto 6.2rem;
        text-align: center;
        animation: rise 260ms ease-out both;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1.35rem;
        color: var(--lavender);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    .eyebrow:before {
        content: '';
        width: 2.2rem;
        height: 1px;
        background: var(--lavender);
    }

    .hero h1 {
        margin: 0;
        color: var(--ink);
        font-family: 'Press Start 2P', monospace;
        font-size: clamp(2.1rem, 6vw, 5rem);
        font-weight: 700;
        letter-spacing: -0.06em;
        line-height: 0.96;
        text-shadow: 3px 3px 0 #263a30;
    }

    .hero h1 span {
        color: var(--lavender);
    }

    .hero h2 {
        margin: 1.5rem 0 1rem;
        color: #e5d9fa;
        font-family: 'Space Mono', monospace;
        font-size: clamp(1.05rem, 2.5vw, 1.65rem);
        font-weight: 500;
    }

    .hero p {
        max-width: 625px;
        margin: 0 auto;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.75;
    }

    .hero:after { display: none; }

    .stButton > button {
        width: 100%;
        min-height: 2.8rem;
        padding: 0.65rem 1rem;
        border: 1px solid rgba(233, 220, 255, 0.24);
        border-radius: 0;
        color: #fff;
        background: #16221c;
        font-family: 'Space Mono', monospace;
        font-size: 0.78rem;
        letter-spacing: 0.02em;
        font-weight: 600;
        box-shadow: 3px 3px 0 #050706;
        transition: border-color 100ms ease, background 100ms ease, transform 100ms ease, box-shadow 100ms ease;
    }

    .stButton > button p {
        white-space: normal;
        overflow-wrap: anywhere;
        line-height: 1.25;
    }

    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {
        min-height: 2.8rem;
        font-size: 1rem;
    }

    .stButton > button:hover {
        border-color: var(--lavender);
        background: #213127;
    }

    .stButton > button:active {
        transform: translate(3px, 3px);
        box-shadow: none;
    }

    .stButton > button:focus-visible,
    .stTextInput input:focus-visible,
    .stTextArea textarea:focus-visible,
    [data-baseweb="select"] > div:focus-within,
    [data-baseweb="tab"]:focus-visible {
        outline: 2px solid var(--lavender);
        outline-offset: 2px;
    }

    .cta-row {
        max-width: 520px;
        margin: 2.1rem auto 0;
    }

    .section-heading {
        margin: 0 0 1.8rem;
        color: var(--ink);
        font-family: 'Press Start 2P', monospace;
        font-size: clamp(1.7rem, 3vw, 2.35rem);
        letter-spacing: 0.02em;
    }

    .section-heading span {
        color: var(--lavender);
    }

    .section-lead {
        margin: -1rem 0 1.8rem;
        color: var(--muted);
        font-size: 0.94rem;
    }

    .glass-card {
        position: relative;
        height: 100%;
        min-height: 185px;
        overflow: hidden;
        padding: 1.55rem;
        border: 1px solid var(--line);
        border-radius: 0;
        background: var(--glass);
        box-shadow: 4px 4px 0 #050706;
        transition: border-color 140ms ease, background 140ms ease;
    }

    .glass-card:hover {
        border-color: var(--violet);
        background: #17251d;
    }

    .glass-card:after { display: none; }

    .card-number {
        display: inline-grid;
        width: 2rem;
        height: 2rem;
        margin-bottom: 1.1rem;
        place-items: center;
        border: 1px solid rgba(218, 199, 255, 0.3);
        border-radius: 0;
        color: var(--lavender);
        background: #20382a;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .glass-card h3 {
        margin: 0 0 0.55rem;
        color: #f5efff;
        font-family: 'Press Start 2P', monospace;
        font-size: 0.8rem;
        font-size: 1.05rem;
    }

    .glass-card p {
        margin: 0;
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.65;
    }

    .section-block {
        margin-bottom: 6rem;
        animation: rise 260ms ease-out both;
    }

    .solution-block {
        padding: 2.7rem 0 0;
        border-top: 1px solid rgba(219, 198, 255, 0.12);
        animation-delay: 60ms;
    }

    .mode-note {
        margin: 1.2rem 0 0;
        padding: 0.85rem 1rem;
        border: 1px solid rgba(208, 190, 255, 0.2);
        border-radius: 0;
        color: var(--lavender);
        background: #1b2b22;
        text-align: center;
        font-size: 0.88rem;
    }

    .footer {
        padding: 2rem 0 0.7rem;
        border-top: 1px solid rgba(219, 198, 255, 0.14);
        color: #a99cc4;
        text-align: center;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
    }

    .nav-shell {
        margin: 0 0 2.5rem;
        padding: 0.55rem;
        border: 1px solid var(--line);
        border-radius: 0;
        background: #111917;
        box-shadow: 4px 4px 0 #050706;
    }

    .nav-caption {
        padding: 0.25rem 0.7rem 0.35rem;
        color: #a99cc4;
        font-family: 'Press Start 2P', monospace;
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .page-title {
        margin: 0 0 0.5rem;
        color: var(--ink);
        font-family: 'Press Start 2P', monospace;
        font-size: clamp(1.35rem, 3vw, 2.4rem);
        letter-spacing: 0.02em;
    }

    .page-intro {
        max-width: 680px;
        margin: 0 0 2rem;
        color: var(--muted);
        line-height: 1.7;
    }

    .dashboard-shell {
        margin-bottom: 2.5rem;
        padding: clamp(1rem, 2.5vw, 1.7rem);
        border: 1px solid var(--line);
        border-radius: 0;
        background: #0f1714;
        box-shadow: 4px 4px 0 #050706;
    }

    .dashboard-shell [data-baseweb="tab-list"] {
        gap: 0.35rem;
        flex-wrap: wrap;
    }

    .dashboard-shell [data-baseweb="tab"] {
        min-height: 2.7rem;
        padding: 0.55rem 0.8rem;
        color: var(--muted);
        white-space: normal;
    }

    .tool-header {
        margin: 0.5rem 0 1.1rem;
        color: var(--ink);
        font-family: 'Press Start 2P', monospace;
        font-size: 0.8rem;
        font-size: 1.35rem;
    }

    .feature-card {
        min-height: 145px;
    }

    .chat-box {
        min-height: 120px;
        margin-bottom: 1rem;
        padding: 1rem 1.15rem;
        border: 1px solid var(--line);
        border-radius: 0;
        background: #111917;
        color: var(--muted);
        line-height: 1.65;
        backdrop-filter: blur(16px);
    }

    .chat-label {
        display: block;
        margin-bottom: 0.3rem;
        color: var(--lavender);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .flow-note {
        margin: 1rem 0 0;
        padding: 0.85rem 1rem;
        border-left: 2px solid var(--violet);
        color: var(--muted);
        background: rgba(127, 75, 219, 0.1);
    }

    @keyframes rise {
        from { opacity: 0; transform: translateY(18px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 1ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 1ms !important;
            scroll-behavior: auto !important;
        }
    }

    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem 1.5rem; }
        .hero { margin-bottom: 4.4rem; }
        .hero h1 { font-size: clamp(1.35rem, 7.8vw, 2rem); line-height: 1.35; white-space: nowrap; }
        .hero h2 { font-size: 0.95rem; line-height: 1.35; }
        .hero p { font-size: 0.92rem; }
        .section-block { margin-bottom: 4.4rem; }
        .glass-card { min-height: 0; }
        .nav-shell { margin-top: -0.8rem; margin-bottom: 1.8rem; padding: 0.35rem; }
        .nav-caption { padding-left: 0.4rem; }
        .nav-shell .stButton > button { min-height: 2.7rem; padding: 0.5rem 0.3rem; font-size: 0.72rem; }
        .dashboard-shell { padding: 0.85rem; }
        .dashboard-shell [data-baseweb="tab"] { flex: 1 1 45%; text-align: center; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

navigation = [
    ("🏠 Home", "Home"),
    ("🎓 Student", "Student"),
    ("👨‍🏫 Teacher", "Teacher"),
    ("ℹ️ About", "About"),
]
st.markdown('<div class="nav-shell"><div class="nav-caption">Explore Zyphron</div>', unsafe_allow_html=True)
nav_columns = st.columns(len(navigation), gap="small")
for column, (label, page) in zip(nav_columns, navigation):
    with column:
        st.button(label, key=f"nav_{page}", use_container_width=True, on_click=go_to, args=(page,))
st.markdown("</div>", unsafe_allow_html=True)


def page_header(title, description):
    if not st.session_state.get("embedded_feature"):
        back_column, home_column = st.columns([1, 1], gap="small")
        with back_column:
            st.button("← Back", key=f"back_{title}", use_container_width=True, on_click=go_back, disabled=st.session_state.page == "Home")
        with home_column:
            st.button("⌂ Home", key=f"home_{title}", use_container_width=True, on_click=go_to, args=("Home",))
    st.markdown(f'<h1 class="page-title">{title}</h1><p class="page-intro">{description}</p>', unsafe_allow_html=True)


def feature_card(number, title, description, action_label, target_page):
    st.markdown(
        f'<article class="glass-card feature-card"><div class="card-number">{number}</div><h3>{title}</h3><p>{description}</p></article>',
        unsafe_allow_html=True,
    )
    st.button(action_label, key=f"action_{target_page}_{number}", use_container_width=True, on_click=go_to, args=(target_page,))


def learning_status():
    metrics = st.columns(4, gap="small")
    metrics[0].metric("⚡ XP", st.session_state.xp)
    metrics[1].metric("🔥 Streak", f"{st.session_state.streak} session" if st.session_state.streak == 1 else f"{st.session_state.streak} sessions")
    metrics[2].metric("🧠 Mastered", len(st.session_state.concepts_mastered))
    metrics[3].metric("🎯 Weak areas", len(st.session_state.weak_topics))
    if st.session_state.weak_topics:
        st.markdown(f'<div class="flow-note"><strong>Recommended next step:</strong> Review {st.session_state.weak_topics[-1]}, then try three easier targeted questions.</div>', unsafe_allow_html=True)
    if st.session_state.achievements:
        st.caption("Achievements: " + " · ".join(sorted(st.session_state.achievements)))


def socratic_response(topic, step):
    prompts = [
        f"Let's investigate {topic}. What do you already think is causing or controlling it?",
        f"Good starting point. For {topic}, what force, rule, or relationship might explain that observation?",
        f"Now connect your idea to an example. What would happen if one part of {topic} changed?",
    ]
    return prompts[min(step, len(prompts) - 1)]


def learning_pack_page():
    st.markdown('<h2 class="tool-header">📦 Turn Anything Into Learning</h2>', unsafe_allow_html=True)
    st.caption("Paste notes once. Zyphron turns them into a summary, key concepts, flashcards, quiz, and study plan.")
    topic = st.text_input("Topic", placeholder="Newton's Laws", key="pack_topic")
    source = st.text_area("Paste your notes or study text", placeholder="Paste a paragraph, class notes, or a textbook excerpt.", height=140, key="pack_source")
    if st.button("Generate Learning Pack", type="primary", use_container_width=True, key="generate_pack"):
        if not topic.strip():
            st.warning("Add a topic so the learning pack can be organized.")
        else:
            st.session_state.learning_pack = make_learning_pack(topic.strip(), source)
            st.session_state.flashcards = st.session_state.learning_pack["flashcards"]
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_revealed = False
            st.session_state.xp += 10
            st.session_state.streak = max(1, st.session_state.streak + 1)
    pack = st.session_state.learning_pack
    if not pack:
        st.info("Your generated learning pack will appear here.")
        return
    pack_tabs = st.tabs(["📖 Summary", "🧠 Key concepts", "📝 Quiz", "🃏 Flashcards", "⏱️ Study plan"])
    with pack_tabs[0]:
        st.markdown(f"### {pack['topic']}\n\n{pack['summary']}")
        content_actions(f"{pack['topic']} learning summary", pack["summary"], "learning-pack-summary")
    with pack_tabs[1]:
        for concept in pack["key_concepts"]:
            st.markdown(f"- {concept}")
    with pack_tabs[2]:
        st.markdown("### Practice the pack")
        for index, question in enumerate(build_quiz(pack["topic"], "Beginner", 3)):
            st.markdown(f"**{index + 1}. {question['question']}**")
    with pack_tabs[3]:
        flashcard_page(compact=True)
    with pack_tabs[4]:
        st.markdown("\n".join(f"- {step}" for step in pack["study_plan"]))


def flashcard_page(compact=False):
    st.markdown('<h2 class="tool-header">🃏 Flashcards</h2>', unsafe_allow_html=True)
    key_prefix = "pack_" if compact else "main_"
    if not st.session_state.flashcards:
        st.info("Generate a Learning Pack to create flashcards, or start with a topic below.")
        topic = st.text_input("Flashcard topic", placeholder="Inertia", key=f"{key_prefix}flashcard_topic")
        if st.button("Create Flashcards", use_container_width=True, key=f"{key_prefix}create_flashcards") and topic.strip():
            st.session_state.flashcards = make_learning_pack(topic.strip(), "")["flashcards"]
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_revealed = False
            st.rerun()
        return
    question, answer = st.session_state.flashcards[st.session_state.flashcard_index]
    st.markdown(f'<div class="glass-card flashcard"><div class="card-number">{st.session_state.flashcard_index + 1}/{len(st.session_state.flashcards)}</div><h3>{question}</h3></div>', unsafe_allow_html=True)
    if st.session_state.flashcard_revealed:
        st.markdown(f'<div class="flow-note"><strong>Answer</strong><br>{answer}</div>', unsafe_allow_html=True)
        known_col, revise_col = st.columns(2, gap="small")
        with known_col:
            if st.button("I knew it", use_container_width=True, key=f"{key_prefix}flash_known"):
                st.session_state.xp += 10
                st.session_state.flashcard_revealed = False
                st.session_state.flashcard_index = (st.session_state.flashcard_index + 1) % len(st.session_state.flashcards)
                st.rerun()
        with revise_col:
            if st.button("Need revision", use_container_width=True, key=f"{key_prefix}flash_revision"):
                st.session_state.weak_topics.append(question)
                st.session_state.flashcard_revealed = False
                st.session_state.flashcard_index = (st.session_state.flashcard_index + 1) % len(st.session_state.flashcards)
                st.rerun()
    elif st.button("Reveal", type="primary", use_container_width=True, key=f"{key_prefix}flash_reveal"):
        st.session_state.flashcard_revealed = True
        st.rerun()
    control_columns = st.columns(3, gap="small")
    with control_columns[0]:
        if st.button("Previous", use_container_width=True, key=f"{key_prefix}flash_previous"):
            st.session_state.flashcard_index = (st.session_state.flashcard_index - 1) % len(st.session_state.flashcards)
            st.session_state.flashcard_revealed = False
            st.rerun()
    with control_columns[1]:
        if st.button("Next", use_container_width=True, key=f"{key_prefix}flash_next"):
            st.session_state.flashcard_index = (st.session_state.flashcard_index + 1) % len(st.session_state.flashcards)
            st.session_state.flashcard_revealed = False
            st.rerun()
    with control_columns[2]:
        if st.button("Restart", use_container_width=True, key=f"{key_prefix}flash_restart"):
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_revealed = False
            st.rerun()


def knowledge_map_page():
    st.markdown('<h2 class="tool-header">🗺️ Knowledge Map</h2>', unsafe_allow_html=True)
    topic = st.selectbox("Choose a topic", ["Newton's Laws", "Photosynthesis", "Fractions", "The Water Cycle"], key="map_topic")
    relationships = {
        "Newton's Laws": ("Force and Motion", "Newton's Laws", "Momentum", "Energy"),
        "Photosynthesis": ("Cells and Light", "Photosynthesis", "Plant Respiration", "Food Chains"),
        "Fractions": ("Whole Numbers", "Fractions", "Ratios", "Percentages"),
        "The Water Cycle": ("States of Matter", "The Water Cycle", "Weather", "Climate"),
    }
    prerequisite, current, related, next_topic = relationships[topic]
    map_columns = st.columns(4, gap="small")
    for column, label, value in zip(map_columns, ["Prerequisite", "Current focus", "Related", "Recommended next"], relationships[topic]):
        with column:
            st.markdown(f'<article class="glass-card map-node"><div class="card-number">→</div><h3>{label}</h3><p>{value}</p></article>', unsafe_allow_html=True)


def quick_challenge_page():
    st.markdown('<h2 class="tool-header">⚡ Quick Challenge</h2>', unsafe_allow_html=True)
    st.markdown("**A 2kg object experiences a force of 10N. What is its acceleration?**")
    answer = st.number_input("Your answer in m/s²", min_value=0.0, step=0.5, key="challenge_answer")
    if st.button("Check answer", type="primary", use_container_width=True, key="check_challenge"):
        if answer == 5:
            st.session_state.challenge_complete = True
            st.session_state.xp += 20
            st.session_state.achievements.add("Quick Challenge")
            st.success("Correct! +20 XP")
        else:
            st.warning("Not quite. Use acceleration = force ÷ mass.")
    if st.session_state.challenge_complete:
        st.caption("Challenge completed in this session.")


def quick_attendance_page():
    st.markdown('<h2 class="tool-header">📋 Quick Attendance</h2>', unsafe_allow_html=True)
    st.caption("Take attendance in seconds. Everyone starts Present, so you only need to tap absent students.")
    details = st.columns([1.2, 1.1, 0.8, 1.2, 0.8], gap="small")
    with details[0]:
        attendance_date = st.date_input("Date", value=date.today(), key="attendance_date")
    with details[1]:
        class_name = st.text_input("Class", placeholder="Grade 8", key="attendance_class")
    with details[2]:
        division = st.text_input("Division", placeholder="A", key="attendance_division")
    with details[3]:
        subject = st.text_input("Subject", placeholder="Mathematics", key="attendance_subject")
    with details[4]:
        period = st.text_input("Period", placeholder="1", key="attendance_period")

    input_tabs = st.tabs(["Paste names", "Upload CSV"])
    with input_tabs[0]:
        pasted_names = st.text_area("Student list", placeholder="1. Rahul\n2. Anu\n3. Adithya", height=125, key="attendance_pasted_names")
        if st.button("Load Class", type="primary", use_container_width=True, key="load_attendance_names"):
            students = parse_student_list(pasted_names, None)
            if not students:
                st.warning("Paste at least one student name.")
            else:
                st.session_state.attendance_students = students
                st.session_state.attendance_last_saved = None
                st.rerun()
    with input_tabs[1]:
        uploaded_csv = st.file_uploader("CSV with Roll No and Name", type=["csv"], key="attendance_csv_upload")
        if st.button("Load CSV Class", type="primary", use_container_width=True, key="load_attendance_csv"):
            if uploaded_csv is None:
                st.warning("Choose a CSV file first.")
            else:
                students = parse_student_list("", uploaded_csv)
                if not students:
                    st.warning("The CSV needs at least one student name.")
                else:
                    st.session_state.attendance_students = students
                    st.session_state.attendance_last_saved = None
                    st.rerun()

    students = st.session_state.attendance_students
    if not students:
        st.info("Load a class list to begin. Every student will start as Present.")
        return

    st.markdown(f"### Attendance · {len(students)} students")
    action_columns = st.columns(3, gap="small")
    with action_columns[0]:
        if st.button("Mark All Present", use_container_width=True, key="attendance_all_present"):
            for student in students:
                student["present"] = True
            st.rerun()
    with action_columns[1]:
        if st.button("Clear Attendance", use_container_width=True, key="attendance_clear"):
            for student in students:
                student["present"] = True
            st.rerun()
    with action_columns[2]:
        save_attendance = st.button("Save Attendance", type="primary", use_container_width=True, key="save_attendance")

    for student in students:
        row_columns = st.columns([0.65, 3.2, 1.45], gap="small")
        with row_columns[0]:
            st.markdown(f"**{student['roll']}**")
        with row_columns[1]:
            st.markdown(f"**{student['name']}**")
        with row_columns[2]:
            status = "Present" if student["present"] else "Absent"
            st.button(status, key=f"attendance_toggle_{student['roll']}", use_container_width=True, on_click=toggle_attendance, args=(student["roll"],))

    if save_attendance:
        if not class_name.strip() or not subject.strip():
            st.warning("Add the class and subject before saving attendance.")
        else:
            record = attendance_record(attendance_date, class_name.strip(), division.strip(), subject.strip(), period.strip())
            st.session_state.attendance_records.append(record)
            st.session_state.attendance_last_saved = record
            st.session_state.xp += 10
            st.success("Attendance saved.")

    record = st.session_state.attendance_last_saved
    if record:
        absent_students = [student for student in record["students"] if not student["present"]]
        st.markdown("### Attendance Summary")
        summary_columns = st.columns(4, gap="small")
        summary_columns[0].metric("Total students", len(record["students"]))
        summary_columns[1].metric("Present", record["present_count"])
        summary_columns[2].metric("Absent", record["absent_count"])
        summary_columns[3].metric("Attendance", f"{record['percentage']:.1f}%")
        if absent_students:
            st.markdown("#### 📋 Copy Absent List")
            absent_text = f"Absent Students – {date.fromisoformat(record['date']).strftime('%d %B %Y')}\n\n" + "\n".join(f"{student['roll']} – {student['name']}" for student in absent_students)
            st.code(absent_text, language=None)
        else:
            st.success("Everyone is present.")
        sheet = attendance_csv(record)
        st.download_button("📄 Generate Attendance Sheet", sheet, file_name=f"attendance-{record['date']}.csv", mime="text/csv", use_container_width=True, key="download_attendance_sheet")
        st.caption("The absent list above includes a copy control for WhatsApp, email, or your school system.")

    if st.session_state.attendance_records:
        st.markdown("### Recent Attendance")
        for history_record in reversed(st.session_state.attendance_records[-5:]):
            formatted_date = date.fromisoformat(history_record["date"]).strftime("%d %b")
            st.markdown(f"**{formatted_date}** — {history_record['subject']} — {history_record['present_count']}/{len(history_record['students'])}")
        total_students = sum(len(item["students"]) for item in st.session_state.attendance_records)
        total_present = sum(item["present_count"] for item in st.session_state.attendance_records)
        student_absences = {}
        student_totals = {}
        for history_record in st.session_state.attendance_records:
            for student in history_record["students"]:
                student_totals[student["name"]] = student_totals.get(student["name"], 0) + 1
                if not student["present"]:
                    student_absences[student["name"]] = student_absences.get(student["name"], 0) + 1
        average = total_present / total_students * 100 if total_students else 0
        most_absent = max(student_absences, key=student_absences.get) if student_absences else "None yet"
        below_75 = sum(1 for name, total in student_totals.items() if student_absences.get(name, 0) / total > 0.25)
        st.markdown("### Class Attendance Insights")
        insight_columns = st.columns(3, gap="small")
        insight_columns[0].metric("Average attendance", f"{average:.1f}%")
        insight_columns[1].metric("Most absent", most_absent)
        insight_columns[2].metric("Students below 75%", below_75)


def class_copilot_page():
    st.markdown('<h2 class="tool-header">🎤 Class Copilot</h2>', unsafe_allow_html=True)
    topic = st.text_input("What is the class about?", placeholder="I have a 40-minute class on photosynthesis.", key="copilot_topic")
    if st.button("Generate class flow", type="primary", use_container_width=True, key="generate_copilot"):
        if not topic.strip():
            st.warning("Add a class topic first.")
        else:
            content = f"# Class Copilot · {topic.strip()}\n\n0–5 min · Warm-up question\n\n5–15 min · Concept explanation\n\n15–25 min · Interactive activity\n\n25–35 min · Student questions\n\n35–40 min · Quick assessment"
            st.session_state.generated_content["copilot"] = content
    if st.session_state.generated_content.get("copilot"):
        st.markdown(st.session_state.generated_content["copilot"])
        content_actions("Class copilot", st.session_state.generated_content["copilot"], "copilot")


def presentation_page():
    st.markdown('<h2 class="tool-header">🖥️ Presentation Mode</h2>', unsafe_allow_html=True)
    source = st.session_state.generated_content.get("lesson") or st.session_state.generated_content.get("copilot")
    if not source:
        st.info("Generate a lesson plan or Class Copilot flow first.")
        return
    slides = [line.strip("# ") for line in source.splitlines() if line.strip()][:5]
    index = min(st.session_state.get("presentation_index", 0), len(slides) - 1)
    st.markdown(f'<div class="glass-card presentation-slide"><div class="eyebrow">Slide {index + 1} of {len(slides)}</div><h2>{slides[index]}</h2><p>One concept at a time. Explain it, ask a question, then move forward.</p></div>', unsafe_allow_html=True)
    previous, next_slide = st.columns(2, gap="small")
    with previous:
        if st.button("← Previous", disabled=index == 0, use_container_width=True, key="presentation_previous"):
            st.session_state.presentation_index = index - 1
            st.rerun()
    with next_slide:
        if st.button("Next →", disabled=index == len(slides) - 1, use_container_width=True, key="presentation_next"):
            st.session_state.presentation_index = index + 1
            st.rerun()


def home_page():
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">Learning, made clearer</div>
            <h1><span>Zyphron</span></h1>
            <h2>Intelligent Education, Redefined</h2>
            <p>A thoughtful education companion that helps teachers create lesson plans and quizzes, while helping students clear doubts instantly.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="cta-row">', unsafe_allow_html=True)
    start_column, lesson_column, doubt_column = st.columns(3, gap="small")
    with start_column:
        st.button("Start Learning", use_container_width=True, on_click=go_to, args=("Student",))
    with lesson_column:
        st.button("Create Lesson", use_container_width=True, on_click=go_to, args=("Teacher",))
    with doubt_column:
        st.button("Ask a Doubt", use_container_width=True, on_click=go_to, args=("Doubt Solver",))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<section class="section-block"><h2 class="section-heading">The <span>Challenge</span></h2><p class="section-lead">Small frictions can make learning feel much harder than it needs to be.</p>', unsafe_allow_html=True)
    problem_cards = [
        ("01", "Time-heavy preparation", "Teachers spend hours creating lesson plans and quizzes instead of focusing on their classrooms."),
        ("02", "Doubts left waiting", "Students need clear, instant explanations that meet them at their level and pace."),
        ("03", "A complex tool landscape", "Education needs focused, easy-to-use tools that make everyday learning support simpler."),
    ]
    problem_columns = st.columns(3, gap="medium")
    for column, (number, title, description) in zip(problem_columns, problem_cards):
        with column:
            st.markdown(f'<article class="glass-card"><div class="card-number">{number}</div><h3>{title}</h3><p>{description}</p></article>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section class="section-block solution-block"><h2 class="section-heading">How Zyphron <span>Helps</span></h2><p class="section-lead">A calm, capable companion for every part of the learning journey.</p>', unsafe_allow_html=True)
    solution_cards = [
        ("01", "For Teachers", "Create instant lesson plans and quizzes with practical classroom support."),
        ("02", "For Students", "Clear doubts with simple explanations, examples, and a conversation that remembers the thread."),
        ("03", "Smart & Fast", "Get clean, focused, and intelligent responses for everyday education needs."),
    ]
    solution_columns = st.columns(3, gap="medium")
    for column, (number, title, description) in zip(solution_columns, solution_cards):
        with column:
            st.markdown(f'<article class="glass-card"><div class="card-number">{number}</div><h3>{title}</h3><p>{description}</p></article>', unsafe_allow_html=True)
    st.markdown('</section><footer class="footer">Zyphron • Built for the future of education | Conclave 2026</footer>', unsafe_allow_html=True)


def student_page():
    st.session_state.embedded_feature = True
    page_header("Student Dashboard", "Learn clearly, practice deliberately, and turn weak areas into the next step.")
    st.markdown('<div class="dashboard-shell">', unsafe_allow_html=True)
    st.markdown("### Quick start\nChoose a focused tool and keep the whole learning loop in one place.")
    learning_status()
    student_tabs = st.tabs(["💬 Doubt", "📦 Learning Pack", "🧠 Study", "📝 Quiz", "🃏 Flashcards", "🗺️ Map", "⚡ Challenge", "📊 Progress", "⭐ Saved"])
    with student_tabs[0]:
        doubt_page()
    with student_tabs[1]:
        learning_pack_page()
    with student_tabs[2]:
        study_page()
    with student_tabs[3]:
        quiz_page()
    with student_tabs[4]:
        flashcard_page()
    with student_tabs[5]:
        knowledge_map_page()
    with student_tabs[6]:
        quick_challenge_page()
    with student_tabs[7]:
        progress_page()
    with student_tabs[8]:
        saved_page()
    st.session_state.embedded_feature = False
    st.markdown('</div>', unsafe_allow_html=True)


def teacher_page():
    st.session_state.embedded_feature = True
    page_header("Teacher Dashboard", "Plan, create, and refine classroom material without leaving the workspace.")
    st.markdown('<div class="dashboard-shell">', unsafe_allow_html=True)
    st.markdown("### Classroom toolkit\nGenerate the core materials for one topic, then save or download what is ready.")
    st.markdown('<article class="glass-card feature-card attendance-card"><div class="card-number">01</div><h3>📋 Quick Attendance</h3><p>Take attendance in seconds. Load a class, tap absent students, and download the sheet.</p></article>', unsafe_allow_html=True)
    teacher_tabs = st.tabs(["📋 Quick Attendance", "🎤 Class Copilot", "📋 Lesson Plan", "📝 Quiz", "💡 Activity", "🖥️ Presentation", "📊 Overview", "⭐ Saved"])
    with teacher_tabs[0]:
        quick_attendance_page()
    with teacher_tabs[1]:
        class_copilot_page()
    with teacher_tabs[2]:
        lesson_page()
    with teacher_tabs[3]:
        quiz_page()
    with teacher_tabs[4]:
        activities_page()
    with teacher_tabs[5]:
        presentation_page()
    with teacher_tabs[6]:
        progress_page()
    with teacher_tabs[7]:
        saved_page()
    st.session_state.embedded_feature = False
    st.markdown('</div>', unsafe_allow_html=True)


def doubt_page():
    page_header("Doubt Solver", "Ask one clear question, choose the depth, and build understanding from the answer.")
    topic = st.text_area("What do you want to understand?", placeholder="Explain Newton's Laws simply.", height=110, key="doubt_input")
    tutor_mode = st.radio("Tutor mode", ["Direct Answer", "Socratic Tutor"], horizontal=True, key="tutor_mode")
    level = st.selectbox("Explanation style", ["Explain like I'm 10", "Beginner", "Standard", "Advanced"], key="doubt_level")
    if st.button("Explain", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Enter a question or topic first.")
        elif tutor_mode == "Socratic Tutor":
            st.session_state.socratic_topic = topic.strip()
            st.session_state.socratic_step = 0
            st.session_state.generated_content["doubt"] = socratic_response(topic.strip(), 0)
        else:
            st.session_state.generated_content["doubt"] = explain_topic(topic.strip(), level)
            st.session_state.chat_messages.append(("You", topic.strip()))
            st.session_state.chat_messages.append(("Zyphron", st.session_state.generated_content["doubt"]))
    if tutor_mode == "Socratic Tutor" and st.session_state.socratic_topic and st.button("Continue Tutor", use_container_width=True, key="continue_socratic"):
        st.session_state.socratic_step = min(st.session_state.socratic_step + 1, 2)
        st.session_state.generated_content["doubt"] = socratic_response(st.session_state.socratic_topic, st.session_state.socratic_step)
    quick_columns = st.columns(4, gap="small")
    for column, label, suffix in zip(quick_columns, ["Explain simpler", "Give example", "Give analogy", "Summarize"], ["Beginner", "Standard", "Explain like I'm 10", "Standard"]):
        with column:
            if st.button(label, use_container_width=True, key=f"quick_{label}") and topic.strip():
                st.session_state.generated_content["doubt"] = explain_topic(topic.strip(), suffix)
    response = st.session_state.generated_content.get("doubt")
    if response:
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        st.markdown(response)
        st.markdown('</div>', unsafe_allow_html=True)
        content_actions("Doubt explanation", response, "doubt")
    elif not topic.strip():
        st.info("Try the Newton's Laws prompt above to follow the 3-minute demo flow.")


def quiz_page():
    page_header("Quiz Studio", "Generate a short practice set, see why answers are right, and retry the weak area.")
    if st.session_state.weak_topics:
        st.markdown(f'<div class="flow-note"><strong>Adaptive recommendation:</strong> Your next targeted practice is {st.session_state.weak_topics[-1]}. We will start with an easier set.</div>', unsafe_allow_html=True)
    setup_columns = st.columns([2, 1, 1, 1], gap="small")
    with setup_columns[0]:
        topic = st.text_input("Topic", placeholder="e.g. Newton's Laws", key="quiz_topic")
    with setup_columns[1]:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Standard", "Advanced"], key="quiz_difficulty")
    with setup_columns[2]:
        count = st.selectbox("Questions", [3, 4, 5], key="quiz_count")
    with setup_columns[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("Generate", type="primary", use_container_width=True)
    if generate:
        if not topic.strip():
            st.warning("Enter a topic before generating the quiz.")
        else:
            selected_topic = topic.strip() or st.session_state.weak_topics[-1] if st.session_state.weak_topics else topic.strip()
            selected_difficulty = "Beginner" if st.session_state.weak_topics else difficulty
            st.session_state.quiz_data = {"topic": selected_topic, "difficulty": selected_difficulty, "questions": build_quiz(selected_topic, selected_difficulty, count)}
            st.session_state.quiz_results = None
            st.rerun()
    quiz = st.session_state.quiz_data
    if not quiz:
        st.info("Your generated quiz will appear here. Keep it short so feedback stays useful.")
        return
    st.markdown(f"### {quiz['topic']} · {quiz['difficulty']}")
    if st.session_state.quiz_results is None:
        for index, item in enumerate(quiz["questions"]):
            st.radio(item["question"], item["options"], key=f"quiz_answer_{index}", index=None)
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            unanswered = [index for index in range(len(quiz["questions"])) if f"quiz_answer_{index}" not in st.session_state]
            if any(st.session_state.get(f"quiz_answer_{index}") is None for index in range(len(quiz["questions"]))):
                st.warning("Answer every question before submitting.")
            else:
                correct = sum(st.session_state[f"quiz_answer_{index}"] == item["options"][item["answer"]] for index, item in enumerate(quiz["questions"]))
                st.session_state.quiz_results = {"correct": correct, "total": len(quiz["questions"]), "answers": [st.session_state[f"quiz_answer_{index}"] for index in range(len(quiz["questions"]))]}
                record_quiz_result(quiz["topic"], correct, len(quiz["questions"]))
                st.rerun()
    else:
        results = st.session_state.quiz_results
        weak = quiz["topic"] if results["correct"] < results["total"] else "None detected"
        st.success(f"Score: {results['correct']} / {results['total']}")
        st.metric("Weak topic", weak)
        if weak != "None detected":
            st.warning(f"Recommended action: Review {weak}, then attempt three easier targeted questions.")
        for index, item in enumerate(quiz["questions"]):
            answer = results["answers"][index]
            expected = item["options"][item["answer"]]
            icon = "✅" if answer == expected else "❌"
            st.markdown(f"**{icon} {index + 1}. {item['question']}**\n\nYour answer: {answer}\n\nExplanation: The best answer is **{expected}** because it connects the concept to observable understanding.")
        result_text = f"{quiz['topic']} quiz\nScore: {results['correct']} / {results['total']}\nWeak topic: {weak}"
        content_actions(f"{quiz['topic']} quiz result", result_text, "quiz-result")
        if st.button("Retry Quiz", use_container_width=True):
            st.session_state.quiz_results = None
            for index in range(len(quiz["questions"])):
                st.session_state.pop(f"quiz_answer_{index}", None)
            st.rerun()


def study_page():
    page_header("Study Mode", "Turn a time limit into a simple session you can actually complete.")
    request = st.text_input("What do you want to learn and how much time do you have?", placeholder="I have 30 minutes to learn Newton's Laws", key="study_request")
    if st.button("Build Study Plan", type="primary", use_container_width=True):
        if not request.strip():
            st.warning("Describe a topic and your available time first.")
        else:
            import re
            minutes_match = re.search(r"(\d+)\s*(?:minutes?|mins?)", request.lower())
            minutes = int(minutes_match.group(1)) if minutes_match else 30
            topic = re.sub(r"i have\s+\d+\s*(?:minutes?|mins?)\s*(?:to learn)?", "", request, flags=re.IGNORECASE).strip(" .") or "your topic"
            first = max(1, minutes // 6)
            second = max(1, minutes // 3)
            third = max(1, minutes // 3)
            final = max(1, minutes - first - second - third)
            st.session_state.study_session = {"topic": topic, "minutes": minutes, "steps": [(f"0–{first} min", "Concept introduction", f"Define {topic} and identify the one idea everything else depends on."), (f"{first}–{first + second} min", "Explanation + examples", f"Study two examples of {topic}, then explain the pattern in your own words."), (f"{first + second}–{first + second + third} min", "Interactive questions", "Take a short quiz and mark every answer you had to guess."), (f"{minutes - final}–{minutes} min", "Revision + weak areas", "Review missed questions and write a one-sentence takeaway.")]}
            st.session_state.study_step = 0
            st.rerun()
    session = st.session_state.study_session
    if not session:
        st.info("Example: I have 30 minutes to learn Newton's Laws.")
        return
    st.markdown(f"### {session['minutes']}-Minute Study Plan · {session['topic']}")
    progress = (st.session_state.study_step + 1) / len(session["steps"])
    st.progress(progress)
    for index, (time, title, detail) in enumerate(session["steps"]):
        marker = "→" if index == st.session_state.study_step else "○"
        st.markdown(f"**{marker} {time} · {title}**  \n{detail}")
    control_columns = st.columns(4, gap="small")
    with control_columns[0]:
        if st.button("Previous", disabled=st.session_state.study_step == 0, use_container_width=True):
            st.session_state.study_step -= 1
            st.rerun()
    with control_columns[1]:
        if st.button("Next", disabled=st.session_state.study_step == len(session["steps"]) - 1, use_container_width=True):
            st.session_state.study_step += 1
            st.rerun()
    with control_columns[2]:
        if st.button("Quiz Me", use_container_width=True):
            st.session_state.quiz_data = {"topic": session["topic"], "difficulty": "Standard", "questions": build_quiz(session["topic"], "Standard", 3)}
            st.session_state.quiz_results = None
            go_to("Quiz")
            st.rerun()
    with control_columns[3]:
        if st.button("Finish Session", use_container_width=True):
            save_content(f"{session['topic']} study plan", "\n".join(f"{time} - {title}: {detail}" for time, title, detail in session["steps"]), "study")
            st.success("Session complete. The plan is saved to your library.")


def summarizer_page():
    page_header("Topic Summarizer", "Turn a topic or study text into a compact revision sheet.")
    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis", key="summary_topic")
    source = st.text_area("Optional study text", placeholder="Paste notes here for a more focused summary.", height=120, key="summary_source")
    if st.button("Create Summary", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            summary = f"### {topic.strip()}\n\n**Short summary**\n{topic.strip()} can be understood by defining its central process, connecting the main parts, and checking the result with an example.\n\n**Key concepts**\n- Main definition and purpose\n- Cause-and-effect relationship\n- One concrete example\n\n**Important points**\n- Start with the core vocabulary.\n- Link each step to what changes next.\n- Test your understanding without looking at the notes.\n\n**Quick revision**\nExplain {topic.strip()} in three sentences, then answer: What is the most important relationship?"
            if source.strip():
                summary += f"\n\n**Notes used**\nYour {len(source.split())}-word study text was used as context."
            st.session_state.generated_content["summary"] = summary
    if st.session_state.generated_content.get("summary"):
        st.markdown(st.session_state.generated_content["summary"])
        content_actions("Topic summary", st.session_state.generated_content["summary"], "summary")


def lesson_page():
    page_header("Lesson Planner", "Build a ready-to-refine classroom plan with objectives, activities, and assessment.")
    columns = st.columns(2, gap="medium")
    with columns[0]:
        subject = st.text_input("Subject", placeholder="Physics", key="lesson_subject")
        topic = st.text_input("Topic", placeholder="Newton's Laws", key="lesson_topic")
        grade = st.selectbox("Class level", ["Primary", "Middle school", "Secondary", "College"], key="lesson_grade")
    with columns[1]:
        duration = st.selectbox("Duration", ["30 minutes", "45 minutes", "60 minutes", "90 minutes"], key="lesson_duration")
        objective = st.text_area("Learning objective", placeholder="Students will explain how force changes motion.", key="lesson_objective", height=100)
    if st.button("Generate Lesson Plan", type="primary", use_container_width=True):
        if not subject.strip() or not topic.strip():
            st.warning("Add a subject and topic before generating.")
        else:
            objective = objective.strip() or f"Students will explain the core ideas of {topic.strip()} using an example."
            plan = f"# {subject.strip()} Lesson Plan\n\n**Topic:** {topic.strip()}\n**Level:** {grade}\n**Duration:** {duration}\n\n## Learning objectives\n- {objective}\n- Connect the concept to an everyday example.\n\n## Flow\n1. **Introduction (5 min):** Open with a question about {topic.strip()}.\n2. **Explanation:** Model the concept with a clear example and invite questions.\n3. **Activity:** Students work in pairs to explain the idea and compare answers.\n4. **Assessment:** Ask three checks for understanding and address the most common misconception.\n5. **Homework:** Write a short explanation and create one original example."
            st.session_state.generated_content["lesson"] = plan
    if st.session_state.generated_content.get("lesson"):
        st.markdown(st.session_state.generated_content["lesson"])
        content_actions("Lesson plan", st.session_state.generated_content["lesson"], "lesson")


def activities_page():
    page_header("Activity Generator", "Create a practical classroom activity or assignment around one topic.")
    topic = st.text_input("Topic", placeholder="The water cycle", key="activity_topic")
    level = st.selectbox("Student level", ["Primary", "Middle school", "Secondary"], key="activity_level")
    duration = st.selectbox("Class duration", ["10 minutes", "20 minutes", "30 minutes", "45 minutes"], key="activity_duration")
    if st.button("Generate Activity", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            activity = f"# {topic.strip()} Classroom Activity\n\n**Level:** {level} · **Time:** {duration}\n\n**Activity:** Think, pair, explain\n\n1. Give each student one prompt about {topic.strip()}.\n2. Students write a prediction, compare it with a partner, and identify one difference.\n3. Pairs explain their reasoning to the class.\n4. Close with a two-question exit check.\n\n**Teacher look-for:** Listen for the key vocabulary and record misconceptions to revisit next lesson."
            st.session_state.generated_content["activity"] = activity
    if st.session_state.generated_content.get("activity"):
        st.markdown(st.session_state.generated_content["activity"])
        content_actions("Classroom activity", st.session_state.generated_content["activity"], "activity")


def progress_page():
    page_header("Learning Progress", "A transparent view of what has actually happened in this session.")
    history = st.session_state.quiz_history
    if not history:
        st.info("No quiz history yet. Complete a quiz and your score, topics, and weak areas will appear here.")
        return
    total_questions = sum(item["total"] for item in history)
    total_correct = sum(item["score"] for item in history)
    metrics = st.columns(3)
    metrics[0].metric("Quizzes completed", len(history))
    metrics[1].metric("Average score", f"{total_correct / total_questions:.0%}")
    metrics[2].metric("Topics studied", len({item['topic'] for item in history}))
    st.markdown("### Recent activity")
    for item in reversed(history):
        status = "Strong" if item["score"] == item["total"] else "Review needed"
        st.markdown(f"**{item['topic']}** · {item['score']}/{item['total']} · {status}")
    st.markdown("### Next focus")
    weak_topics = sorted({item["topic"] for item in history if item["score"] < item["total"]})
    st.write(", ".join(weak_topics) if weak_topics else "No weak topics detected yet.")


def saved_page():
    page_header("Saved Content", "Keep useful explanations, quiz results, study plans, and teaching material nearby.")
    if not st.session_state.saved_content:
        st.info("Nothing saved yet. Use Save on any generated response to build your library.")
        return
    for index, item in enumerate(st.session_state.saved_content):
        with st.expander(f"{item['title']} · {item['category']}"):
            st.markdown(item["content"])
            if st.button("Remove", key=f"remove_saved_{index}"):
                st.session_state.saved_content.pop(index)
                st.rerun()


def about_page():
    page_header("About Zyphron", "One platform for the full loop: learn, practice, identify weakness, and teach.")
    st.markdown('<div class="glass-card"><div class="card-number">Z</div><h3>Student → Learn → Practice → Improve</h3><p>Zyphron helps students turn a question into an explanation, a study plan, and measurable practice. Teachers can turn the same topic into a lesson and an activity.</p></div>', unsafe_allow_html=True)


page_renderers = {
    "Home": home_page,
    "Student": student_page,
    "Teacher": teacher_page,
    "Doubt Solver": doubt_page,
    "Chat": doubt_page,
    "Quiz": quiz_page,
    "Study Mode": study_page,
    "Summarizer": summarizer_page,
    "Lesson Planner": lesson_page,
    "Activities": activities_page,
    "Progress": progress_page,
    "Saved": saved_page,
    "About": about_page,
}
page_renderers.get(st.session_state.page, home_page)()
