from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import contact_pb2
import RWDict

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# Helper method to convert a string to a Contact Type
def stringToContactType(string):
    return {
        'SPEAKER' : contact_pb2.Contact.SPEAKER,
        'VOLUNTEER' : contact_pb2.Contact.VOLUNTEER,
        'ATTENDANT' : contact_pb2.Contact.ATTENDANT
    }[string]

# Get current user - treat this as an RWDevCon Attendee using an app
@app.route("/currentUser")
def getCurrentUser():
    contact = contact_pb2.Contact()
    contact.first_name = "Vincent"
    contact.last_name = "Ngo"
    contact.twitter_name = "@vincentngo2"
    contact.email = "vincent@mail.com"
    contact.github_link = "github.com/vincentngo"
    contact.type = contact_pb2.Contact.ATTENDANT
    contact.imageName = "vincentngo.png"
    str = contact.SerializeToString()

    return str

# Get Speakers speaking at the conference. Loop through the predefinied array of contact 
# dictionary, and create a Contact object, adding it to an array and serializing our Speakers object.
@app.route("/speakers")
def getSpeakers():
    contacts = []
    for contactDict in RWDict.speakers:
        contact = contact_pb2.Contact()
        contact.first_name = contactDict['first_name']
        contact.last_name = contactDict['last_name']
        contact.twitter_name = contactDict['twitter_name']
        contact.email = contactDict['email']
        contact.github_link = contactDict['github_link']
        contact.type = stringToContactType(contactDict['type'])
        contact.imageName = contactDict['imageName']
        contacts.append(contact)
    speakers = contact_pb2.Speakers()
    speakers.contacts.extend(contacts)
    return speakers.SerializeToString()

@app.route('/')
def index():
    return "Hello, World!"


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


if __name__ == "__main__":
    app.run()
