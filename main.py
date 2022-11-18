from flask import Flask
from flask_cors import CORS
from app.routes import blueprints

app = Flask(__name__, template_folder="template")
app.config['CORS-HEADERS'] = 'Content-Type'
CORS(app)

for route_blueprint in blueprints:
    app.register_blueprint(route_blueprint)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
