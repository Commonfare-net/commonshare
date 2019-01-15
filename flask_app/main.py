from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'
    
@app.route('/user/<id>/')
def user_profile(id):
    return "Profile page of user #{}".format(id)
    
if __name__ == "__main__":
    app.run()