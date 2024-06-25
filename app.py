from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
swagger = Swagger(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()

    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }

@app.route('/users', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'A list of users',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'age': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def home():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The user ID'
        }
    ],
    'responses': {
        200: {
            'description': 'A user object',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                },
                'required': ['id', 'name', 'age']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                }
            }
        }
    }
})
def create_user():
    user = User(id=request.json['id'], name=request.json['name'], age=request.json['age'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route('/users/<int:id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The user ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                },
                'required': ['name', 'age']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def update_user(id):
    user = User.query.get(id)
    if user:
        user.name = request.json['name']
        user.age = request.json['age']
        db.session.commit()
        return jsonify(user.to_dict())
    return jsonify({"error": "User not found"}), 404

@app.route('/users/<int:id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The user ID'
        }
    ],
    'responses': {
        200: {
            'description': 'User deleted'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['DELETE'])
@swag_from({
    'responses': {
        200: {
            'description': 'All users deleted'
        }
    }
})
def delete_all_users():
    users = User.query.all()
    for user in users:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "All users deleted"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
