import mammoth
import spire.pdf as pdf
import aspose.pdf as apdf


def docxToHtml(fileName: str):
    file = open(fileName, "rb")

    result = mammoth.convert_to_html(file)

    outFile = open(fileName + ".html", "w+")

    outFile.write(result.value)

    outFile.close()

    file.close()

# Converts into image
def pdfToHTML(fileName: str):
    doc = pdf.PdfDocument()

    doc.LoadFromFile(fileName)

    doc.SaveToFile(fileName + ".html", pdf.FileFormat.HTML)

    doc.Close()

# Converts into image
def pdfToHtml_v2(fileName: str):
    document = apdf.Document(fileName)

    save_options = apdf.HtmlSaveOptions()
    document.save(fileName + ".html", save_options)

# For texting
# # docxToHtml("../documents/grants/Grant Proposal for Solar Panel Installation.docx")
pdfToHTML("../data/instructions/ziadostogrant.pdf")
# pdfToHtml_v2("../data/1.pdf")
# #pdfToHtml_v3("../documents/employment_contract/Employment Contract sample.pdf")
# #pdfToRawText("../documents/employment_contract/Employment Contract sample.pdf")
