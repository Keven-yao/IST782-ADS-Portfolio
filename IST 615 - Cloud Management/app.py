from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
#from docx import Document
import pdfplumber
import re

en_letter = '[\u0041-\u005a|\u0061-\u007a\`\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\]\{\}\\\|\;\'\'\:\"\"\,\.\/\<\>\?]+' # 大小写英文字母
zh_char = '[\u4e00-\u9fa5\u3002\uff0c\uff1b\uff1a\u201c\u201d\u2018\u2019\uff01\uff1f\uff08\uff09\u300a\u300b\u3010\u3011\u3014\u3015\uff5b\uff5d\u3016\u3017\u300c\u300d\u300e\u300f\uff08\uff09\u3010\u3011\uff3b\uff3d\uff62\uff63\uff62\uff63\uff5b\uff5d\uff5b\uff5d\uff5b\uff5d]+' # 中文字符

def extract_words_from_pdf(pdf_path):
    english_words = []
    chinese_words = []

    with pdfplumber.open(pdf_path) as pdf:
        docu_zh = Document()
        docu_en = Document()
        for j in range(len(pdf.pages)):
            # extract
            temp_page = pdf.pages[j]
            temp_words = temp_page.extract_text()
            # find Chinese and English
            temp_zh_words = re.findall(zh_char, temp_words)
            temp_en_words = re.findall(en_letter, temp_words)
            # join
            temp_zh_words = ','.join(temp_zh_words)
            temp_en_words = ' '.join(temp_en_words)
            docu_en.add_paragraph(temp_en_words)
            docu_zh.add_paragraph(temp_zh_words)
    return docu_en, docu_zh

app = Flask(__name__)

@app.route("/")  # this sets the route to this page
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return "No file selected"
        
        if file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file.save(filename)

            docu_en, docu_zh = extract_words_from_pdf(filename)

            docu_en.save("extracted_English_words.docx")
            docu_zh.save("extracted_Chinese_words.docx")

            # Extracted words for preview
            en_paragraphs = [p.text.strip() for p in docu_en.paragraphs]
            zh_paragraphs = [p.text.strip() for p in docu_zh.paragraphs]

            return render_template('preview.html', en_paragraphs=en_paragraphs, zh_paragraphs=zh_paragraphs)
        else:
            return "File uploaded is not a PDF."
    else:
        return "Method not allowed."

@app.route('/download_en')
def download_en():
    return send_file("extracted_English_words.docx", as_attachment=True)

@app.route('/download_zh')
def download_zh():
    return send_file("extracted_Chinese_words.docx", as_attachment=True)

if __name__ == '__main__':
    app.run()
