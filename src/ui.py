from datetime import datetime, timedelta
from io import BytesIO

import pymupdf
import requests
import streamlit as st
import streamlit_pdf_viewer as stpdf

if "session_id" not in st.session_state:
    st.session_state.session_id = 0

if "results" not in st.session_state:
    st.session_state.results = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "doc" not in st.session_state:
    st.session_state.doc = None

if "tpl" not in st.session_state:
    st.session_state.tpl = None

if "quality" not in st.session_state:
    st.session_state.quality = None

st.set_page_config(
    page_title="QuickForm",
    layout="wide",
    page_icon="resources/icon.png",
    initial_sidebar_state="expanded",
)
st.title("QuickForm")


def show_icon(level):
    match level:
        case "incorrect":
            st.image("resources/error.png")
        case "missing":
            st.image("resources/error.png")
        case "improvable":
            st.image("resources/warning.png")


def display_result(con, result):
    if not st.session_state.quality:
        return
    with con.container(border=True):
        col_a, colb_ = st.columns([0.9, 0.1], vertical_alignment="center")
        with col_a:
            st.write("Rating")
        with colb_:
            st.write(f"{str(st.session_state.quality)}%")

    for entry in result:
        c = con.container(border=True)
        icon_col, error_col = c.columns([0.05, 0.6], vertical_alignment="center")
        with icon_col:
            show_icon(entry["type"])
        with error_col:
            if entry["type"] == "missing":
                st.write(entry["message"])
            else:
                with st.expander(entry["message"]):
                    st.write(entry["suggestion"])


def hightlight_color(defect):
    if defect["type"] == "incorrect" or defect["type"] == "missing":
        return (1, 0, 0)
    return (1, 1, 0)


def highlight_defect(pdf, defect):
    if defect["type"] == "missing":
        return

    for i in range(0, pdf.page_count):
        page = pdf[i]
        for match in page.search_for(defect["occurrence"]):
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


def display_chat(prompt_, message_):
    session_id_ = st.session_state.session_id
    chat_history = st.session_state.chat_history
    if not session_id_ in chat_history:
        chat_history[session_id_] = [(prompt_, message_)]
    else:
        chat_history[session_id_].insert(0, (prompt_, message_))
    st.session_state.chat_history = chat_history

    for exchange in chat_history[session_id_]:
        with st.chat_message("human"):
            st.write(exchange[0])
        with st.chat_message("assistant"):
            st.write(exchange[1])


def show_summary():
    doc = st.session_state.doc
    if not doc:
        return

    pdf = pymupdf.open(stream=doc.getvalue(), filetype="pdf")
    title = pdf.metadata["title"]
    pages = pdf.page_count
    author = pdf.metadata["author"]
    creation_date = pdf.metadata["creationDate"]
    creation_date = (
        datetime.strptime(creation_date[2:16], "%Y%m%d%H%M%S")
        - timedelta(hours=int(creation_date[16:19]), minutes=int(creation_date[20:22]))
    ).strftime("%d.%m.%Y %H:%M:%S")
    pdf.close()
    for entry in [
        ("Title", title),
        ("Author", author),
        ("Pages", pages),
        ("Author", author),
        ("Creation date", creation_date),
    ]:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(entry[0])
            with col2:
                st.write(entry[1])


left_col, _, right_col = st.columns([0.35, 0.05, 0.6])

with left_col:
    st.header("Upload your documents here")
    template = st.file_uploader("Template", key="template", type=["pdf"])
    document = st.file_uploader("Document", key="document", type=["pdf"])

    if st.button("Submit"):
        if document and template:
            st.session_state.doc = document
            st.session_state.tpl = template

            files = [
                ("files", (file.name, file.getvalue(), file.type)) for file in [template, document]
            ]

            st.session_state.session_id += 1
            session_id_ = st.session_state.session_id
            data = {
                "session_id": session_id_,
                "message": "Hello, I need help with this document",
            }
            response = requests.post("http://localhost:8000/analysis", data=data, files=files)
            print(response.text)
            st.session_state.results = response.json()["analysis"]["issues"]
            st.session_state.quality = response.json()["analysis"]["rating"]

with right_col:
    st.header("Result")
    defects_tab, summary_tab, preview_tab, chat_tab = st.tabs(
        ["Defects", "Summary", "Preview", "Chat"]
    )
    with defects_tab:
        results = st.session_state.results
        if results:
            display_result(defects_tab, results)
        else:
            defects_tab.write("Nothing to see...")
    with summary_tab:
        show_summary()
        session_id_ = st.session_state.session_id
        data = {"session_id": session_id_, "message": "hello"}
        r = requests.post("http://localhost:8000/summary", data=data)
        print(r.text)
    with preview_tab:
        highlight_defects()
    with chat_tab:
        prompt = st.chat_input("Ask something about document")
        if prompt:
            session_id_ = st.session_state.session_id
            data = {"session_id": session_id_, "message": prompt}
            r = requests.post("http://localhost:8000/chat", data=data)
            if r.ok:
                message = r.json()["completion"]
                display_chat(str(prompt), message)
