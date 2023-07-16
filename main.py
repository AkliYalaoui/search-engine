from flask import Flask, request, render_template, jsonify
from search import search
from filter import Filter
from storage import DBStorage
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
            filtered = fi.sort(contrast_ratio=False)
            filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
            filtered=filtered.to_dict(orient='records')
        return render_template("main.html", results=filtered, query=query)
    else:
        return render_template("main.html")

@app.route("/about", methods=['GET'])
def about_page():
    storage = DBStorage()
    stats = storage.top_queries_this_month()
    x = [item[0] for item in stats]
    y = [item[1] for item in stats]
    print(x)
    print(y)
    return render_template("about.html", labels=x, values=y)


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    query = request.form.get('query')
    storage = DBStorage()
    suggestions = storage.get_autocomplete_suggestions(query)
    return jsonify(suggestions=suggestions)


if __name__ == "__main__" :
    app.run(debug=True)