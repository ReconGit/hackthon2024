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
        # icon_col, error_col, goto_col = c.columns([0.05, 0.6, 0.1], vertical_alignment="center")
        icon_col, error_col = c.columns([0.05, 0.6], vertical_alignment="center")
        with icon_col:
            show_icon(entry["level"])
        with error_col:
            with st.expander(entry["message"]):
                st.write("Bdaksljflkajds;f")
        # with goto_col:
        #     st.button("Goto", key=f"goto_{i}")
        i += 1


if "results" not in st.session_state:
    st.session_state.results = None

left_col, _, right_col = st.columns([0.35, 0.05, 0.6])

with left_col:
    results = st.session_state.results
    st.header("Upload your documents here")
    document = st.file_uploader("Document", key="document", type=["pdf"])
    template = st.file_uploader("Template", key="template", type=["pdf"])

    if document and template:
        files = [("files", (file.name, file.getvalue(), file.type)) for file in [document, template]]

    if st.button("Submit"):
        if document and template:
            st.session_state.results = [
                {"level": "error", "message": "Incorrect phone number"},
                {"level": "warning", "message": "Better wording. Try ...."},
            ]
            data = {
                "session_id": "1",
                "message": "Don't fill in Jozef Mrkvicka, fill my actual name instead",
            }
            response = requests.post("http://localhost:8000/analysis", data=data, files=files)
            print(response.text)

with right_col:
    st.header("Result")
    defects_tab, overview_tab, preview_tab, chat_tab = st.tabs(["Defects", "Overview", "Preview", "Chat"])
    with defects_tab:
        results = st.session_state.results
        if results:
            display_result(defects_tab, results)
        else:
            right_col.write("Nothing to see...")
    with overview_tab:
        st.write("")
    with preview_tab:
        stpdf.pdf_viewer("resources/test_pdf.pdf", width=500)
    with chat_tab:
        prompt = st.chat_input("Ask something about document")
        if prompt:
            st.write(f"Prompt: {prompt}")
