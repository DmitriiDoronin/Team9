# Importing all needed libraries.
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate
from search import find_top_n
import pickle
import numpy as np

# open vectorizer
vectorizer = pickle.load(open('vectorizer.obj', 'rb'))

# Configuration of database and Flask Framework
app = Flask(__name__, template_folder='templates')
app.static_folder = 'static'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
auth = Blueprint('auth', __name__)

migrate=Migrate(app,db)
manager = Manager(app)

# Class which describe recruiter and adding into database
class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    company = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return str(self.id)

# Class which describe resume and adding into database
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=False)
    resume = db.Column(db.String(10000), unique=False, nullable=False)

    def __repr__(self):
        return str(self.id)

# Class returns model with job list and inserting into database
class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(10000), unique=False, nullable=False)
    creator = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return str(self.id)

# The main page function
@app.route('/', methods=['GET'])
def index():
    return render_template('Creative CV1.html')

# Hr page function
@app.route('/login-recruiter', methods=['GET'])
def login_recruiter():
    return render_template('HRIntro.html')

# Signup page function
@app.route('/register', methods=['GET'])
def signup():
    return render_template('sign-up.html')

# HR Page function
@app.route('/profile/<id>', methods=['GET'])
def profile_recruiter(id):
    recruiter = Recruiter.query.filter_by(id=id).first()
    jobs = JobListing.query.filter_by(creator=id)
    return render_template('HRPage.html', name=recruiter.name, company=recruiter.company, jobs=jobs, id=recruiter.id)

# Adding Job page function
@app.route('/add-job/<id>', methods=['GET', 'POST'])
def job(id):
    if request.method == 'GET':
        return render_template('ADDJOB.html', id=id)
    else:
        creator = id
        description = request.form.get('description')

        job_listing = JobListing(description=description, creator=creator)

        db.session.add(job_listing)
        db.session.commit()

        last_joblist = JobListing.query.filter_by(description=description).first()

        if last_joblist:
            return redirect(url_for('results', id=last_joblist.id))

# Results page function
@app.route('/results/<id>', methods=['GET'])
def results(id):
    last_joblist = JobListing.query.filter_by(id=id).first()

    text = last_joblist.description

    records = Resume.query.with_entities(Resume.resume, Resume.name, Resume.email).all()

    records = np.array([list(record) for record in records])

    X = vectorizer.transform(records[:, 0])
    text_vectorized = vectorizer.transform([text]).toarray()[0]

    top_5 = find_top_n(text_vectorized, X)
    print(top_5)
    print(records[top_5, 1])
    print(records[top_5, 2])
    return render_template('results.html', names=records[top_5, 1], email=records[top_5, 2])

# HR signup function
@app.route('/signup-recruiter', methods=['POST', 'GET'])
def signup_recruiter():
    if request.method == 'GET':
        return render_template('HRIntro.html')
    else:
        email = request.form.get('email')
        name = request.form.get('name')
        company = request.form.get('company')
        recruiter = Recruiter.query.filter_by(email=email).first()

        if recruiter:

            id = Recruiter.query.filter_by(email=email).first().id

            return redirect(url_for('profile_recruiter', id=id))

        new_recruiter = Recruiter(email=email, name=name, company=company)

        db.session.add(new_recruiter)
        db.session.commit()
        id = Recruiter.query.filter_by(email=email).first().id
        return redirect(url_for('signup_recruiter', id=id))

# Resume adding function
@app.route('/add-resume', methods=['GET', 'POST'])
def add_resume():
    if request.method == 'GET':
        return render_template('AddResume.html')
    else:
        email = request.form.get('email')
        name = request.form.get('name')
        resume = request.form.get('resume')

        new_resume = Resume(email=email, name=name, resume=resume)

        db.session.add(new_resume)
        db.session.commit()

        return redirect(url_for('index'))

# HR data getting function
@auth.route('/login-recruiter', methods=['POST'])
def login_recruiter():
    name = request.form.get('name')
    email = request.form.get('email')
    company = request.form.get('company')

    recruiter = Recruiter.query.filter_by(email=email).first()

    if not recruiter:
        return redirect(url_for('login_recruiter'))

    return redirect(url_for('profile'))

