from flask import Flask, request, render_template

## Creating a Flask application instance
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True,)