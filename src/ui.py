import base64

import requests
import streamlit as st
import streamlit_pdf_viewer as stpdf

st.set_page_config(
    page_title="QuickForm",
    layout="wide",
    page_icon="resources/icon.png",
    initial_sidebar_state="expanded",
)
st.title("QuickForm")


def display_result(con, result):
    i = 0
    for entry in result:
        c = con.container(border=True)
        icon_col, error_col, goto_col = c.columns([0.05, 0.6, 0.1], vertical_alignment="center")
        with icon_col:
            match entry["level"]:
                case "error":
                    st.image("resources/error.png")
                case "warning":
                    st.image("resources/warning.png")

        with error_col:
            st.write(entry["message"])
        with goto_col:
            st.button("Goto", key=f"goto_{i}")
        i += 1


if "results" not in st.session_state:
    st.session_state.results = None

left_col, _, right_col = st.columns([0.35, 0.05, 0.6])

with left_col:
    results = st.session_state.results
    st.header("Upload your documents here")
    document = st.file_uploader("Document", key="document", type=["pdf"])
    template = st.file_uploader("Template", key="template", type=["pdf"])

    data = {"session_id": 1, "message": "hello"}

    if document is not None:
        file_type = document.type
        if file_type == "application/pdf":
            data["document"] = base64.encodebytes(document.getvalue())

    if template is not None:
        file_type = template.type
        if file_type == "application/pdf":
            data["template"] = base64.encodebytes(template.getvalue())

    if st.button("Submit"):
        if document and template:
            st.session_state.results = [
                {"level": "error", "message": "Incorrect phone number"},
                {"level": "warning", "message": "Better wording. Try ...."},
            ]
            response = requests.post("http://localhost:8000/chat", data=data)
            print(response.text)

with right_col:
    st.header("Result")
    defects_tab, preview_tab, chat_tab = st.tabs(["Defects", "Preview", "Chat"])
    with defects_tab:
        results = st.session_state.results
        if results:
            display_result(defects_tab, results)
        else:
            right_col.write("Nothing to see...")
    with preview_tab:
        stpdf.pdf_viewer("resources/test_pdf.pdf", width=500)
    with chat_tab:
        prompt = st.chat_input("Ask something about document")
        if prompt:
            st.write(f"Prompt: {prompt}")
