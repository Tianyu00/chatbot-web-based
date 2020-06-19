from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import re
from collections import Counter
from string import punctuation
from math import sqrt
# import json
from sqlalchemy import create_engine

db_string = os.environ['DATABASE_URL']

db = create_engine(db_string)

# try:
#     db.execute('DROP TABLE words;')
# except:
#     pass
# try:
#     db.execute('DROP TABLE sentences;')
# except:
#     pass
# try:
#     db.execute('DROP TABLE associations;')
# except:
#     pass

# db.execute("CREATE TABLE words(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY  , word TEXT UNIQUE)")
# db.execute("CREATE TABLE sentences(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY , sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)")
# db.execute("CREATE TABLE associations (id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY , word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS words(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, word TEXT UNIQUE)")
db.execute("CREATE TABLE IF NOT EXISTS sentences(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)")
db.execute("CREATE TABLE IF NOT EXISTS associations (id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)")

db.execute("CREATE TABLE IF NOT EXISTS conversations (id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, input TEXT, response TEXT)")

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# db = SQLAlchemy(app)

# from models import *

def get_id(entityName, text):
    tableName = entityName + 's'
    columnName = entityName
    print('a')
    r = db.execute('SELECT id FROM ' + tableName + ' WHERE ' + columnName + " = '" + text +"'")
    print('b')
    for ri in r:
        r = ri[0]
        break
    if not isinstance(r, int):
        print('8')
        print(text)
        db.execute('INSERT INTO ' + tableName + ' (' + columnName + ") VALUES ('" + text+ "')")
        r = db.execute('SELECT id FROM ' + tableName + ' ORDER BY id DESC LIMIT 1')
        for ri in r:
            r = ri[0]
            break
    print(r)
    return r

def get_words(text):
    wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
    wordsRegexp = re.compile(wordsRegexpString)
    wordsList = wordsRegexp.findall(text.lower())
    return Counter(wordsList).items()

B = 'Hello!'
def response(B,H):
    if H == '':
        return ''

    print('cp4')
    try: db.execute('DROP TABLE results')
    except: pass
    print('cp5')
    db.execute('CREATE TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    print('cp2')
    words = get_words(H)
    words_length = sum([n * len(word) for word, n in words])
    for word, n in words:
        weight = sqrt(n / float(words_length))
        print("select * FROM words INNER JOIN associations ON associations.word_id=words.id INNER JOIN sentences ON sentences.id=associations.sentence_id WHERE words.word='"+ word+"'")
        r = db.execute("select * FROM words INNER JOIN associations ON associations.word_id=words.id INNER JOIN sentences ON sentences.id=associations.sentence_id WHERE words.word='"+ word+"'")
        for ri in r:
            print(ri)
        db.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, '+str(weight)+"*associations.weight/(4+sentences.used) AS weight FROM words INNER JOIN associations ON associations.word_id=words.id INNER JOIN sentences ON sentences.id=associations.sentence_id WHERE words.word='"+ word+"'")
    # if matches were found, give the best one
    print('cp1')
    print('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    try:
        r = db.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
        print(0)
        print(r)
    except:
        print(1)
        r = db.execute('SELECT id, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        print(2)
    print(3)
    print(r)
    for ri in r:
        print(ri)
        r = ri
        break
    db.execute("UPDATE sentences SET used=used+1 WHERE id='"+str(r[0])+"'")
    print('output')
    print(r[0])
    print(r[1])

    words = get_words(B)
    words_length = sum([n * len(word) for word, n in words])
    print('cp3')
    sentence_id = get_id('sentence', H)
    print('cp7')
    for word, n in words:
        word_id = get_id('word', word)
        weight = sqrt(n / float(words_length))
        print("INSERT INTO associations (word_id, sentence_id, weight) VALUES ('" +str(word_id)+ "', '"+str(sentence_id)+ "', '" +str(weight)+ "')")
        db.execute("INSERT INTO associations (word_id, sentence_id, weight) VALUES ('" +str(word_id)+ "', '"+str(sentence_id)+ "', '" +str(weight)+ "')")

    return r[1]


# app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('session.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    global B
    try:
        print(1)
        json['bot_message'] = response(B, json['message'])
        B = json['bot_message']
        if json['message']:
            db.execute("INSERT INTO conversations ( input, response) VALUES ('" + str(json['message']) + "','" + str(json['bot_message']) +"')")
        print(2)
    except:
        pass
    print(json)
    # db.execute('DROP TABLE results2')
    # socketio.to(json['user']).emit('my response', json, callback=messageReceived)
    socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    socketio.run(app, debug=True)























#
# migrate = Migrate(app, db)
#
# class CarsModel(db.Model):
#     __tablename__ = 'cars'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String())
#     model = db.Column(db.String())
#     doors = db.Column(db.Integer())
#
#     def __init__(self, name, model, doors):
#         self.name = name
#         self.model = model
#         self.doors = doors
#
#     def __repr__(self):
#         return f"<Car {self.name}>"
#
#
# @app.route('/')
# def hello():
#     return {"hello": "world"}
#
#
# # Imports and CarsModel truncated
#
# @app.route('/cars', methods=['POST', 'GET'])
# def handle_cars():
#     if request.method == 'POST':
#         if request.is_json:
#             data = request.get_json()
#             new_car = CarsModel(name=data['name'], model=data['model'], doors=data['doors'])
#             db.session.add(new_car)
#             db.session.commit()
#             return {"message": f"car {new_car.name} has been created successfully."}
#         else:
#             return {"error": "The request payload is not in JSON format"}
#
#     elif request.method == 'GET':
#         cars = CarsModel.query.all()
#         results = [
#             {
#                 "name": car.name,
#                 "model": car.model,
#                 "doors": car.doors
#             } for car in cars]
#
#         return {"count": len(results), "cars": results}
#
#
#
#
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
