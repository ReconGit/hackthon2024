import streamlit as st
import streamlit_pdf_viewer as stpdf

st.set_page_config(page_title="QuickForm", layout="wide", initial_sidebar_state="expanded")
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
    st.header("Drop here your documents")
    document = st.file_uploader("Document", key="document", type=["txt", "pdf"])
    template = st.file_uploader("Template", key="template", type=["txt", "pdf"])

    if st.button("Submit"):
        st.session_state.results = [
            {"level": "error", "message": "Incorrect phone number"},
            {"level": "warning", "message": "Better wording. Try ...."},
        ]

    # st.header("Chat")

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


# if document is not None:
#     file_type = document.type
#     if file_type == "text/plain":
#         document_content = document.getvalue()
#     elif file_type == "application/pdf":
#         document_content = document.getvalue()

# if template is not None:
#     file_type = template.type
#     if file_type == "text/plain":
#         template_content = template.getvalue()
#     elif file_type == "application/pdf":
#         template_content = template.getvalue()
