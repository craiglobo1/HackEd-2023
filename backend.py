import json
from urllib.parse import unquote
from google.cloud import vision


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


if __name__ == "__main__":
    # text = detect_texts("notes.webp")
    page = detect_texts("https://static.wixstatic.com/media/523ce0_adf2af738fc04476801642fc3b87331e~mv2.jpg/v1/fill/w_552,h_824,al_c/pg2.jpg")
    
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
    json.dump(data, open("sample_pg1.json", "w+"), indent=3)   

    #     print(block.bounding_box)
    # print((text[0].paragraphs[0].words[0].symbols))