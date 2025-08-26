from flask import Flask, render_template, request
from autolider import search  # Make sure to import the search function

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')  # Placeholder for homepage template

@app.route('/search', methods=['POST'])
def search_results():
    part_number = request.form['part_number']
    results = search(part_number)  # Call the search function from autolider.py
    return render_template('results.html', results=results)  # Placeholder for results template

if __name__ == '__main__':
    app.run(debug=True)