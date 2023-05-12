from flask import (
    Flask, 
    request, 
    render_template, 
    redirect, 
    url_for, 
    jsonify

)

from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

cxn_str = 'mongodb+srv://zulfian506150700:zulfian@cluster0.ksi9p44.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cxn_str)

db = client.dbsparta_plus_week2

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id' : False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else[0]
        words.append({
            'word' : word['word'],
            'definition' : definition,
        })

    msg = request.args.get('msg')
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):     
    api_key = 'f7eacc6d-e1b2-470a-8b61-13e0b89b0ec3' 
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'error',
            msg=f'Kata "{keyword}" tidak ditemukan dalam kamus.',
            suggestions=[]
        ))
    
    if type(definitions[0]) is str:
        suggestions = definitions
        return redirect(url_for(
            'error',
            msg=f'Kata "{keyword}" tidak ditemukan dalam kamus. Mungkin Anda mencari salah satu kata berikut:',
            suggestions=suggestions
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word' : word,
        'definitions' : definitions,
        'date': datetime.now().strftime('%Y.%m.%d'),
    }
    db.words.insert_one(doc)

    return jsonify({
        'result': 'success', 
        'msg': f'the word, {word}, berhasil disimpan!!',
    })


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.examples.delete_many({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word {word}, berhasil dihapus!'
    })

@app.route('/error')
def error():
    msg = request.args.get('msg')
    suggestions = request.args.get('suggestions')
    return render_template('error.html', msg=msg, suggestions=suggestions)

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word' : word})
    examples = []
    for example in example_data :
        examples.append({
            'example' : example.get('example'),
            'id' : str(example.get('_id')),
        })
    return jsonify({
        'result': 'success',
        'example' : examples
    })

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')

    doc = {
        'word' : word,
        'example' : example,
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg' : f'Your example, {example},  for the word, {word}, was save!',
    })


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})

    return jsonify({
        'result': 'success',
        'msg' : f'Your example for the word, {word}, was delete!',
        })



   
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)



