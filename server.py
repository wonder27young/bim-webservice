#!/usr/bin/python
#coding:utf-8
from flask import Flask,jsonify,make_response,request,json,render_template

import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
app = Flask(__name__)

questions = []
with open('data.txt') as data_file:
    questions = json.load(data_file)
def sync_data_to_file():
    with io.open('data.txt', 'w+', encoding='utf8') as outfile:
        str_ = json.dumps(questions,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)
@app.route('/')
def index():
    return render_template("index.html")
@app.route('/auth/login')
def auth_login():
    return render_template("auth/login.html")
@app.route('/question_list')
def get_question_list_view():
    return render_template("question_list")

@app.route('/api/questions',methods=['GET'])
def get_questions():
    return jsonify({'questions': questions})
@app.route('/api/questions/<int:ques_id>', methods=['GET'])
def get_question(ques_id):
    question = filter(lambda t: t['id'] == ques_id, questions)
    if len(question) == 0:
        abort(404)
    return jsonify({'question': question[0]})
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
@app.route('/api/questions', methods=['POST'])
def create_question():
    if not request.json or not 'title' in request.json:
        abort(400)
    question = {
        'id': questions[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'score': request.json.get('score', 0)
    }
    questions.append(question)
    sync_data_to_file()
    return jsonify({'quesion': question}), 201
@app.route('/api/questions/<int:ques_id>', methods=['PUT'])
def update_question(ques_id):
    question = filter(lambda t: t['id'] == ques_id, questions)
    if len(question) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'score' in request.json and type(request.json['score']) is not int:
        abort(400)
    question[0]['title'] = request.json.get('title', question[0]['title'])
    question[0]['description'] = request.json.get('description', question[0]['description'])
    question[0]['score'] = request.json.get('score', question[0]['score'])
    sync_data_to_file()
    return jsonify({'question': question[0]})

@app.route('/api/questions/<int:ques_id>', methods=['DELETE'])
def delete_question(ques_id):
    question = filter(lambda t: t['id'] == ques_id, questions)
    if len(question) == 0:
        abort(404)
    questions.remove(question[0])
    sync_data_to_file()
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0')