# NeverNote

## To run this app locally, start mongodb with 

`sudo service mongod start`

### Create a virtual environment and run

`pip install -r requirements.txt`

### Start the app

`python app.py`

### Now the app can be accessed at http://localhost:5000

## To run this app in a docker container

`sudo docker-compose build`

`sudo docker-compose up`

# Routes

## POST and GET notes
`/note`
### POST body format
`{'title': <string:title>, 'nbid': <int:notebook_id>, 'body': <string:note_body>, tags:<list:note_tags>}`

## GET, PUT or DELETE a single note by ID number
`/note/<int:id>`

## POST notebook body
`/notebook`
### POST body format
`{name: <string:notebook_name>}`

## GET, PUT or DELETE a notebook by ID number
`/notebook/<int:id>`

## GET a notebook by ID number and retrieve only the notes with a given tag
`/notebook/<int:id>/<string:tag>`

