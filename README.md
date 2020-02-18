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

## Post and Get notes
`/note`
### Post body format
`{'title': <string:title>, 'nbid': <int:notebook_id>, 'body': <string:note_body>, tags:<list:note_tags>}`

## Get a single note by ID number
`/note/<int:id>`

## Post notebook body
`/notebook`
### Post body format
`{name: <string:notebook_name>}`

## Get a notebook by ID number
`/notebook/<int:id>`

## Get a notebook by ID number and retrieve only the notes with a given tag
`/notebook/<int:id>/<string:tag>`

