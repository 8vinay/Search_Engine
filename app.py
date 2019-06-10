from flask import Flask, render_template, request
import search

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['t']
    processed_text = search.process_query(text)
    pt = []
    if len(processed_text) > 10:
    	pt = processed_text[10:]
    return render_template('Results.html', links=processed_text[:10], links1=pt, query=text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')