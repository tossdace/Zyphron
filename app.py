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


def go_to(page):
    st.session_state.previous_page = st.session_state.page
    st.session_state.page = page


def go_back():
    st.session_state.page = st.session_state.previous_page


def select_mode(mode):
    st.session_state.mode = mode
    go_to("Teacher" if mode == "Teacher" else "Student")


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
        padding: 1.7rem 2.2rem 2rem;
    }

    .brand-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 4.5rem;
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
        min-height: 3rem;
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
        margin: -2.2rem 0 3.2rem;
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
        .block-container { padding: 1.15rem 1rem 1.5rem; }
        .brand-bar { margin-bottom: 3.5rem; }
        .language-pill { font-size: 0.68rem; }
        .hero { margin-bottom: 4.4rem; }
        .hero h1 { font-size: clamp(3.7rem, 19vw, 5.8rem); }
        .hero p { font-size: 0.92rem; }
        .section-block { margin-bottom: 4.4rem; }
        .glass-card { min-height: 0; }
        .nav-shell { margin-top: -1.9rem; margin-bottom: 2.5rem; }
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
    ("💬 Chat", "Chat"),
    ("📝 Quiz", "Quiz"),
    ("📚 Lessons", "Lesson Planner"),
    ("ℹ️ About", "About"),
]
st.markdown('<div class="nav-shell"><div class="nav-caption">Explore Zyphron</div>', unsafe_allow_html=True)
nav_columns = st.columns(len(navigation), gap="small")
for column, (label, page) in zip(nav_columns, navigation):
    with column:
        st.button(label, key=f"nav_{page}", use_container_width=True, on_click=go_to, args=(page,))
st.markdown("</div>", unsafe_allow_html=True)


def page_header(title, description):
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


def add_chat_response(prompt):
    st.session_state.chat_messages.append(("You", prompt))
    st.session_state.chat_messages.append(("Zyphron", f"Here is a clear starting point for: {prompt}. I can explain it step by step, add an example, or turn it into a short quiz."))


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
        st.button("Ask a Doubt", use_container_width=True, on_click=go_to, args=("Chat",))
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
    page_header("Student Space", "Choose a focused next step for learning, practice, and progress.")
    cards = [
        ("01", "💬 Ask a Doubt", "Get a clear, step-by-step explanation.", "Open Chat", "Chat"),
        ("02", "📝 Take a Quiz", "Practice concepts with quick questions.", "Take Quiz", "Quiz"),
        ("03", "📖 Learn a Topic", "Build a focused learning path.", "Open Lessons", "Lesson Planner"),
        ("04", "📊 View Progress", "Review your learning journey.", "View Progress", "About"),
    ]
    columns = st.columns(4, gap="medium")
    for column, card in zip(columns, cards):
        with column:
            feature_card(*card)


def teacher_page():
    page_header("Teacher Studio", "Turn a classroom idea into useful material in a few focused clicks.")
    cards = [
        ("01", "⚡ Generate Lesson Plan", "Shape a topic into a ready-to-use lesson.", "Plan a Lesson", "Lesson Planner"),
        ("02", "📝 Create Quiz", "Build a short quiz for your class.", "Create Quiz", "Quiz"),
        ("03", "💡 Explain a Topic", "Prepare a student-friendly explanation.", "Explain Topic", "Chat"),
        ("04", "📚 Teaching Resources", "Find a focused starting point for class.", "Open Resources", "About"),
    ]
    columns = st.columns(4, gap="medium")
    for column, card in zip(columns, cards):
        with column:
            feature_card(*card)


def chat_page():
    page_header("Chat / Doubt Solver", "Ask a question and keep the conversation moving without losing context.")
    mode = st.session_state.mode or "Student"
    st.markdown(f'<div class="mode-note">Current mode: <strong>{mode}</strong> · English</div>', unsafe_allow_html=True)
    if not st.session_state.chat_messages:
        st.markdown('<div class="chat-box"><span class="chat-label">Zyphron</span>Welcome. Ask a question, paste a topic, or choose a quick prompt below.</div>', unsafe_allow_html=True)
    for sender, message in st.session_state.chat_messages:
        st.markdown(f'<div class="chat-box"><span class="chat-label">{sender}</span>{message}</div>', unsafe_allow_html=True)
    prompt_columns = st.columns(4, gap="small")
    for column, prompt in zip(prompt_columns, ["Explain this simply", "Give an example", "Quiz me", "Summarize this"]):
        with column:
            st.button(prompt, key=f"prompt_{prompt}", use_container_width=True, on_click=add_chat_response, args=(prompt,))
    user_prompt = st.chat_input("Ask a doubt or enter a topic...")
    if user_prompt:
        add_chat_response(user_prompt)
        st.rerun()


def quiz_page():
    page_header("Quiz Studio", "Create a quick practice set for a topic, then keep learning from the results.")
    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis")
    level = st.selectbox("Level", ["Foundations", "Practice", "Challenge"])
    if st.button("Generate Quiz", use_container_width=True):
        selected_topic = topic.strip() or "your selected topic"
        st.markdown(f'<div class="flow-note"><strong>{level} quiz: {selected_topic}</strong><br><br>1. What is the central idea of {selected_topic}?<br>2. Give one real-world example.<br>3. Explain it in your own words.<br><br>Use Chat to explore any answer.</div>', unsafe_allow_html=True)


def lesson_page():
    page_header("Lesson Planner", "Build a clean lesson outline that is ready to refine for your classroom.")
    topic = st.text_input("Lesson topic", placeholder="e.g. The water cycle")
    grade = st.selectbox("Class level", ["Primary", "Middle school", "Secondary"])
    duration = st.selectbox("Duration", ["30 minutes", "45 minutes", "60 minutes"])
    if st.button("Generate Lesson Plan", use_container_width=True):
        selected_topic = topic.strip() or "your selected topic"
        st.markdown(f'<div class="flow-note"><strong>{selected_topic} · {grade} · {duration}</strong><br><br>1. Warm-up question<br>2. Core explanation with one example<br>3. Guided activity<br>4. Quick understanding check<br>5. Takeaway and follow-up question</div>', unsafe_allow_html=True)


def about_page():
    page_header("About Zyphron", "A focused education companion designed around the moments that matter most.")
    st.markdown('<div class="glass-card"><div class="card-number">Z</div><h3>Clear support for real education work</h3><p>Zyphron helps teachers prepare lessons and quizzes, helps students work through doubts, and keeps every interaction simple, focused, and easy to demonstrate.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="flow-note">Built for the future of education · Conclave 2026</div>', unsafe_allow_html=True)


page_renderers = {
    "Home": home_page,
    "Student": student_page,
    "Teacher": teacher_page,
    "Chat": chat_page,
    "Quiz": quiz_page,
    "Lesson Planner": lesson_page,
    "About": about_page,
}
page_renderers[st.session_state.page]()
