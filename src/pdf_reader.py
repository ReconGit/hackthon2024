import fitz

pdf_path = "../data/2.pdf"

with fitz.open(pdf_path) as pdf_document:
    for page_num in range(pdf_document.page_count):
        # Get each page
        page = pdf_document[page_num]
        # Extract text
        text = page.get_text("text")
        print(f"Page {page_num + 1}:\n{text}\n")