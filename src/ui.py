from io import BytesIO

import pymupdf
import requests
import streamlit as st
import streamlit_pdf_viewer as stpdf

if "session_id" not in st.session_state:
    st.session_state.session_id = 0

if "results" not in st.session_state:
    st.session_state.results = None

if "doc" not in st.session_state:
    st.session_state.doc = None

if "tpl" not in st.session_state:
    st.session_state.tpl = None

st.set_page_config(
    page_title="QuickForm",
    layout="wide",
    page_icon="resources/icon.png",
    initial_sidebar_state="expanded",
)
st.title("QuickForm")


def show_icon(level):
    match level:
        case "error":
            st.image("resources/error.png")
        case "warning":
            st.image("resources/warning.png")


def display_result(con, result):
    i = 0
    for entry in result:
        c = con.container(border=True)
        icon_col, error_col = c.columns([0.05, 0.6], vertical_alignment="center")
        with icon_col:
            show_icon(entry["level"])
        with error_col:
            with st.expander(entry["message"]):
                st.write("Bdaksljflkajds;f")
        i += 1


def hightlight_color(defect):
    if defect["level"] == "error":
        return (1, 0, 0)
    return (1, 1, 0)


def highlight_defect(pdf, defect):
    for i in range(0, pdf.page_count):
        page = pdf[i]
        for match in page.search_for(defect["message"]):
            highlight = page.add_rect_annot(match)
            highlight.set_colors(stroke=hightlight_color(defect))
            highlight.set_border(width=1)
            highlight.update()


def highlight_defects():
    doc = st.session_state.doc
    if not doc or not st.session_state.results:
        return

    pdf = pymupdf.open(stream=doc.getvalue(), filetype="pdf")
    for defect in st.session_state.results:
        highlight_defect(pdf, defect)

    buffer = BytesIO()
    pdf.save(buffer)
    pdf.close()
    with open("tmp.pdf", mode="wb") as f:
        f.write(buffer.getbuffer())
    c = st.container(border=True)
    with c:
        stpdf.pdf_viewer("tmp.pdf")


left_col, _, right_col = st.columns([0.35, 0.05, 0.6])

with left_col:
    st.header("Upload your documents here")
    document = st.file_uploader("Document", key="document", type=["pdf"])
    template = st.file_uploader("Template", key="template", type=["pdf"])

    st.session_state.doc = document
    st.session_state.tpl = template

    if st.button("Submit"):
        if document and template:
            files = [
                ("files", (file.name, file.getvalue(), file.type)) for file in [document, template]
            ]

            session_id = st.session_state.session_id
            st.session_state.session_id += 1

            st.session_state.results = [
                {"level": "error", "message": "Hackathon"},
                {"level": "warning", "message": '(hereinafter referred to as the "Competition")'},
            ]
            data = {
                "session_id": session_id,
                "message": "Hello, I need help with this document",
            }
            r = requests.post("http://localhost:8000/structure", data=data, files=files)

with right_col:
    st.header("Result")
    defects_tab, overview_tab, preview_tab, chat_tab = st.tabs(
        ["Defects", "Overview", "Preview", "Chat"]
    )
    with defects_tab:
        results = st.session_state.results
        if results:
            display_result(defects_tab, results)
        else:
            right_col.write("Nothing to see...")
    with overview_tab:
        st.write("")
    with preview_tab:
        highlight_defects()
    with chat_tab:
        prompt = st.chat_input("Ask something about document")
        if prompt:
            session_id = st.session_state.session_id
            data = {"session_id": session_id, "message": prompt}
            r = requests.post("http://localhost:8000/chat", data=data)
            if r.ok:
                message = r.json()["completion"]
                with st.chat_message("assistant"):
                    st.write(message)
