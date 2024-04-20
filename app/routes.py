from app import app

@app.route('/')
@app.route('/index')
def index():
    '''Define the view function for the index page'''
    return "Hello, World!"