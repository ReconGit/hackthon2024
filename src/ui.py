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
    for entry in result:
        c = con.container(border=True)
        icon_col, error_col = c.columns([0.05, 0.8], vertical_alignment="center")
        with icon_col:
            st.image("resources/error.png")
        with error_col:
            st.write(entry["message"])


if "results" not in st.session_state:
    st.session_state.results = None

left_col, _, right_col = st.columns([0.35, 0.05, 0.6])

with left_col:
    results = st.session_state.results
    st.header("Upload your documents here")
    document = st.file_uploader("Document", key="document", type=["pdf"])
    template = st.file_uploader("Template", key="template", type=["pdf"])

    files = []
    if document is not None:
        file_type = document.type
        if file_type == "application/pdf":
            files.append(("files", (document.name, document.getvalue(), document.type)))

    if template is not None:
        file_type = template.type
        if file_type == "application/pdf":
            files.append(("files", (template.name, template.getvalue(), template.type)))

    if st.button("Submit"):
        if document and template:
            st.session_state.results = [
                {"level": "error", "message": "Incorrect phone number"},
                {"level": "warning", "message": "Better wording. Try ...."},
            ]
            data = {"session_id": 1, "message": "some test message"}
            response = requests.post("http://localhost:8000/chat", data=data, files=files)
            print(response.text)

with right_col:
    results_tab, preview_tab, chat_tab = st.tabs(["Results", "Preview", "Chat"])
    with results_tab:
        st.header("Results")
        results = st.session_state.results
        if results:
            display_result(results_tab, results)
        else:
            right_col.write("Nothing to see...")
    with preview_tab:
        st.header("Preview")
        stpdf.pdf_viewer("resources/test_pdf.pdf", width=500)
    with chat_tab:
        st.header("Chat")
        prompt = st.chat_input("Ask something about document")
        if prompt:
            st.write(f"Prompt: {prompt}")
