from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from urllib.parse import unquote
from google.cloud import vision
import requests
from fpdf import FPDF
from drive import upload_data_to_drive
import os

app = Flask(__name__)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class PDF(FPDF):
    def headline(self, headline):
        self.set_font('Roboto', 'B', 18)
        self.set_fill_color(255, 255, 255)
        self.cell(0, 5, headline, 0, 1, 'C', 1)
        self.ln(4)

    def paragraph(self, paragraph):
        self.set_font('Roboto', '', 14)
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

def pages_to_pdf(uris):
    wpdf = PDF()
    wpdf.add_page()
    wpdf.add_font('Roboto', 'B', 'Roboto-Bold.ttf')
    wpdf.add_font('Roboto', '', 'Roboto-Regular.ttf')
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

def detect_texts(uri):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = unquote(uri)
    print(unquote(uri))

    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    return response.full_text_annotation.pages[0]

def get_ocr_data_from_uri(uri):
    page = detect_texts(uri)

    data ={
        "blocks": []
    }
    for block in page.blocks:
        c_block = {
            "bounds" : [ (ver.x, ver.y) for ver in block.bounding_box.vertices],
            "paras" : []
        }

        for paragraph in block.paragraphs:
            c_para = {
                "bounds" : [ (ver.x, ver.y) for ver in paragraph.bounding_box.vertices],
                "words" : []
            }
            for word in paragraph.words:
                c_word = {
                    "bounds" : [ (ver.x, ver.y) for ver in word.bounding_box.vertices],
                    "chars" : []
                }
                for symbol in word.symbols:
                    c_symbol = {
                        "bounds" : [ (ver.x, ver.y) for ver in symbol.bounding_box.vertices],
                        "text" : symbol.text
                    }
                    c_word["chars"].append(c_symbol)
                c_word["text"] = "".join([ s["text"] for s in c_word["chars"]])
                c_para["words"].append(c_word)
            c_para["text"] = " ".join([ s["text"] for s in c_para["words"]])
            c_block["paras"].append(c_para)
        data["blocks"].append(c_block)
    return data


@app.route("/")
@cross_origin()
def hello_world():
    return jsonify({"Routes": {
        "v1/":[
            "get_text_bounds/"
        ]
    }})

@app.route("/v1/get_text_bounds/")
@cross_origin()
def get_text_bounds():
    app.logger.info(request.args)
    if request.args.get("uri", default=-1) == -1:
        return jsonify({"Error" : "No uri for image path provided"})
    else:
        data = get_ocr_data_from_uri(request.args["uri"])

        return jsonify(data)

@app.route("/v1/generate_typed_notes/")
@cross_origin()
def generate_typed_notes():
    if request.args.get("uris", default=-1) == -1:
        return jsonify({"Error" : "No img uris provided"})
    else:
        try:
            uris = eval(request.args.get("uris"))
        except:
            return jsonify({"Error" : "Invalid uris provided"})

        if isinstance(uris, list):
            # if all([ isinstance(val, str) for val in uris]):
            app.logger.info("created pdf")
            data = pages_to_pdf(uris)
            upload_data_to_drive(data)

            return jsonify(uris)
        else:
            return jsonify({"Error" : "uris not a list"})

if __name__ == "__main__":
    app.run()