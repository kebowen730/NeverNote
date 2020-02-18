from app import app, notebooks, notes
import json
from datetime import datetime
from freezegun import freeze_time
import time


def clear_db_and_add_notebook():
	notebooks.drop()
	notes.drop()
        
	response = app.test_client().post(
		'/notebook',
		data=json.dumps({'name': 'Notebook 1'}),
		content_type='application/json',
	)

	return response

def clear_db_and_add_notebook_and_note():
	notebooks.drop()
	notes.drop()
        
	app.test_client().post(
		'/notebook',
		data=json.dumps({'name': 'Notebook 1'}),
		content_type='application/json',
	)

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 1',
			'nbid': 1,
			'body': 'So Many Things',
			'tags': ['good', 'better']
		}),
		content_type='application/json',
	)

	return response

def test_notebook_post():
	clear_db_and_add_notebook()

	response = app.test_client().get(
		'/notebook',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [{'name': 'Notebook 1', 'nbid': 1}]

def test_notebook_post_missing_key_error():
	notebooks.drop()
	notes.drop()
        
	response = app.test_client().post(
		'/notebook',
		data=json.dumps({}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notebook_get_all():
	clear_db_and_add_notebook()

	app.test_client().post(
		'/notebook',
		data=json.dumps({'name': 'Notebook 2'}),
		content_type='application/json',
	)
	response = app.test_client().get(
		'/notebook',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1},
		{'name': 'Notebook 2', 'nbid': 2}
	]

@freeze_time('2019-01-02 03:04:05')
def test_notebook_get_one():
	response = clear_db_and_add_notebook_and_note()

	response = app.test_client().get(
		'/notebook/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1, 'notes': [
			{
				'title' : 'Note 1',
				'nbid': 1,
				'nid': 1,
				'body': 'So Many Things',
				'tags': ['good', 'better'],
				'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
				'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
			}			
		]}
	]

def test_notebook_get_one_missing_notebook_response():
	response = clear_db_and_add_notebook_and_note()

	response = app.test_client().get(
		'/notebook/2',
		content_type='application/json',
	)

	assert response.status_code == 204
	
@freeze_time('2019-01-02 03:04:05')
def test_notebook_get_notes_by_tag():
	clear_db_and_add_notebook_and_note()

	app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)


	response = app.test_client().get(
		'/notebook/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1, 'notes': [
			{
				'title' : 'Note 1',
				'nbid': 1,
				'nid': 1,
				'body': 'So Many Things',
				'tags': ['good', 'better'],
				'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
				'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
			},
			{
				'title' : 'Note 2',
				'nid': 2,
				'nbid': 1,
				'body': 'Even More Things',
				'tags': ['better', 'best'],
				'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
				'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
			}			
		]}
	]

	response = app.test_client().get(
		'/notebook/1/good',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1, 'notes': [
			{
				'title' : 'Note 1',
				'nbid': 1,
				'nid': 1,
				'body': 'So Many Things',
				'tags': ['good', 'better'],
				'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
				'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
			}			
		]}
	]
	
def test_notebook_edit_one():
	response = clear_db_and_add_notebook()

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1}
	]

	app.test_client().put(
		'/notebook/1',
		data=json.dumps({'name': 'Edited Notebook'}),
		content_type='application/json',
	)
	response = app.test_client().get(
		'/notebook/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{'name': 'Edited Notebook', 'nbid': 1, 'notes': []}
	]

def test_notebook_edit_one_missing_notebook_response():
	response = clear_db_and_add_notebook()

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1}
	]

	response = app.test_client().put(
		'/notebook/3',
		data=json.dumps({'name': 'Edited Notebook'}),
		content_type='application/json',
	)

	assert response.status_code == 204

def test_notebook_edit_one_missing_notebook_response():
	response = clear_db_and_add_notebook()

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1}
	]

	response = app.test_client().put(
		'/notebook/1',
		data=json.dumps({}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notebook_delete_one():
	clear_db_and_add_notebook

	response = app.test_client().get(
		'/notebook/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1, 'notes': []}
	]

	app.test_client().delete(
		'/notebook/1',
		content_type='application/json',
	)
	response = app.test_client().get(
		'/notebook',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == []

@freeze_time('2019-01-02 03:04:05')
def test_notebook_delete_one_also_deletes_corresponding_notes():
	clear_db_and_add_notebook_and_note()
	response = app.test_client().get(
		'/notebook/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1, 'notes': [
			{
				'title' : 'Note 1',
				'nbid': 1,
				'nid': 1,
				'body': 'So Many Things',
				'tags': ['good', 'better'],
				'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
				'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
			}
		]}
	]

	app.test_client().delete(
		'/notebook/1',
		data=json.dumps({'name': 'Edited Notebook'}),
		content_type='application/json',
	)
	response = app.test_client().get(
		'/notebook',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == []

	response = app.test_client().get(
		'/note',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == []

def test_notebook_delete_one_missing_notebook_response():
	response = clear_db_and_add_notebook()

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{'name': 'Notebook 1', 'nbid': 1}
	]

	response = app.test_client().delete(
		'/notebook/2',
		data=json.dumps({'name': 'Edited Notebook'}),
		content_type='application/json',
	)

	assert response.status_code == 204

@freeze_time('2019-01-02 03:04:05')
def test_note_post():
	response = clear_db_and_add_notebook_and_note()

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{
			'title' : 'Note 1',
			'nbid': 1,
			'nid': 1,
			'body': 'So Many Things',
			'tags': ['good', 'better'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
		}
	]

def test_notes_can_not_post_to_missing_notebooks():
	clear_db_and_add_notebook()

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 2,
			'body': 'Even More Things',
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notes_can_not_post_without_title():
	clear_db_and_add_notebook()

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notes_can_not_post_with_invalid_body():
	clear_db_and_add_notebook()

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 1,
			'body': 5,
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notes_can_not_post_with_invalid_tags():
	clear_db_and_add_notebook()

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 1,
			'body': 'Even More Things',
			'tags': 'banana'
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_notes_can_not_post_with_invalid_nbid():
	clear_db_and_add_notebook()

	response = app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 'nbid',
			'body': 'Even More Things',
			'tags': []
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

@freeze_time('2019-01-02 03:04:05')
def test_note_get_all():
	clear_db_and_add_notebook_and_note()

	app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)

	response = app.test_client().get(
		'/note',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{
			'title' : 'Note 1',
			'nbid': 1,
			'nid': 1,
			'body': 'So Many Things',
			'tags': ['good', 'better'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
		},
		{
			'title' : 'Note 2',
			'nid': 2,
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'

		}
	]

@freeze_time('2019-01-02 03:04:05')
def test_note_get_one():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().get(
		'/note/1',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{
			'title' : 'Note 1',
			'nbid': 1,
			'nid': 1,
			'body': 'So Many Things',
			'tags': ['good', 'better'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
		}
	]

def test_note_can_not_get_one_with_missing():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().get(
		'/note/2',
		content_type='application/json',
	)

	assert response.status_code == 204

def test_note_edit_one():
	response = clear_db_and_add_notebook_and_note()

	original_data = json.loads(response.get_data(as_text=True))

	time.sleep(1)

	app.test_client().put(
		'/note/1',
		data=json.dumps({
			'title' : 'Note 2',
			'body': 'Even More Things',
			'tags': ['better', 'best'],
		}),
		content_type='application/json',
	)
	response = app.test_client().get(
		'/note/1',
		content_type='application/json',
	)

	edited_data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200


	assert edited_data['result'][0]['title'] == 'Note 2'
	assert edited_data['result'][0]['body'] == 'Even More Things'
	assert edited_data['result'][0]['tags'] == ['better', 'best']
	assert edited_data['result'][0]['lastModified'] != original_data['result'][0]['lastModified']

def test_note_can_not_edit_one_if_note_is_missing():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().put(
		'/note/2',
		data=json.dumps({
			'title' : 'Note 2',
			'body': 'Even More Things',
			'tags': ['better', 'best'],
		}),
		content_type='application/json',
	)

	assert response.status_code == 204

def test_note_can_not_edit_one_if_title_is_invalid():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().put(
		'/note/1',
		data=json.dumps({
			'title' : 5,
			'body': 'Even More Things',
			'tags': ['better', 'best'],
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_note_can_not_edit_one_if_body_is_invalid():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().put(
		'/note/1',
		data=json.dumps({
			'title' : 'Note 2',
			'body': 5,
			'tags': ['better', 'best'],
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

def test_note_can_not_edit_one_if_tags_is_invalid():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().put(
		'/note/1',
		data=json.dumps({
			'title' : 'Note 2',
			'body': 'Even More Things',
			'tags': 5,
		}),
		content_type='application/json',
	)

	assert response.status_code == 400

@freeze_time('2019-01-02 03:04:05')
def test_note_delete_one():
	clear_db_and_add_notebook_and_note()

	app.test_client().post(
		'/note',
		data=json.dumps({
			'title' : 'Note 2',
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best']
		}),
		content_type='application/json',
	)

	response = app.test_client().get(
		'/note',
		content_type='application/json'
	)

	data = json.loads(response.get_data(as_text=True))

	assert data['result'] == [
		{
			'title' : 'Note 1',
			'nbid': 1,
			'nid': 1,
			'body': 'So Many Things',
			'tags': ['good', 'better'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'
		},
		{
			'title' : 'Note 2',
			'nid': 2,
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'

		}
	]

	app.test_client().delete(
		'/note/1',
		content_type='application/json',
	)
	response = app.test_client().get(
		'/note',
		content_type='application/json',
	)

	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert data['result'] == [
		{
			'title' : 'Note 2',
			'nid': 2,
			'nbid': 1,
			'body': 'Even More Things',
			'tags': ['better', 'best'],
			'created': 'Wed, 02 Jan 2019 03:04:05 GMT', 
			'lastModified': 'Wed, 02 Jan 2019 03:04:05 GMT'

		}
	]

def test_note_delete_one_fails_if_note_is_missing():
	clear_db_and_add_notebook_and_note()

	response = app.test_client().delete(
		'/note/2',
		content_type='application/json',
	)

	assert response.status_code == 204

