# Librairie(s) utilisée(s)
from flask import *
import sqlite3
 
# Création d'un objet application web Flask
app = Flask(__name__, static_url_path='/static')

# Fonctions utilisées pour appeler des commandes SQL
def lire_base():
    """ Récupére des questions dans la table
        Renvoie (list of tuples) : liste des questions
    """
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    SELECT * FROM Quiz
    ORDER BY ID"""
    resultat = curseur.execute(requete_sql)
    qcm = resultat.fetchall()
    connexion.close()
    return qcm


def ajoute_enregistrement(donnees):
    """ Créé l'enregistrement avec le nouvel id et les données saisies
        Renvoie un booléen : True si l'ajout a bien fonctionné
    """
    # Test si tous les champs sont renseignés
    parametre0 = donnees['ID']
    parametre1 = donnees['Réponse']
    if parametre0 == "" or parametre1 == "":
        return False
    parametres = (parametre0, parametre1)
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    INSERT INTO Proposition VALUES (?,?);"""
    resultat = curseur.execute(requete_sql, parametres)
    connexion.commit()
    connexion.close()
    return True


def reponse_sql():
    """ Compare deux éléments de différentes tables et renvoie la liste de catégories qui y correspond
    """
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    SELECT Catégorie FROM Quiz as q
    JOIN Proposition as p ON p.ID=q.ID
    WHERE p.ID=q.ID AND p.Réponse=q.Réponse"""
    resultat = curseur.execute(requete_sql)
    bilan = resultat.fetchall()
    connexion.close()
    return bilan


def points_sql(donnees):
    """ Recherche au moins une des informations comprise dans le dictionnaire donnees
        Si un élément est nul, alors le paramètre de la recherche est vide
        Sinon, il est de la forme: '%'+element+'%' pour le paramètre Question
        Pour la catégorie de questions, la recherche est précise vis à vis des informations.
    """
    parametre0, parametre1 = "",""
    if donnees["Question"] !="":
        parametre0 = '%'+donnees["Question"]+'%'
    if donnees["Catégorie"] !="":
        parametre1 = donnees["Catégorie"]
    parametres = (parametre0,parametre1)
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    SELECT *
    FROM Quiz WHERE Question LIKE ? OR Catégorie LIKE ?;"""
    resultat = curseur.execute(requete_sql, parametres)
    bilan = resultat.fetchall()
    connexion.close()
    return bilan

def delete_sql():
    """ Supprime la table Proposition
    """
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    DROP TABLE Proposition;
    """
    resultat = curseur.execute(requete_sql)
    connexion.commit()
    connexion.close()
    return True

def create_sql():
    """Crée une table Proposition
    """
    connexion = sqlite3.connect("bdd/Quiz.db")
    curseur = connexion.cursor()
    requete_sql = """
    CREATE TABLE "Proposition" (
    "ID"    INTEGER,
    "Réponse"    TEXT,
    PRIMARY KEY("ID")
    ); """
    resultat = curseur.execute(requete_sql)
    connexion.commit()
    connexion.close()
    return True

def score_svt(condition):
    """ Prend en paramètre une condition
        Renvoie un score si celle-ci est True
    """
    score=0
    for reponse in condition:
        if reponse[0]=="SVT":
            score+=20
    return score

def score_maths(condition):
    """ Prend en paramètre une condition
        Renvoie un score si celle-ci est True
    """
    score=0
    for reponse in condition:
        if reponse[0]=="MATHS":
            score+=20
    return score

def score_culture(condition):
    """ Prend en paramètre une condition
        Renvoie un score si celle-ci est True
    """
    score=0
    for reponse in condition:
        if reponse[0]=="CULTURE":
            score+=20
    return score

def score_musique(condition):
    """ Prend en paramètre une condition
        Renvoie un score si celle-ci est True
    """
    score=0
    for reponse in condition:
        if reponse[0]=="MUSIQUE":
            score+=20
    return score

def score_espagnol(condition):
    """ Prend en paramètre une condition
        Renvoie un score si celle-ci est True
    """
    score=0
    for reponse in condition:
        if reponse[0]=="ESPAGNOL":
            score+=20
    return score


def moyenne_sql(lst):
    """ Prend en compte une liste non vide et prend chaque élément de celle-ci 
        Renvoie une moyenne de ces valeurs
    """
    compteur=0
    for score in lst:
        compteur+=score
    moyenne=compteur/len(lst)
    return moyenne


# Création d'une fonction accueillir() associee a l'URL "/"
# pour générer une page web dynamique
@app.route("/")
def accueillir():
    """Présentation du site"""
    return render_template("bonjour.html")

# Page utilisant une base de données
@app.route("/questions")
def quiz():
    questions=lire_base()
    return render_template("questionnaire.html", questions=questions)

@app.route("/corrigé", methods = ['POST'])
def corrigé():
    result = request.form # Récupération des informations en provenance du POST: C'est un dictionnaire
    liste_qcm = points_sql(result)
    return render_template("corrigé.html", questions=liste_qcm)

@app.route("/gg")
def super_combat():
    delete_sql() 
    create_sql()
    return render_template("gg.html")


@app.route("/resultats", methods = ['POST'])
def bilan():
    result = request.form # Récupération des informations en provenance du POST: C'est un dictionnaire
    test = reponse_sql()
    ajoute_enregistrement(result)  # Créé l'enregistrement avec le nouvel id et les données saisies.

    liste_scores=[]
    svt = score_svt(test)
    maths = score_maths(test)
    cultures = score_culture(test)
    musiques = score_musique(test)
    espagnol = score_espagnol(test)
        
    liste_scores.append(svt)
    liste_scores.append(maths)
    liste_scores.append(cultures)
    liste_scores.append(musiques)
    liste_scores.append(espagnol)
    moyenneG = moyenne_sql(liste_scores)
    return render_template("resultats.html", score=liste_scores,moyenne=moyenneG)

# Lancement de l'application web et son serveur
# accessible à l'URL : http://127.0.0.1:1664/
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1664, debug=True)

