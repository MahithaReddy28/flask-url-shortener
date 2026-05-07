from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

# Function to generate random short code
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None

    if request.method == 'POST':

        original_url = request.form['url']

        code = generate_code()

        # Ensure unique code
        while URL.query.filter_by(short_code=code).first():
            code = generate_code()

        new_url = URL(
            original_url=original_url,
            short_code=code
        )

        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + code

    return render_template(
        'index.html',
        short_url=short_url
    )

# Redirect route
@app.route('/<short_code>')
def redirect_url(short_code):

    url = URL.query.filter_by(short_code=short_code).first()

    if url:
        return redirect(url.original_url)

    return "URL not found"

# Create database
with app.app_context():
    db.create_all()

# Run server
if __name__ == '__main__':
    app.run(debug=True)