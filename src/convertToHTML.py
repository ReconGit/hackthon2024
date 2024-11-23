import mammoth
from odf import opendocument, odf2xhtml
import spire.pdf as pdf
import aspose.pdf as apdf
import pdf2docx
from tika import parser

def odtToHtml(fileName: str):
    odf_type = odf2xhtml.ODF2XHTML()

    html = odf_type.odf2xhtml(fileName)

    file = open(fileName + ".html", "w+")
    file.write(html)
    file.close()

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

def pdfToHtml_v3(fileName: str):
    file = pdf2docx.Converter(fileName)

    file.convert(fileName + ".docx", start=0, end=None)

    file.close()

def pdfToRawText(fileName: str):
    raw = parser.from_file(fileName)
    print(raw['content'])


# docxToHtml("../documents/grants/Grant Proposal for Solar Panel Installation.docx")
#pdfToHTML("../documents/build_permit/Invalid_example_multiple_check.pdf")
pdfToHtml_v2("../documents/employment_contract/Employment Contract sample.pdf")
#pdfToHtml_v3("../documents/employment_contract/Employment Contract sample.pdf")
#pdfToRawText("../documents/employment_contract/Employment Contract sample.pdf")
