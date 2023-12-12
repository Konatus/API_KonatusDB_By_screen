from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'API KONATUS DEV'
app.run(host='0.0.0.0')
