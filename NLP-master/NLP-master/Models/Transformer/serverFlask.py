from flask import Flask
from flask import request
from Neo4jConnection import Graph

app = Flask(__name__)
conn = Graph(app)
Graph.logger = app.logger.info

@app.route('/')
def check_app():
    return 'app working correctly'

@app.route('/document/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        result = conn.get_document(doc_id)
        return result
    except KeyError:
        return "Argument 'doc_id' is missing."

@app.route('/document/create', methods=['POST'])
def create_document():
    try:
        text = request.form['text']
        result = conn.create_document(text)
        return result
    except KeyError:
        return "Argument 'Text' is missing."

@app.route('/document/<int:docId>', methods=['DELETE'])
def delete_document(doc_id):
    try:
        result = conn.delete_document(doc_id)
        return result
    except KeyError:
        return "Argument 'doc_id' is missing."

@app.route('/count/<node>')
def count_words(node):
    if node == 'Word':
        words_in_corpus = conn.count_words()
        return words_in_corpus
    else:
        return "node %s doesn't exist" % node


# 34.200.68.82
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
