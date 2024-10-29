from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/projet_python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'  # Clé secrète pour les sessions

# Initialisation des extensions
db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app, db)

# Modèle de données
class Tache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.mot_de_passe = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.mot_de_passe, password)

# Routes et logique de l'application Flask

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/taches')
def taches():
    taches = Tache.query.all()
    return render_template('taches.html', taches=taches)

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter_tache():
    if request.method == 'POST':
        titre = request.form.get('titre')
        description = request.form.get('description')
        date = request.form.get('date')
        nouvelle_tache = Tache(titre=titre, description=description, date=date)
        db.session.add(nouvelle_tache)
        db.session.commit()
        return redirect(url_for('taches'))
    return render_template('ajouter.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_tache(id):
    tache = Tache.query.get_or_404(id)
    if request.method == 'POST':
        tache.titre = request.form.get('titre')
        tache.description = request.form.get('description')
        tache.date = request.form.get('date')
        db.session.commit()
        return redirect(url_for('taches'))
    return render_template('modifier.html', tache=tache)

@app.route('/supprimer/<int:id>', methods=['POST'])
def supprimer_tache(id):
    tache = Tache.query.get_or_404(id)
    db.session.delete(tache)
    db.session.commit()
    return redirect(url_for('taches'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nom_utilisateur = request.form.get('nom_utilisateur')
        mot_de_passe = request.form.get('mot_de_passe')
        utilisateur = Utilisateur.query.filter_by(nom_utilisateur=nom_utilisateur).first()
        if utilisateur and utilisateur.check_password(mot_de_passe):
            session['utilisateur_id'] = utilisateur.id
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom_utilisateur = request.form.get('nom_utilisateur')
        mot_de_passe = request.form.get('mot_de_passe')
        confirmer_mot_de_passe = request.form.get('confirmer_mot_de_passe')

        if mot_de_passe != confirmer_mot_de_passe:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('register'))

        # Vérifiez si le nom d'utilisateur existe déjà
        if Utilisateur.query.filter_by(nom_utilisateur=nom_utilisateur).first():
            flash('Nom d\'utilisateur déjà pris.', 'danger')
            return redirect(url_for('register'))

        # Créez un nouvel utilisateur
        nouvel_utilisateur = Utilisateur(nom_utilisateur=nom_utilisateur)
        nouvel_utilisateur.set_password(mot_de_passe)
        db.session.add(nouvel_utilisateur)
        db.session.commit()

        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))

    return render_template('registre.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Ajoutez des utilisateurs pour le test si aucun utilisateur n'existe
        if not Utilisateur.query.first():
            admin = Utilisateur(nom_utilisateur='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
