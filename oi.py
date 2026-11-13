import streamlit as st
import streamlit.components.v1 as components
from google import genai
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="✍📍 مولد الفيديوهات بالذكاء الاصطناعي (المطور عباس)",
    page_icon="🎞️",
    layout="wide"
)

# إنشاء مجلد لحفظ الفيديوهات المتولدة
os.makedirs("videos", exist_ok=True)

# تنسيق CSS احترافي وجذاب مع الحفاظ على نفس الألوان
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
}

.stApp {
    background: radial-gradient(circle at top right, #1e132b 0%, #121212 45%, #0a0a0a 100%);
}

/* الهيدر الرئيسي */
.hero-box {
    background: linear-gradient(135deg, #1A1A1A 0%, #241734 100%);
    border: 1px solid rgba(157, 78, 221, 0.35);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    margin-bottom: 25px;
}

.hero-title {
    color: #ffffff;
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 8px;
    text-shadow: 0 0 15px rgba(157, 78, 221, 0.6);
}

.hero-sub {
    color: #e0e0e0;
    font-size: 16px;
    margin: 0 0 10px 0;
}

.dev-note {
    display: inline-block;
    background: rgba(157, 78, 221, 0.12);
    border: 1px dashed rgba(157, 78, 221, 0.5);
    color: #c792ea;
    font-size: 13px;
    padding: 6px 16px;
    border-radius: 20px;
    margin-top: 5px;
}

/* البطاقات */
.glass-card {
    background-color: #1A1A1A;
    border: 1px solid #2c2c2c;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
    margin-bottom: 20px;
}

/* مربع النص */
.stTextArea textarea {
    background-color: #121212 !important;
    color: #00FF7F !important;
    font-weight: bold !important;
    font-size: 16px !important;
    text-align: right;
    direction: rtl;
    border: 1px solid #9D4EDD !important;
    border-radius: 12px !important;
    padding: 15px !important;
}
.stTextArea textarea:focus {
    box-shadow: 0 0 15px rgba(157, 78, 221, 0.5) !important;
}

/* الأزرار */
div.stButton > button {
    background: linear-gradient(90deg, #1A1A1A, #251933) !important;
    color: #9D4EDD !important;
    border: 1px solid #9D4EDD !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    width: 100%;
    padding: 12px 20px;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    background: #9D4EDD !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(157, 78, 221, 0.7);
    transform: translateY(-2px);
}

/* زر التشغيل الأخضر */
.play-btn div.stButton > button {
    color: #00FF7F !important;
    border: 1px solid #00FF7F !important;
    background: linear-gradient(90deg, #1A1A1A, #132a1e) !important;
}
.play-btn div.stButton > button:hover {
    background: #00FF7F !important;
    color: #121212 !important;
    box-shadow: 0 0 20px rgba(0, 255, 127, 0.6);
}

/* صندوق العرض */
.video-frame {
    border: 2px solid #9D4EDD;
    border-radius: 16px;
    padding: 10px;
    background-color: #0e0e0e;
    box-shadow: 0 0 25px rgba(157, 78, 221, 0.25);
    text-align: center;
}

/* شريط الحالة */
.status-generating {
    background: rgba(157, 78, 221, 0.15);
    border: 1px solid #9D4EDD;
    color: #d8a6ff;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    font-size: 17px;
    margin-top: 10px;
}

.status-done {
    background: rgba(0, 255, 127, 0.15);
    border: 1px solid #00FF7F;
    color: #00FF7F;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    font-size: 17px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

add = """
Rules:
- Output ONE complete HTML file: <canvas id="c" width="800" height="500"> and a <script>.
- Write function drawFrame(t, ctx) that draws the full scene at time t (0..DURATION). It depends only on t.
- Use only ctx.fillRect, arc, beginPath/lineTo, fillText, and similar basic drawing.
- Animate with requestAnimationFrame, and loop t from 0 to DURATION.
- Add a "ابدأ" button. On click, start the animation and the audio (browsers block autoplay without a click).
- Dialogue: use speechSynthesis with SpeechSynthesisUtterance, lang='ar-SA', and a different pitch/rate per character (male/female). Trigger each line at its time.
- Output ONLY raw HTML. No explanation, no markdown.
Story:"""


# الدالتان الخاصتان بالحالة
def جاري_التوليد(مكان_الحالة, نص_المرحلة=""):
    مكان_الحالة.markdown(
        f"<div class='status-generating'>⏳ جاري التوليد... {نص_المرحلة}</div>",
        unsafe_allow_html=True
    )


def تم_التوليد(مكان_الحالة):
    مكان_الحالة.markdown(
        "<div class='status-done'>✅ تم التوليد بنجاح! الفيديو جاهز الآن في المشغل وقسم الفيديوهات المتولدة</div>",
        unsafe_allow_html=True
    )


# دوال الذكاء الاصطناعي
API_KEY=st.secrets["GEMINI_API_KEY"]


def call_gemini(prompt_content):
    gen = genai.Client(api_key=API_KEY)
    for attempt in range(2):
        try:
            return gen.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt_content
            )
        except Exception as e:
            if attempt == 1:
                raise e
            time.sleep(2)


def add_ai_Thedirector(text):
    c = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your task is to write the dialogues and long scripts when the user specifies the type of story or video."
    return call_gemini(add + c + text.strip())


def add_ai_Drawingcharacters(r1):
    c1 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to draw the characters with incredible, imaginative precision using the scenarios or previews generated by the previous version."
    return call_gemini(add + c1 + r1)


def add_ai_Improvecharacters(r2):
    c3 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to improve and coordinate the colors of the characters generated by the previous version by adding or removing any errors or inconsistent colors with extreme precision."
    return call_gemini(add + c3 + r2)


def add_ai_Movement(r3):
    c4 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to animate the characters generated by the previous clones, following the script they created with utmost precision."
    return call_gemini(add + c4 + r3)


def add_ai_Improve_movement(r4):
    c4 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to improve the animation of the characters generated by the previous version, correcting any errors and ensuring the animation is fantastic."
    return call_gemini(add + c4 + r4)


def add_ai_Movethecamera(r5):
    c5 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to move the camera during the characters' dialogues, as if it were a movie, and I will rely on you for that."
    return call_gemini(add + c5 + r5)


def add_ai_Accuracyandlighting(r6):
    c7 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to add high precision and consistent lighting."
    return call_gemini(add + c7 + r6)


def add_ai_Backgrounds(r7):
    c8 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to improve and coordinate the background colors generated by the previous version, ensuring they are of high quality, beautiful, and easy on the eyes."
    return call_gemini(add + c8 + r7)


def add_ai_Improvebackgrounds(r8):
    c9 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to improve or correct the sound if there are any errors."
    return call_gemini(add + c9 + r8)


def add_ai_Addingaccuratesounds(r9):
    c10 = "We divided the tasks across each version of the AI to ensure the video is accurate, and your task is: Your job is to add dialogue audio to the HTML code from the previous version. Use ONLY the browser's speechSynthesis API with SpeechSynthesisUtterance and lang='ar-SA'. Give each character a different pitch and rate based on gender. Trigger each line at its exact time in the animation. Do NOT use gTTS or any Python library. Audio must start only after the user clicks the start button. Output the full updated HTML only."
    return call_gemini(add + c10 + r9)


def add_ai_Codechecker(r12):
    c13 = "We divided the tasks across each version of the AI ​​to ensure the video is accurate, and your task is:Your job is to review and proofread the code."
    return call_gemini(add + c13 + r12)


def Codecleaning(rd_m, story_title):
    cm = (rd_m.text.replace("```html", "").replace("```HTML", "")
          .replace("```python", "").replace("```Python", "")
          .replace("```", "").replace("`", "").strip())

    with open("a.html", "w", encoding="utf-8") as file:
        file.write(cm)

    safe_name = "".join(c for c in story_title[:25] if c.isalnum() or c in (" ", "_")).strip()
    if not safe_name:
        safe_name = "فيديو"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_path = os.path.join("videos", f"{safe_name}_{timestamp}.html")
    with open(saved_path, "w", encoding="utf-8") as file:
        file.write(cm)
    return saved_path


def stafe3(مكان_الحالة, user_text):
    شريط_التقدم = st.progress(0)

    جاري_التوليد(مكان_الحالة, "(1/12) كتابة السيناريو والحوار...")
    r1 = add_ai_Thedirector(user_text)
    شريط_التقدم.progress(8)

    جاري_التوليد(مكان_الحالة, "(2/12) رسم الشخصيات...")
    r2 = add_ai_Drawingcharacters(r1.text)
    شريط_التقدم.progress(16)

    جاري_التوليد(مكان_الحالة, "(3/12) تحسين وتنسيق...")
    r3 = add_ai_Improvebackgrounds(r2.text)
    شريط_التقدم.progress(25)

    جاري_التوليد(مكان_الحالة, "(4/12) إضافة الدقة والإضاءة...")
    r4 = add_ai_Accuracyandlighting(r3.text)
    شريط_التقدم.progress(33)

    جاري_التوليد(مكان_الحالة, "(5/12) تصميم الخلفيات...")
    r5 = add_ai_Backgrounds(r4.text)
    شريط_التقدم.progress(42)

    جاري_التوليد(مكان_الحالة, "(6/12) تحسين الخلفيات...")
    r6 = add_ai_Improvebackgrounds(r5.text)
    شريط_التقدم.progress(50)

    جاري_التوليد(مكان_الحالة, "(7/12) دمج الأصوات العربية...")
    r7 = add_ai_Addingaccuratesounds(r6.text)
    شريط_التقدم.progress(60)

    جاري_التوليد(مكان_الحالة, "(8/12) تحريك الشخصيات...")
    r9 = add_ai_Movement(r7.text)
    شريط_التقدم.progress(70)

    جاري_التوليد(مكان_الحالة, "(9/12) تحسين نعومة الحركة...")
    r10 = add_ai_Improve_movement(r9.text)
    شريط_التقدم.progress(80)

    جاري_التوليد(مكان_الحالة, "(10/12) ضبط حركة الكاميرا...")
    r11 = add_ai_Movethecamera(r10.text)
    شريط_التقدم.progress(88)

    جاري_التوليد(مكان_الحالة, "(11/12) تحسين ألوان الشخصيات...")
    r13 = add_ai_Improvecharacters(r11.text)
    جاري_التوليد(مكان_الحالة, "(12/12) التدقيق النهائي للكود...")
    r13 = add_ai_Codechecker(r13.text)
    شريط_التقدم.progress(100)

    saved_file = Codecleaning(r13, user_text)
    st.session_state["active_video"] = saved_file
    تم_التوليد(مكان_الحالة)


# ==================== واجهة المستخدم ====================

st.markdown("""
<div class="hero-box">
    <div class="hero-title">🎞️ مولد الفيديوهات بالذكاء الاصطناعي</div>
    <p class="hero-sub">✍📍 اصنع فيديوهاتك الكرتونية والقصصية الناطقة بسهولة ومجاناً — تطوير: <b style="color:#00FF7F;"> المطور عباس عبدالرحمن</b></p>
    <div class="dev-note">⚠️ ملاحظة صغيرة: قد يصيب البرنامج خطأ أحياناً بسبب أن شخصاً واحداً فقط يقوم بتطويره، شكراً لتفهمكم ودعمكم 💜</div>
</div>
""", unsafe_allow_html=True)

# تقسيم الشاشة إلى عمودين: يمين للكتابة والتحكم، يسار للمشغل
col_controls, col_player = st.columns([1, 1.35], gap="large")

with col_controls:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#9D4EDD; margin-bottom:10px;'>📝 اكتب فكرة القصة أو السيناريو</h4>",
                unsafe_allow_html=True)

    user_text = st.text_area(
        label="نص القصة",
        label_visibility="collapsed",
        placeholder="مثال: قصة قصيرة بين طفل وروبوت ذكي في المستقبل يتحدثان عن الفضاء...",
        height=200
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        generate_clicked = st.button("🚀 اضغط للتوليد")
    with btn_col2:
        st.markdown("<div class='play-btn'>", unsafe_allow_html=True)
        play_clicked = st.button("🎬 اضغط للتشغيل")
        st.markdown("</div>", unsafe_allow_html=True)

    مكان_الحالة = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

if generate_clicked:
    if user_text.strip():
        stafe3(مكان_الحالة, user_text)
    else:
        مكان_الحالة.markdown("<div class='status-generating'>⚠️ يرجى كتابة نص القصة أولاً!</div>",
                             unsafe_allow_html=True)

if play_clicked:
    if os.path.exists("a.html"):
        st.session_state["active_video"] = "a.html"

with col_player:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#00FF7F; margin-bottom:10px;'>📺 شاشة عرض الفيديو</h4>", unsafe_allow_html=True)

    video_to_play = st.session_state.get("active_video", "a.html" if os.path.exists("a.html") else None)

    if video_to_play and os.path.exists(video_to_play):
        st.markdown(
            f"<p style='color:#00FF7F; font-size:14px;'>🎉 جارٍ عرض: <b>{os.path.basename(video_to_play)}</b> (اضغط على زر <b>ابدأ</b> داخل الفيديو لتشغيل الصوت والحركة)</p>",
            unsafe_allow_html=True)
        with open(video_to_play, "r", encoding="utf-8") as f:
            html_code = f.read()
        st.markdown("<div class='video-frame'>", unsafe_allow_html=True)
        components.html(html_code, width=810, height=540)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='height:420px; border: 2px dashed #333; border-radius:16px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#777;'>
            <div style='font-size:50px;'>🎬</div>
            <p style='font-size:16px;'>لا يوجد فيديو معروض حالياً — اكتب قصتك واضغط على <b>اضغط للتوليد</b></p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== قسم الفيديوهات المتولدة ====================
st.markdown("---")
st.markdown("<h3 style='color:#9D4EDD;'>📂 مكتبة الفيديوهات المتولدة</h3>", unsafe_allow_html=True)

video_files = sorted(
    [f for f in os.listdir("videos") if f.endswith(".html")],
    key=lambda x: os.path.getmtime(os.path.join("videos", x)),
    reverse=True
)

if not video_files:
    st.info("لم يتم توليد أي فيديوهات محفوظة بعد. سيظهر كل فيديو تقوم بتوليده هنا تلقائياً!")
else:
    cols = st.columns(3)
    for idx, vid_file in enumerate(video_files):
        vid_path = os.path.join("videos", vid_file)
        created_time = datetime.fromtimestamp(os.path.getmtime(vid_path)).strftime("%Y-%m-%d | %I:%M %p")
        clean_title = vid_file.rsplit("_", 2)[0]

        with cols[idx % 3]:
            st.markdown(f"""
            <div class='glass-card' style='border-color: rgba(157, 78, 221, 0.4);'>
                <div style='font-size:28px; text-align:center;'>🎞️</div>
                <h5 style='color:white; text-align:center; margin:8px 0;'>{clean_title}</h5>
                <p style='color:#999; font-size:12px; text-align:center;'>🕒 {created_time}</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶️ تشغيل", key=f"play_{vid_file}"):
                    st.session_state["active_video"] = vid_path
                    st.rerun()
            with c2:
                with open(vid_path, "rb") as file_data:
                    st.download_button(
                        label="⬇️ تحميل",
                        data=file_data,
                        file_name=vid_file,
                        mime="text/html",
                        key=f"dl_{vid_file}"
                    )

# تذييل الصفحة باسم المطور والملاحظة
st.markdown("""
<div style='text-align:center; margin-top:40px; padding:15px; border-top:1px solid #262626; color:#888; font-size:13px;'>
    تطوير وبرمجة: <b style='color:#00FF7F;'>المطور عباس</b> | ⚠️ ملاحظة: قد يصيب البرنامج خطأ بسبب أن شخصاً واحداً يطوره.
</div>
""", unsafe_allow_html=True)
