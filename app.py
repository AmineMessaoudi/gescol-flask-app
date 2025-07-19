from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Configuration de l'application
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gescol.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèles de la base de données
class Classe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.String(7), unique=True, nullable=False)
    niveau = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    num_labo = db.Column(db.Integer)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)

class Eleve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    num_ordre = db.Column(db.String(20), unique=True, nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    notes = db.relationship('Note', backref='eleve', lazy=True, cascade="all, delete-orphan")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valeur = db.Column(db.Float, nullable=False)
    type_note = db.Column(db.String(10), nullable=False) # DC, DS, NCC
    trimestre = db.Column(db.Integer, nullable=False)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleve.id'), nullable=False)

# Création initiale de la base de données
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classes', methods=['GET', 'POST'])
def gerer_classes():
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        niveau = request.form['niveau']
        section = request.form['section']
        num_labo = request.form['num_labo']
        
        nouvelle_classe = Classe(identifiant=identifiant, niveau=niveau, section=section, num_labo=num_labo)
        db.session.add(nouvelle_classe)
        db.session.commit()
        return redirect(url_for('gerer_classes'))
        
    classes = Classe.query.all()
    return render_template('classes.html', classes=classes)

@app.route('/classe/supprimer/<int:classe_id>', methods=['POST'])
def supprimer_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    db.session.delete(classe)
    db.session.commit()
    return redirect(url_for('gerer_classes'))

@app.route('/classe/modifier/<int:classe_id>', methods=['GET', 'POST'])
def modifier_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    if request.method == 'POST':
        classe.identifiant = request.form['identifiant']
        classe.niveau = request.form['niveau']
        classe.section = request.form['section']
        classe.num_labo = request.form['num_labo']
        db.session.commit()
        return redirect(url_for('gerer_classes'))
    return render_template('modifier_classe.html', classe=classe)

@app.route('/eleves', methods=['GET', 'POST'])
def gerer_eleves():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        num_ordre = request.form['num_ordre']
        classe_id = request.form['classe_id']
        
        nouvel_eleve = Eleve(nom=nom, prenom=prenom, num_ordre=num_ordre, classe_id=classe_id)
        db.session.add(nouvel_eleve)
        db.session.commit()
        return redirect(url_for('gerer_eleves'))

    eleves = Eleve.query.all()
    classes = Classe.query.all()
    return render_template('eleves.html', eleves=eleves, classes=classes)

@app.route('/eleve/<int:eleve_id>', methods=['GET', 'POST'])
def details_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    if request.method == 'POST':
        valeur = request.form['valeur']
        type_note = request.form['type_note']
        trimestre = request.form['trimestre']

        nouvelle_note = Note(valeur=valeur, type_note=type_note, trimestre=trimestre, eleve_id=eleve.id)
        db.session.add(nouvelle_note)
        db.session.commit()
        return redirect(url_for('details_eleve', eleve_id=eleve.id))

    # Calcul des moyennes trimestrielles
    moyennes_trimestrielles = {}
    for trimestre_num in [1, 2, 3]:
        notes_trimestre = [note for note in eleve.notes if note.trimestre == trimestre_num]
        total_points = 0
        total_coefficients = 0
        
        for note in notes_trimestre:
            if note.type_note == 'DS':
                total_points += note.valeur * 2
                total_coefficients += 2
            else:
                total_points += note.valeur
                total_coefficients += 1
        
        if total_coefficients > 0:
            moyennes_trimestrielles[trimestre_num] = round(total_points / total_coefficients, 2)
        else:
            moyennes_trimestrielles[trimestre_num] = "N/A"

    return render_template('details_eleve.html', eleve=eleve, moyennes=moyennes_trimestrielles)

@app.route('/note/modifier/<int:note_id>', methods=['GET', 'POST'])
def modifier_note(note_id):
    note = Note.query.get_or_404(note_id)
    if request.method == 'POST':
        note.valeur = request.form['valeur']
        note.type_note = request.form['type_note']
        note.trimestre = request.form['trimestre']
        db.session.commit()
        return redirect(url_for('details_eleve', eleve_id=note.eleve.id))
    return render_template('modifier_note.html', note=note)

@app.route('/note/supprimer/<int:note_id>', methods=['POST'])
def supprimer_note(note_id):
    note = Note.query.get_or_404(note_id)
    eleve_id = note.eleve.id # On garde l'ID de l'élève avant de supprimer la note
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('details_eleve', eleve_id=eleve_id))

@app.route('/dashboard')
def dashboard():
    total_classes = Classe.query.count()
    total_eleves = Eleve.query.count()

    classes = Classe.query.all()
    stats_classes = []
    for classe in classes:
        eleves_classe = Eleve.query.filter_by(classe_id=classe.id).all()
        nb_eleves_classe = len(eleves_classe)
        
        moyenne_generale_classe = "N/A"
        if nb_eleves_classe > 0:
            total_points_classe = 0
            total_coefficients_classe = 0
            for eleve in eleves_classe:
                for note in eleve.notes:
                    if note.type_note == 'DS':
                        total_points_classe += note.valeur * 2
                        total_coefficients_classe += 2
                    else:
                        total_points_classe += note.valeur
                        total_coefficients_classe += 1
            if total_coefficients_classe > 0:
                moyenne_generale_classe = round(total_points_classe / total_coefficients_classe, 2)
            
        stats_classes.append({
            'identifiant': classe.identifiant,
            'niveau': classe.niveau,
            'section': classe.section,
            'nb_eleves': nb_eleves_classe,
            'moyenne_generale': moyenne_generale_classe
        })

    return render_template('dashboard.html',
                           total_classes=total_classes,
                           total_eleves=total_eleves,
                           stats_classes=stats_classes)

@app.route('/eleve/modifier/<int:eleve_id>', methods=['GET', 'POST'])
def modifier_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    if request.method == 'POST':
        eleve.nom = request.form['nom']
        eleve.prenom = request.form['prenom']
        eleve.num_ordre = request.form['num_ordre']
        eleve.classe_id = request.form['classe_id']
        db.session.commit()
        return redirect(url_for('gerer_eleves'))
    
    classes = Classe.query.all()
    return render_template('modifier_eleve.html', eleve=eleve, classes=classes)

@app.route('/eleve/supprimer/<int:eleve_id>', methods=['POST'])
def supprimer_eleve(eleve_id):
    eleve = Eleve.query.get_or_404(eleve_id)
    db.session.delete(eleve)
    db.session.commit()
    return redirect(url_for('gerer_eleves'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)