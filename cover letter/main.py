from flask import Flask, render_template, request
import openai
from fpdf import FPDF
pdf = FPDF()



app = Flask(__name__)
openai.api_key = "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"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name'] 
    job_des= request.form['job_des']
    company = request.form['company']
    experience = request.form['experience']

    keywords = openai.Completion.create(
        engine = "text-davinci-003",
        prompt=(f"Extract the keywords that can be used to write a cover letter from the following JOB description {job_des}"),
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    keywords = keywords.choices[0].text
    
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt=(f"Write a cover letter for {name} who want to apply at {company} having professioanl experience i-e {experience} containing the following keywords {keywords}"),
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    letter = completions.choices[0].text
    return render_template('generate.html', message=letter, name=name)


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    content = f"\n{request.form['content']}\n\n\n"
    name = request.form['name']
    pdf.add_page()
    pdf.set_font("Arial",'B', size = 20)
    pdf.cell(180, 2, txt = f"\n\n\n\n\n\nCover Letter",
            ln = 1, align = 'C')

    pdf.set_font("Arial", size = 8)
    pdf.multi_cell(w = 180, h = 6, txt = content, border = 0, align = 'L', fill = False)
    
    pdf.output(f"{name}.pdf") 
    return render_template('index.html')


if __name__ == '_main_':
    app.run(debug=True)
