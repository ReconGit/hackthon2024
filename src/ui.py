import streamlit as st

st.set_page_config(page_title="QuickForm", layout="wide", initial_sidebar_state="expanded")

st.title("QuickForm")

file_column, result_column = st.columns(2)

with file_column:
    st.header("Drop here your documents")
    document = st.file_uploader("Document", key="document", type=["txt", "pdf"])
    template = st.file_uploader("Template", key="template", type=["txt", "pdf"])

document_content = None
if document is not None:
    file_type = document.type
    if file_type == "text/plain":
        document_content = document.getvalue()
    elif file_type == "application/pdf":
        document_content = document.getvalue()

template_content = None
if template is not None:
    file_type = template.type
    if file_type == "text/plain":
        template_content = template.getvalue()
    elif file_type == "application/pdf":
        template_content = template.getvalue()

data = [
    {"line": 12, "error": "Phone number has invalid format"},
    {"line": 24, "error": "some other text"},
]

if st.button("Submit"):
    with result_column:
        st.header("Result")
        for d in data:
            c = st.container(border=True)
            icon_col, error_col = c.columns([0.05, 0.8], vertical_alignment="center")
            with icon_col:
                # st.write("sinep")
                st.image("error.png")
            with error_col:
                st.write(f"Page {d["line"]}")
                st.write(f"{d["error"]}")
else:
    with result_column:
        st.header("Result")
        st.write("Nothing to see...")
