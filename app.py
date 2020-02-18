#!flask/bin/python
from flask import Flask, jsonify, request, make_response, Response, abort
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
if os.environ.get('DB_ENV_MONGO_VERSION'):
    app.config['MONGO_URI'] = 'mongodb://db:27017/notes'
else:
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/notes'

mongo = PyMongo(app)
notebooks = mongo.db.notebooks
notes = mongo.db.notes

def no_content():
    abort(Response(response='204: No resource exists', content_type='application/json', status=204))

def missing_or_invalid_key():
    abort(Response(response='400: Request body has missing or invalid parameters', content_type='application/json', status=400))

def missing_notebook():
    abort(Response(response='400: Invalid notebook', content_type='application/json', status=400))

# route for retrieving all notes
@app.route('/notebook', methods=['GET'])
def get_all_notebooks():
    output = []
    nb_entries = notebooks.find()
    # appends notebook objects to the output if any are found
    if nb_entries:
        for nb in nb_entries:
            output.append({'nbid': nb['nbid'], 'name' : nb['name']})
   
    return jsonify({'result' : output})

# route for retrieving one notebook by id number
@app.route('/notebook/<int:nbid>', methods=['GET'])
def get_one_notebook(nbid):
    output = []
    nb = notebooks.find_one({'nbid': nbid})
    # returns a notebook object if one exists
    if nb:
        note_data = notes.find({'nbid': {'$eq': nbid}})
        output.append({
            'nbid': nb['nbid'], 
            'name': nb['name'],
            'notes': []})
        for n in note_data:
            output[0]['notes'].append({
                'nid': n['nid'], 
                'title' : n['title'],
                'nbid': n['nbid'],
                'body': n['body'],
                'tags': n['tags'],
                'created': n['created'],
                'lastModified': n['lastModified']            
            })
        return jsonify({'result' : output})
    # returns a 204 status code if not
    else:
        no_content()

@app.route('/notebook/<int:nbid>/<string:tag>', methods=['GET'])
def get_one_notebook_by_tag(nbid, tag):
    output = []
    nb = notebooks.find_one({'nbid': nbid})
    # returns a notebook object if one exists
    if nb:
        note_data = notes.find({'nbid': {'$eq': nbid}})
        output.append({
            'nbid': nb['nbid'], 
            'name': nb['name'],
            'notes': []})
        for n in note_data:
            if tag in n['tags']:
                output[0]['notes'].append({
                    'nid': n['nid'], 
                    'title' : n['title'],
                    'nbid': n['nbid'],
                    'body': n['body'],
                    'tags': n['tags'],
                    'created': n['created'],
                    'lastModified': n['lastModified']            
                })
        return jsonify({'result' : output})
    # returns a 204 status code if not
    else:
        no_content()

# route for posting a new notebook
@app.route('/notebook', methods=['POST'])
def post_notebook():
    output = []
    name = request.json.get('name')
    # returns a 400 status if no name is present in the request body
    if not name:
        missing_or_invalid_key()
    max_id_nb = notebooks.find_one(sort=[('nbid', -1)])
    # increments the notebook id number and sets it to 1 if the collection is empty
    if max_id_nb:
        nbid = max_id_nb['nbid'] + 1
    else:
        nbid = 1
    # inserts a new notebook and returns the newly created notebook data
    notebooks.insert_one({'name': name, 'nbid': nbid})
    new_nb = notebooks.find_one({'nbid': nbid})
    output.append({'nbid': nbid, 'name' : new_nb['name']})
    return jsonify({'result' : output})

# route for editing an existing notebook
@app.route('/notebook/<int:nbid>', methods=['PUT'])
def edit_notebook(nbid):
    output = []
    new_name = request.json.get('name')
    nb = notebooks.find_one({'nbid': nbid})
    # checks the name in the body is a string, returns a 400 status otherwise
    if isinstance(new_name, str):
        # checks that the notebook exists and returns a 204 status otherwise
        if nb:
            notebooks.update_one({'nbid': nbid}, {'$set': {'name': new_name}})
            updated_nb = notebooks.find_one({'nbid': nbid})
            output.append({'nbid': updated_nb['nbid'], 'name' : updated_nb['name']})
            return jsonify({'result' : output})
        else:
            no_content()
    else:
        missing_or_invalid_key()
    
# route for deleting a notebook
@app.route('/notebook/<int:nbid>', methods=['DELETE'])
def delete_notebook(nbid):
    output = []
    nb = notebooks.find_one({'nbid': nbid})
    # checks that the notebook exists, returns a 204 status if not
    if nb:
        # deletes the notebook and all corresponding notes, and returns the deleted notebook
        notebooks.delete_one({'nbid': nbid})
        note_data = notes.delete_many({'nbid': {'$eq': nbid}})
        output.append({'nbid': nb['nbid'], 'name' : nb['name'], 'notes': []})
        for note in note_data:
            output[0]['notes'].append({
                'nid': note['nid'], 
                'title' : note['title'],
                'nbid': note['nbid'],
                'body': note['body'],
                'tags': note['tags'],
                'created': note['created'],
                'lastModified': note['lastModified']
            })
        return jsonify({'result' : output})
    else:
        no_content()

# route for getting all existing notes
@app.route('/note', methods=['GET'])
def get_all_notes():
    output = []
    note_entries = notes.find()
    # returns a list of all notes if they exist and an empty list if not
    if note_entries:
        for n in note_entries:
            output.append({
                'nid': n['nid'], 
                'title' : n['title'],
                'nbid': n['nbid'],
                'body': n['body'],
                'tags': n['tags'],
                'created': n['created'],
                'lastModified': n['lastModified']
            })

    return jsonify({'result' : output})

# route for getting a specific note
@app.route('/note/<int:nid>', methods=['GET'])
def get_one_note(nid):
    output = []
    note = notes.find_one({'nid': nid})
    # returns a copy of the selected note if it exists, and a 204 status if not
    if note:
        output.append({
            'nid': note['nid'], 
            'title' : note['title'],
            'nbid': note['nbid'],
            'body': note['body'],
            'tags': note['tags'],
            'created': note['created'],
            'lastModified': note['lastModified']
        })
        return jsonify({'result' : output})
    else:
        no_content()

# route for posting a new note
@app.route('/note', methods=['POST'])
def post_note():
    output = []
    title = request.json.get('title')
    body = request.json.get('body', '')
    tags = request.json.get('tags', [])
    nbid = request.json.get('nbid')
    # returns a 400 status if any of the values passed in the body are the wrong type
    if not isinstance(title, str) or not isinstance(body, str) or not isinstance(tags, list) or not isinstance(nbid, int):
        missing_or_invalid_key()

    # returns a 400 if the notebook id passed does not exist
    if not notebooks.find_one({'nbid': nbid}):
        missing_notebook()

    time = datetime.utcnow()
    max_id_note = notes.find_one(sort=[('nid', -1)])
    # increments the note id number and sets it to 1 if the collection is empty
    if max_id_note:
        nid = max_id_note['nid'] + 1
    else:
        nid = 1
    # inserts and retrieves the new note
    notes.insert_one({
        'title': title, 
        'nid': nid,
        'nbid': nbid,
        'body': body,
        'tags': tags,
        'created': time,
        'lastModified': time
    })
    new_note = notes.find_one({'nid': nid})
    # appends the data from the newly created note
    output.append({
        'nid': nid, 
        'title' : new_note['title'],
        'nbid': new_note['nbid'],
        'body': new_note['body'],
        'tags': new_note['tags'],
        'created': new_note['created'],
        'lastModified': new_note['lastModified']
    })
    return jsonify({'result' : output})

# route for editing an existing note
@app.route('/note/<int:nid>', methods=['PUT'])
def edit_note(nid):
    output = []
    new_title = request.json['title']
    note = notes.find_one({'nid': nid})
    # checks that the note exists, returns a 204 status if not
    if note:
        title = request.json.get('title')
        body = request.json.get('body')
        tags = request.json.get('tags')
        data = {'lastModified': datetime.utcnow()}
        # check the values passed in the body for the correct type
        if isinstance(title, str):
            data["title"] = title
        elif title:
            missing_or_invalid_key()

        if isinstance(body, str):
            data["body"] = body
        elif body:
            missing_or_invalid_key()

        if isinstance(tags, list):
            data["tags"] = tags
        elif tags:
            missing_or_invalid_key()

        # updates the selected note and returns the updated note
        notes.update_one({'nid': nid}, {'$set': data})
        updated_note = notes.find_one({'nid': nid})
        output.append({
            'nid': updated_note['nid'], 
            'title' : updated_note['title'],
            'nbid': updated_note['nbid'],
            'body': updated_note['body'],
            'tags': updated_note['tags'],
            'created': updated_note['created'],
            'lastModified': updated_note['lastModified']
        })
        return jsonify({'result' : output})
    else:
        no_content()

# route for deleting an existing note
@app.route('/note/<int:nid>', methods=['DELETE'])
def delete_note(nid):
    output = []
    note = notes.find_one({'nid': nid})
    # checks that the note exists, returns a 204 status if not
    if note:
        # deletes and returns the selected note
        notes.delete_one({'nid': nid})
        output.append({'nid': note['nid'], 'title' : note['title']})
        return jsonify({'result' : output})
    else:
        no_content()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
