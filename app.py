from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gescol.db'
app.config['SECRET_KEY'] = 'your_secret_key_here' # CHANGE THIS IN PRODUCTION!
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Vue de connexion pour Flask-Login

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Classe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.String(7), unique=True, nullable=False)
    niveau = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    num_labo = db.Column(db.Integer)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='classes')

class Eleve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    num_ordre = db.Column(db.String(10), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    notes = db.relationship('Note', backref='eleve', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valeur = db.Column(db.Float, nullable=False)
    type_note = db.Column(db.String(10), nullable=False) # DC, DS, NCC
    trimestre = db.Column(db.Integer, nullable=False) # 1, 2, 3
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleve.id'), nullable=False)

# Fonctions Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes d'authentification
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ce nom d'utilisateur existe déjà. Veuillez en choisir un autre.", 'danger')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

# Routes existantes, maintenant protégées
@app.route('/')
def index():
    now = datetime.datetime.now()
    return render_template('index.html', current_time=now.strftime("%H:%M:%S"), current_date=now.strftime("%d/%m/%Y"))

@app.route('/classes', methods=['GET', 'POST'])
@login_required
def gerer_classes():
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        niveau = request.form['niveau']
        section = request.form['section']
        num_labo = request.form.get('num_labo')
        
        existing_classe = Classe.query.filter_by(identifiant=identifiant, user_id=current_user.id).first()
        if existing_classe:
            flash('Une classe avec cet identifiant existe déjà.', 'danger')
        else:
            nouvelle_classe = Classe(identifiant=identifiant, niveau=niveau, section=section, num_labo=num_labo, user_id=current_user.id)
            db.session.add(nouvelle_classe)
            db.session.commit()
            flash('Classe ajoutée avec succès !', 'success')
        return redirect(url_for('gerer_classes'))
    classes = Classe.query.filter_by(user_id=current_user.id).all()
    return render_template('classes.html', classes=classes)

@app.route('/classes/modifier/<int:classe_id>', methods=['GET', 'POST'])
@login_required
def modifier_classe(classe_id):
    classe = Classe.query.filter_by(id=classe_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        classe.identifiant = request.form['identifiant']
        classe.niveau = request.form['niveau']
        classe.section = request.form['section']
        classe.num_labo = request.form.get('num_labo')
        db.session.commit()
        flash('Classe modifiée avec succès !', 'success')
        return redirect(url_for('gerer_classes'))
    return render_template('modifier_classe.html', classe=classe)

@app.route('/classes/supprimer/<int:classe_id>', methods=['POST'])
@login_required
def supprimer_classe(classe_id):
    classe = Classe.query.filter_by(id=classe_id, user_id=current_user.id).first_or_404()
    # Supprimer d'abord les élèves de cette classe
    Eleve.query.filter_by(classe_id=classe.id).delete()
    db.session.delete(classe)
    db.session.commit()
    flash('Classe et tous les élèves associés supprimés avec succès !', 'success')
    return redirect(url_for('gerer_classes'))

@app.route('/eleves', methods=['GET', 'POST'])
@login_required
def gerer_eleves():
    classes = Classe.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        num_ordre = request.form['num_ordre']
        classe_id = request.form['classe_id']

        # Security check
        classe = Classe.query.filter_by(id=classe_id, user_id=current_user.id).first()
        if not classe:
            flash("Classe non valide ou non autorisée.", "danger")
            return redirect(url_for('gerer_eleves'))

        existing_eleve = Eleve.query.filter_by(num_ordre=num_ordre, classe_id=classe_id).first()
        if existing_eleve:
            flash("Un élève avec ce numéro d'ordre existe déjà dans cette classe.", 'danger')
        else:
            nouvel_eleve = Eleve(nom=nom, prenom=prenom, num_ordre=num_ordre, classe_id=classe_id)
            db.session.add(nouvel_eleve)
            db.session.commit()
            flash('Élève ajouté avec succès !', 'success')
        return redirect(url_for('gerer_eleves'))
    
    user_classe_ids = [c.id for c in classes]
    eleves = Eleve.query.filter(Eleve.classe_id.in_(user_classe_ids)).all()
    return render_template('eleves.html', eleves=eleves, classes=classes)

@app.route('/eleves/modifier/<int:eleve_id>', methods=['GET', 'POST'])
@login_required
def modifier_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    # Security check: Make sure the student belongs to a class owned by the user
    if eleve.classe.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('gerer_eleves'))

    classes = Classe.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        # Security check: Make sure the new class is also owned by the user
        new_classe_id = request.form['classe_id']
        new_classe = Classe.query.filter_by(id=new_classe_id, user_id=current_user.id).first()
        if not new_classe:
            flash("Classe non valide ou non autorisée.", "danger")
            return redirect(url_for('gerer_eleves'))

        eleve.nom = request.form['nom']
        eleve.prenom = request.form['prenom']
        eleve.num_ordre = request.form['num_ordre']
        eleve.classe_id = new_classe_id
        db.session.commit()
        flash('Élève modifié avec succès !', 'success')
        return redirect(url_for('gerer_eleves'))
    return render_template('modifier_eleve.html', eleve=eleve, classes=classes)

@app.route('/eleves/supprimer/<int:eleve_id>', methods=['POST'])
@login_required
def supprimer_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    # Security check: Make sure the student belongs to a class owned by the user
    if eleve.classe.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('gerer_eleves'))

    # Supprimer d'abord les notes de cet élève
    Note.query.filter_by(eleve_id=eleve.id).delete()
    db.session.delete(eleve)
    db.session.commit()
    flash('Élève et toutes ses notes supprimés avec succès !', 'success')
    return redirect(url_for('gerer_eleves'))

@app.route('/eleves/<int:eleve_id>/notes', methods=['GET', 'POST'])
@login_required
def details_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    # Security check: Make sure the student belongs to a class owned by the user
    if eleve.classe.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('gerer_eleves'))

    if request.method == 'POST':
        valeur = float(request.form['valeur'])
        type_note = request.form['type_note']
        trimestre = int(request.form['trimestre'])
        nouvelle_note = Note(valeur=valeur, type_note=type_note, trimestre=trimestre, eleve_id=eleve.id)
        db.session.add(nouvelle_note)
        db.session.commit()
        flash('Note ajoutée avec succès !', 'success')
        return redirect(url_for('details_eleve', eleve_id=eleve.id))
    
    notes_par_trimestre = {1: [], 2: [], 3: []}
    for note in eleve.notes:
        notes_par_trimestre[note.trimestre].append(note)

    moyennes = {}
    for t in range(1, 4):
        notes_ds = [n.valeur for n in notes_par_trimestre[t] if n.type_note == 'DS']
        notes_autres = [n.valeur for n in notes_par_trimestre[t] if n.type_note != 'DS']
        
        if notes_ds or notes_autres:
            somme_ponderee = sum(notes_ds) * 2 + sum(notes_autres)
            nombre_notes_ponderees = len(notes_ds) * 2 + len(notes_autres)
            moyennes[t] = round(somme_ponderee / nombre_notes_ponderees, 2) if nombre_notes_ponderees > 0 else 0
        else:
            moyennes[t] = 0
            
    return render_template('details_eleve.html', eleve=eleve, moyennes=moyennes)

@app.route('/notes/modifier/<int:note_id>', methods=['GET', 'POST'])
@login_required
def modifier_note(note_id):
    note = Note.query.get_or_404(note_id)
    # Security check: Make sure the note belongs to a student in a class owned by the user
    if note.eleve.classe.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('gerer_eleves'))

    if request.method == 'POST':
        note.valeur = float(request.form['valeur'])
        note.type_note = request.form['type_note']
        note.trimestre = int(request.form['trimestre'])
        db.session.commit()
        flash('Note modifiée avec succès !', 'success')
        return redirect(url_for('details_eleve', eleve_id=note.eleve_id))
    return render_template('modifier_note.html', note=note)

@app.route('/notes/supprimer/<int:note_id>', methods=['POST'])
@login_required
def supprimer_note(note_id):
    note = Note.query.get_or_404(note_id)
    # Security check: Make sure the note belongs to a student in a class owned by the user
    if note.eleve.classe.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('gerer_eleves'))

    eleve_id = note.eleve_id
    db.session.delete(note)
    db.session.commit()
    flash('Note supprimée avec succès !', 'success')
    return redirect(url_for('details_eleve', eleve_id=eleve_id))

@app.route('/dashboard')
@login_required
def dashboard():
    classes = Classe.query.filter_by(user_id=current_user.id).all()
    total_classes = len(classes)
    
    user_classe_ids = [c.id for c in classes]
    total_eleves = Eleve.query.filter(Eleve.classe_id.in_(user_classe_ids)).count()

    stats_classes = []
    for classe in classes:
        nb_eleves = Eleve.query.filter_by(classe_id=classe.id).count()
        
        moyenne_generale_classe = 0
        eleves_classe = Eleve.query.filter_by(classe_id=classe.id).all()
        
        if eleves_classe:
            somme_moyennes_eleves = 0
            for eleve in eleves_classe:
                notes_eleve = eleve.notes
                
                moyennes_trimestrielles_eleve = {}
                for t in range(1, 4):
                    notes_ds = [n.valeur for n in notes_eleve if n.type_note == 'DS' and n.trimestre == t]
                    notes_autres = [n.valeur for n in notes_eleve if n.type_note != 'DS' and n.trimestre == t]
                    
                    if notes_ds or notes_autres:
                        somme_ponderee = sum(notes_ds) * 2 + sum(notes_autres)
                        nombre_notes_ponderees = len(notes_ds) * 2 + len(notes_autres)
                        moyennes_trimestrielles_eleve[t] = somme_ponderee / nombre_notes_ponderees if nombre_notes_ponderees > 0 else 0
                    else:
                        moyennes_trimestrielles_eleve[t] = 0
                
                # Calculer la moyenne générale de l'élève sur les 3 trimestres
                moyennes_valides = [m for m in moyennes_trimestrielles_eleve.values() if m > 0]
                if moyennes_valides:
                    somme_moyennes_eleves += sum(moyennes_valides) / len(moyennes_valides)
            
            moyenne_generale_classe = round(somme_moyennes_eleves / len(eleves_classe), 2)
            
        stats_classes.append({
            'identifiant': classe.identifiant,
            'niveau': classe.niveau,
            'section': classe.section,
            'nb_eleves': nb_eleves,
            'moyenne_generale': moyenne_generale_classe
        })

    return render_template('dashboard.html', total_classes=total_classes, total_eleves=total_eleves, stats_classes=stats_classes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crée les tables si elles n'existent pas
    app.run(debug=True)
