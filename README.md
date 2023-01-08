# HackEd-2023 : Handwrite
---
**An easy way to convert Handwritten Notes into a readble digital PDF**

**Handwrite** is a web app that provides an easy way to convert Handwritten Notes into a typed digital PDF file

This project was made for the HACKEd 2023 hackaton and was created within a 24-hour time frame on Jan 7 – 8, 2023 by

- [Craig Lobo](https://github.com/craiglobo1) : Front End and Api setup 
- [Kaiden Mastel](https://github.com/KaidenMastel) : Handling Cloud Vision API
- [Brian](https://github.com/koalazzzzzz) : Doing Formating for pdf output

Devpost Link: TBA
## Prerequisites
- Python 3.6 or later (https://www.python.org/)
- Pygame
- flask
- google-cloud-vision
- google-api-python-client
- fpdf2

## Usage
First you'll need the all the libraries in the requirements file 
```shell
pip install -r requirements.txt
```
Ensure Google [credentials.json]() is provided from the Google Vision API

Ensure Enviromental Variable GOOGLE_APPLICATION_CREDENTIALS is set
```shell
set GOOGLE_APPLICATION_CREDENTIALS=<credentials path>
```

Run [main.py](./main.py) in development mode
```shell
> flask --app main.py --debug run
```