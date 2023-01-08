
from urllib.parse import unquote
from fpdf import FPDF
import requests
from drive import upload_data_to_drive
from main import pages_to_pdf
import base64
class PDF(FPDF):
    def headline(self, headline):
        self.set_font('Times', 'B', 18)
        self.set_fill_color(255, 255, 255)
        self.cell(0, 5, headline, 0, 1, 'C', 1)
        self.ln(4)

    def paragraph(self, paragraph):
        self.set_font('Times', '', 14)
        self.set_fill_color(255, 255, 255)
        self.multi_cell(0, 5, paragraph)
        self.ln(4)


def extract_data(img_url):
    req = requests.get(F"https://handwrite-374020.wn.r.appspot.com/v1/get_text_bounds/?uri={img_url}")
    data = req.json()

    get_height = lambda x : max(x)-min(x)

    heights = [get_height([ bound[1] for bound in para["bounds"]]) for block in data["blocks"] for para in block["paras"] ]

    avg_height = sum(heights)/len(heights)

    paragraphs = [para["text"] for block in data["blocks"] for para in block["paras"] if get_height([bound[0] for bound in para["bounds"]]) >= avg_height*0.5]
    paragraphs = [x for x in paragraphs if any(c.isalpha() for c in x)]

    for i in range(len(paragraphs)):
        paragraphs[i] = paragraphs[i].replace(" .", ".")
        paragraphs[i] = paragraphs[i].replace(". ", ".")
        paragraphs[i] = paragraphs[i].replace(".", ". ")
        paragraphs[i] = paragraphs[i].replace(" ,", ",")
        paragraphs[i] = paragraphs[i].replace(", ", ",")
        paragraphs[i] = paragraphs[i].replace(",", ", ")
        paragraphs[i] = paragraphs[i].replace(" )", ")")
        paragraphs[i] = paragraphs[i].replace(") ", ")")
        paragraphs[i] = paragraphs[i].replace(")", ") ")
        paragraphs[i] = paragraphs[i].replace(" (", "(")
        paragraphs[i] = paragraphs[i].replace("( ", "(")
        paragraphs[i] = paragraphs[i].replace("(", " (")
        paragraphs[i] = paragraphs[i].replace(" -", "-")
        paragraphs[i] = paragraphs[i].replace("- ", "-")

    return paragraphs


def extractOrder(paragraphs):
    order = []
    for i in range(len(paragraphs)):
        # print([para for para in paragraphs[i].split(" ") if para != ""])
        if all([ para[0].isupper() for para in paragraphs[i].split(" ") if para != ""]):
            order.append('h')
        else:
            order.append('p')
    return order


def pages_to_pdf_here(uris):
    wpdf = PDF()
    wpdf.add_page()
    wpdf.add_font(fname='times_new_roman.ttf')
    wpdf.add_font(fname='times_new_roman_bold.ttf')
    for uri in uris:
        uri = unquote(uri)
        paragraphs = extract_data(uri)
        order = extractOrder(paragraphs)


        for i in range(len(order)):
            if order[i] == 'h':
                wpdf.headline(paragraphs[i])
            elif order[i] == 'p':
                wpdf.paragraph(paragraphs[i])

    return wpdf.output(dest='S')


# with open("test2.pdf", "w+", encoding="utf-8") as wf:
#     wf.write(data)
data = pages_to_pdf(["https://i.pinimg.com/564x/e5/53/bf/e553bf6c13fb6768e5289ca7bd142fff--penmanship-cursive.jpg"])
upload_data_to_drive(data)