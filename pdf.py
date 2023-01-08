from fpdf import FPDF
import json
from ordering import extract_data, extractOrder
#import ordering

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

#data
# f = open("message2.json")
# data = json.load(f)
paragraphs = extract_data("https://media.discordapp.net/attachments/1061328440021753858/1061439675358773278/IMG_2940.jpg")
# paragraphs = ['Old English Period', 'The Old English period. or the Anglo-Saxcen period extended from the Invasion of Celtic England by Germanic tribes Cthe Angles, Sascons, and Juts) in the first half of the fifth century to the conquest of England in 1066 by the Norman French under the leadership of William the Conqueror. The Anglo Saxons were then converted to Christianity in the 7th century. ', 'Page No', 'I', 'English literature started with Songs and stories of these three tribes. Its subject were the sea, the beats, battles, adventures and the love of home. Their poetry reflected their profound emotions and bravery, Accent, ', 'alliteration, and sudden break of each line', 'their', 'gave', "poetry a kind of (Matrial) Martial rhythm. The main Characteristics of Anglo-Saxon literature are the love of freedom rensponsiveness to nature, strong religious Convictions belief in fate, respect to womanhood and a devotion to glory as the ruling motive in every warrior's life. ", 'Beowulf was the first great, heroic folk epic of unknown author It is a Story of about 3000 lines. A brave young man, Beawolf, from Southen Sweden, goes to help Hrothgar, king of Danies and kills a terrible monster Grendel and This mother-Later, he becomes the king of his people and should save his people from a fire-breathing creature. He kills the creature but gets badly wounded and dies. The poem ends with Beowulf\'s funeral " There is no rhyme but alliteration is used in it. ']
#order = ['h', 'p', 'h', 'h', 'p', 'p', 'p', 'p', 'p', 'p']
# paragraphs = ordering.extractData(data)
order = extractOrder(paragraphs)

wpdf = PDF()
wpdf.add_page()    

for i in range(len(order)):
    if order[i] == 'h':
        wpdf.headline(paragraphs[i])
    elif order[i] == 'p':
        wpdf.paragraph(paragraphs[i])

wpdf.output('formatted.pdf', 'F')

