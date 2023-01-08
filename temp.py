
from urllib.parse import unquote
from fpdf import FPDF
import requests
from drive import upload_data_to_drive
from main import pages_to_pdf
import base64
from gtts import gTTS
from io import BytesIO
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

get_height = lambda x : max(x)-min(x)

def extract_data(data):
    # req = requests.get(F"https://handwrite-374020.wn.r.appspot.com/v1/get_text_bounds/?uri={img_url}")
    # data = req.json()


    heights = [get_height([ bound[1] for bound in para["bounds"]]) for block in data["blocks"] for para in block["paras"] ]

    avg_height = sum(heights)/len(heights)

    paragraphs = [para for block in data["blocks"] for para in block["paras"] if get_height([bound[0] for bound in para["bounds"]]) >= avg_height*0.5]
    paragraphs = [para for para in paragraphs if any(char.isalpha() for char in para["text"])]

    for i in range(len(paragraphs)):
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(" .", ".")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(". ", ".")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(".", ". ")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(" ,", ",")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(", ", ",")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(",", ", ")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(" )", ")")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(") ", ")")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(")", ") ")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(" (", "(")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace("( ", "(")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace("(", " (")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace(" -", "-")
        paragraphs[i]["text"] = paragraphs[i]["text"].replace("- ", "-")

    return paragraphs


def extractOrder(paragraphs):
    for i, para in enumerate(paragraphs):
        word_heights = [ get_height([ bound[1] for bound in word["bounds"]]) for word in para["words"]]
        avg_word_height = sum(word_heights)/len(word_heights)
        paragraphs[i]["fnt_size"] = avg_word_height
    
    fnt_sizes = [ para["fnt_size"] for para in paragraphs]
    max_size = max(fnt_sizes)
    min_size = min(fnt_sizes)
    size_range = max_size-min_size


    max_width = -1
    max_height = -1
    for i, para in enumerate(paragraphs):
        max_width = max(max_width, max([ bound[0] for bound in para["bounds"]]))
        max_height = max(max_height, max([ bound[1] for bound in para["bounds"]]))
    
    print(max_width, max_height)

    order = []
    for i, para in enumerate(paragraphs):
        paragraphs[i]["fnt_size"] = (paragraphs[i]["fnt_size"] - min_size)/size_range
        if min([bounds[1] for bounds in para["bounds"]]) < max_height*0.1:
            paragraphs[i]["fnt_size"] *= 1.1
        if paragraphs[i]["fnt_size"] >= 0.95:
            order.append('h')
        else:
            order.append('p')
    
    print([ para["fnt_size"] for para in paragraphs])

    # order = []
    # for i in range(len(paragraphs)):
    #     # print([para for para in paragraphs[i].split(" ") if para != ""])
    #     if all([ para[0].isupper() for para in paragraphs[i].split(" ") if para != ""]):
    #         order.append('h')
    #     else:
    #         order.append('p')
    return order


def pages_to_pdf_here(uris):
    wpdf = PDF()
    wpdf.add_page()
    wpdf.add_font("Roboto", "B", fname='Roboto-Bold.ttf')
    wpdf.add_font("Roboto", "", fname='Roboto-Regular.ttf')
    for uri in uris:
        uri = unquote(uri)
        page_data = requests.get(F"https://handwrite-374020.wn.r.appspot.com/v1/get_text_bounds/?uri={uri}").json()
        paragraphs = extract_data(page_data)
        order = extractOrder(paragraphs)
        print(order)

        for i in range(len(order)):
            if order[i] == 'h':
                wpdf.headline(paragraphs[i]["text"])
            elif order[i] == 'p':
                wpdf.paragraph(paragraphs[i]["text"])

    return wpdf.output(dest='S')


def read_notes(uris):
    text = ""
    for uri in uris:
        uri = unquote(uri)
        page_data = requests.get(F"https://handwrite-374020.wn.r.appspot.com/v1/get_text_bounds/?uri={uri}").json()
        paras = extract_data(page_data)
        paras.sort(key=lambda x: min([bound[1] for bound in x["bounds"]]))
        text += "\n".join([para["text"] for para in paras]) +"\n"
    tts = gTTS(text=text, lang="en", slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

data = read_notes(["https://media.discordapp.net/attachments/1061328440021753858/1061439675358773278/IMG_2940.jpg", "https://media.discordapp.net/attachments/1061328440021753858/1061439675358773278/IMG_2940.jpg"])
upload_data_to_drive(data.read(), "audio/wav","1I56myabft5w2fykmtKA6pYMP416CxM-_")
# mytext = 'Welcome to geeksforgeeks!'
    
# myobj.save("welcome.mp3")


# with open("test2.pdf", "w+", encoding="utf-8") as wf:
#     wf.write(data)
# data = pages_to_pdf_here(["https://media.discordapp.net/attachments/1061328440021753858/1061439675358773278/IMG_2940.jpg"])