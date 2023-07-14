from flask import Flask, request, render_template
from search import search
from filter import Filter
import html
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        filtered = None
        if query : 
            results = search(query)
            fi = Filter(results)
            filtered = fi.filter()
            filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
            filtered=filtered.to_dict(orient='records')
        return render_template("main.html", results=filtered, query=query)
    else:
        return render_template("main.html")


if __name__ == "__main__" :
    app.run(debug=True)