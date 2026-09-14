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


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #f8f5ff;
        --muted: #c9bfe1;
        --lavender: #d9c7ff;
        --violet: #9c6dff;
        --purple: #7139d7;
        --deep: #120a2b;
        --glass: rgba(255, 255, 255, 0.09);
        --line: rgba(232, 220, 255, 0.18);
    }

    .stApp {
        min-height: 100vh;
        color: var(--ink);
        background:
            radial-gradient(circle at 14% 14%, rgba(155, 93, 255, 0.34), transparent 27%),
            radial-gradient(circle at 86% 8%, rgba(112, 214, 255, 0.16), transparent 24%),
            radial-gradient(circle at 72% 76%, rgba(126, 56, 227, 0.23), transparent 30%),
            linear-gradient(135deg, #0e0822 0%, #1c0e3e 47%, #0b0920 100%);
        font-family: 'DM Sans', sans-serif;
    }

    .stApp:before,
    .stApp:after {
        content: '';
        position: fixed;
        pointer-events: none;
        z-index: 0;
    }

    .stApp:before {
        width: 420px;
        height: 420px;
        top: -170px;
        left: 12%;
        border: 1px solid rgba(224, 208, 255, 0.16);
        transform: rotate(34deg) skewX(-15deg);
        box-shadow: 0 0 70px rgba(166, 117, 255, 0.12), inset 0 0 70px rgba(208, 193, 255, 0.06);
    }

    .stApp:after {
        width: 260px;
        height: 260px;
        right: 9%;
        bottom: 8%;
        border: 1px solid rgba(162, 220, 255, 0.12);
        transform: rotate(45deg);
        box-shadow: 0 0 55px rgba(107, 181, 255, 0.1);
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

    .brand-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    .brand-mark {
        display: grid;
        width: 2.25rem;
        height: 2.25rem;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, 0.38);
        border-radius: 0.75rem;
        color: #201044;
        background: linear-gradient(135deg, #f2eaff 0%, #b98bff 48%, #7b56e5 100%);
        box-shadow: 0 0 24px rgba(179, 129, 255, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.8);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
    }

    .language-pill {
        padding: 0.55rem 0.95rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--muted);
        background: rgba(255, 255, 255, 0.06);
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        backdrop-filter: blur(16px);
    }

    .hero {
        position: relative;
        max-width: 830px;
        margin: 0 auto 6.2rem;
        text-align: center;
        animation: rise 0.8s ease-out both;
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
        background: linear-gradient(90deg, transparent, var(--lavender));
    }

    .hero h1 {
        margin: 0;
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(3.7rem, 9vw, 7.8rem);
        font-weight: 700;
        letter-spacing: -0.06em;
        line-height: 0.96;
        text-shadow: 0 0 48px rgba(192, 155, 255, 0.35);
    }

    .hero h1 span {
        color: transparent;
        background: linear-gradient(100deg, #f9f4ff 12%, #c9a7ff 52%, #8fddff 100%);
        -webkit-background-clip: text;
        background-clip: text;
    }

    .hero h2 {
        margin: 1.5rem 0 1rem;
        color: #e5d9fa;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.15rem, 2.5vw, 1.65rem);
        font-weight: 500;
    }

    .hero p {
        max-width: 625px;
        margin: 0 auto;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.75;
    }

    .hero:after {
        content: '';
        position: absolute;
        width: 180px;
        height: 180px;
        top: 15%;
        left: 50%;
        z-index: -1;
        border: 1px solid rgba(231, 219, 255, 0.08);
        transform: translateX(-50%) rotate(45deg);
        box-shadow: 0 0 45px rgba(173, 125, 255, 0.18);
    }

    .stButton > button {
        width: 100%;
        min-height: 2.8rem;
        padding: 0.65rem 1rem;
        border: 1px solid rgba(233, 220, 255, 0.24);
        border-radius: 0.8rem;
        color: #fff;
        background: rgba(255, 255, 255, 0.08);
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
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
        border-color: rgba(231, 214, 255, 0.68);
        background: rgba(183, 134, 255, 0.2);
        box-shadow: 0 0 28px rgba(153, 99, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.24);
        transform: translateY(-2px);
    }

    .cta-row {
        max-width: 520px;
        margin: 2.1rem auto 0;
    }

    .section-heading {
        margin: 0 0 1.8rem;
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.7rem, 3vw, 2.35rem);
        letter-spacing: -0.04em;
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
        border-radius: 1.1rem;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.045));
        box-shadow: 0 18px 45px rgba(3, 0, 16, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.14);
        backdrop-filter: blur(18px);
        transition: transform 220ms ease, border-color 220ms ease, background 220ms ease;
    }

    .glass-card:hover {
        border-color: rgba(223, 204, 255, 0.42);
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.065));
        transform: translateY(-6px);
    }

    .glass-card:after {
        content: '';
        position: absolute;
        width: 90px;
        height: 90px;
        top: -42px;
        right: -34px;
        border: 1px solid rgba(233, 224, 255, 0.15);
        transform: rotate(45deg);
    }

    .card-number {
        display: inline-grid;
        width: 2rem;
        height: 2rem;
        margin-bottom: 1.1rem;
        place-items: center;
        border: 1px solid rgba(218, 199, 255, 0.3);
        border-radius: 0.65rem;
        color: var(--lavender);
        background: rgba(157, 108, 255, 0.16);
        font-size: 0.78rem;
        font-weight: 700;
    }

    .glass-card h3 {
        margin: 0 0 0.55rem;
        color: #f5efff;
        font-family: 'Space Grotesk', sans-serif;
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
        animation: rise 0.8s 0.18s ease-out both;
    }

    .solution-block {
        padding: 2.7rem 0 0;
        border-top: 1px solid rgba(219, 198, 255, 0.12);
        animation-delay: 0.3s;
    }

    .mode-note {
        margin: 1.2rem 0 0;
        padding: 0.85rem 1rem;
        border: 1px solid rgba(208, 190, 255, 0.2);
        border-radius: 0.75rem;
        color: var(--lavender);
        background: rgba(127, 75, 219, 0.12);
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
        margin: -1rem 0 2.5rem;
        padding: 0.55rem;
        border: 1px solid var(--line);
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.06);
        box-shadow: 0 14px 35px rgba(3, 0, 16, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(18px);
    }

    .nav-caption {
        padding: 0.25rem 0.7rem 0.35rem;
        color: #a99cc4;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .page-title {
        margin: 0 0 0.5rem;
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        letter-spacing: -0.05em;
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
        border-radius: 1.1rem;
        background: rgba(255, 255, 255, 0.045);
        box-shadow: 0 14px 35px rgba(3, 0, 16, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
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
        font-family: 'Space Grotesk', sans-serif;
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
        border-radius: 0.9rem;
        background: rgba(255, 255, 255, 0.07);
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

    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem 1.5rem; }
        .brand-bar { margin-bottom: 2rem; }
        .language-pill { font-size: 0.68rem; }
        .hero { margin-bottom: 4.4rem; }
        .hero h1 { font-size: clamp(3.2rem, 17vw, 5.2rem); }
        .hero p { font-size: 0.92rem; }
        .section-block { margin-bottom: 4.4rem; }
        .glass-card { min-height: 0; }
        .nav-shell { margin-top: -0.8rem; margin-bottom: 1.8rem; padding: 0.35rem; }
        .nav-caption { padding-left: 0.4rem; }
        .nav-shell .stButton > button { min-height: 2.6rem; padding: 0.5rem 0.35rem; font-size: 0.78rem; }
        .dashboard-shell { padding: 0.85rem; }
        .dashboard-shell [data-baseweb="tab"] { flex: 1 1 45%; text-align: center; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brand-bar">
        <div class="brand"><span class="brand-mark">Z</span> Zyphron</div>
        <div class="language-pill">English only</div>
    </div>
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
    student_tabs = st.tabs(["💬 Doubt", "🧠 Study", "📝 Quiz", "📚 Summary", "📊 Progress", "⭐ Saved"])
    with student_tabs[0]:
        doubt_page()
    with student_tabs[1]:
        study_page()
    with student_tabs[2]:
        quiz_page()
    with student_tabs[3]:
        summarizer_page()
    with student_tabs[4]:
        progress_page()
    with student_tabs[5]:
        saved_page()
    st.session_state.embedded_feature = False
    st.markdown('</div>', unsafe_allow_html=True)


def teacher_page():
    st.session_state.embedded_feature = True
    page_header("Teacher Dashboard", "Plan, create, and refine classroom material without leaving the workspace.")
    st.markdown('<div class="dashboard-shell">', unsafe_allow_html=True)
    st.markdown("### Classroom toolkit\nGenerate the core materials for one topic, then save or download what is ready.")
    teacher_tabs = st.tabs(["📋 Lesson Plan", "📝 Quiz", "💡 Activity", "📊 Overview", "⭐ Saved"])
    with teacher_tabs[0]:
        lesson_page()
    with teacher_tabs[1]:
        quiz_page()
    with teacher_tabs[2]:
        activities_page()
    with teacher_tabs[3]:
        progress_page()
    with teacher_tabs[4]:
        saved_page()
    st.session_state.embedded_feature = False
    st.markdown('</div>', unsafe_allow_html=True)


def doubt_page():
    page_header("Doubt Solver", "Ask one clear question, choose the depth, and build understanding from the answer.")
    topic = st.text_area("What do you want to understand?", placeholder="Explain Newton's Laws simply.", height=110, key="doubt_input")
    level = st.selectbox("Explanation style", ["Explain like I'm 10", "Beginner", "Standard", "Advanced"], key="doubt_level")
    if st.button("Explain", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Enter a question or topic first.")
        else:
            st.session_state.generated_content["doubt"] = explain_topic(topic.strip(), level)
            st.session_state.chat_messages.append(("You", topic.strip()))
            st.session_state.chat_messages.append(("Zyphron", st.session_state.generated_content["doubt"]))
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
            st.session_state.quiz_data = {"topic": topic.strip(), "difficulty": difficulty, "questions": build_quiz(topic.strip(), difficulty, count)}
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
