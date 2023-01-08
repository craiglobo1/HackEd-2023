from flask import Flask, jsonify, request
from urllib.parse import unquote
from google.cloud import vision

app = Flask(__name__)

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
def hello_world():
    return jsonify({"Routes": {
        "v1/":[
            "get_text_bounds/"
        ]
    }})

@app.route("/v1/get_text_bounds/")
def get_text_bounds():
    app.logger.info(request.args)
    if request.args.get("uri", default=-1) == -1:
        return jsonify({"Error" : "No uri for image path provided"})
    else:
        data = get_ocr_data_from_uri(request.args["uri"])

        return jsonify(data)

@app.route("/v1/generate_typed_notes/")
def generate_typed_notes():
    if request.args.get("uris", default=-1) == -1:
        return jsonify({"Error" : "No img uris provided"})
    else:
        try:
            uris = eval(request.args.get("uris"))
            if isinstance(uris, list):
                if all([ isinstance(val, str) for val in uris]):
                    
                    return jsonify(uris)
        except:
            pass
        return jsonify({"Error" : "Invalid uris provided"})

if __name__ == "__main__":
    app.run()