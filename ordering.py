import requests

# def extractData(data):
#     paragraphs = [para["text"] for block in data["blocks"] for para in block["paras"]]
#     paragraphs = [x for x in paragraphs if any(c.isalpha() for c in x)]
#     return paragraphs


# f = open("message2.json")
# coords = [word["bounds"][0:4] for block in data["blocks"] for para in block["paras"] for word in para["words"] if word["text"].isalpha()]
# rect_ys = []
# sizes = []
# for list in coords:
#     rect_ys.append([coord[1] for coord in list])

# for y in rect_ys:
#     sizes.append(max(y) - min(y))
# avg = sum(sizes)/len(sizes)


# words_too_small = []
# for i in range(len(sizes)):
#     if sizes[i] < avg/2:
#         words_too_small.append(i)

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


print(para := extract_data("https://media.discordapp.net/attachments/1061328440021753858/1061439675358773278/IMG_2940.jpg"))
print(extractOrder(para))