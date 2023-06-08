import os
import function
import json
from neo4j import GraphDatabase, basic_auth
from flask import Flask, app, jsonify, request

app = Flask(__name__)


def Database_connect():
    return GraphDatabase.driver("bolt://44.193.205.141:7687",auth=basic_auth("neo4j", "oscillator-runs-voids"))

# Test
@app.route('/')
def test():
    return "Server Ok"


# recuperer un utilisateur par son id
@app.route('/utilisateur', methods=['GET'])
def get_utilisateur():
    graph = Database_connect()
    id = request.args.get('id', default = 1, type = int)
    print(id)
    query = f"MATCH (u) WHERE u.id_util = {id} RETURN u"
    print(query)
    with graph.session() as session:
        result = session.run(query)
        
        for record in result:
            utilisateur = {}
            # print(record["u"].keys())

            for key in record["u"].keys():
                print(key)
                utilisateur[key] = record["u"][key]
                
            print(utilisateur)
            return jsonify({'utilisateur': utilisateur})
          

# creation d'un utilisateur
@app.route('/utilisateur', methods=['POST'])
def create_utilisateur():
    graph = Database_connect()
    print("in post")
    data = request.get_json()
    print(data)

    id_util = data.get('id_util')
    nom_util = data.get('nom_util')
    prenom_util = data.get('prenom_util')
    mail_util = data.get('mail_util')
    password = data.get('password')

    
    with graph.session() as session:
        query = f"CREATE (p:Utilisateur {{id_util: {id_util}, nom_util: '{nom_util}', prenom_util: '{prenom_util}', mail_util: '{mail_util}', password: '{function.encrypt_password(password)}'}})"
        result = session.run(query)

    return jsonify({'succes': True})

# recuperer la liste des objets IoT
@app.route('/api/objets', methods=['GET'])
def get_objets():
    graph = Database_connect()
    query = f"MATCH (u:Object) RETURN *"
    print(query)
    with graph.session() as session:
        result = session.run(query)

        for record in result:
            objets = {}

            for key in record["u"].keys():
                print(key)
                objets[key] = record["u"][key]

        return jsonify({'objets': objets})

# recuperer les infos d'un composant par son id
@app.route('/api/objet', methods=['GET'])
def get_objet():
    graph = Database_connect()
    id = request.args.get('id', default = 1, type = int)
    query = f"MATCH (u:Objet) WHERE u.id_obj = {id} RETURN u"
    with graph.session() as session:
        result = session.run(query)

        for record in result:
            composant = {}

            for key in record["u"].keys():
                composant[key] = record["u"][key]

            print(composant)
            return jsonify({'composant': composant})


# Android - Connexion
@app.route('/connexion', methods=['POST'])
def get_android_connexion():
    graph = Database_connect()
    data = request.get_json()
    print(data)

    mail = data.get('mail')
    password = data.get('password')

    query = """MATCH (u: Utilisateur {mail_util: $mail, password : $password}) RETURN u.id_util as user_id"""
    print(query)

    with graph.session() as session:
        result = session.run(query, mail=mail, password= function.encrypt_password(password))
        if result.single():
            reponse = jsonify({'succes': True})
        else:
            reponse = jsonify({'succes': False})

    graph.close()
    return reponse

# SDC - Ajout d'un objet
@app.route('/sdc/ajout', methods=['POST'])
def sdc_ajout():
    graph = Database_connect()
    data = request.get_json()
    #print(data)

    
    #query = """MATCH (u: Utilisateur {mail_util: $mail, password : $password}) RETURN u.id_util as user_id"""
    #print(query)

    #with graph.session() as session:
    #    result = session.run(query, mail=mail, password= function.encrypt_password(password))
    #    if result.single():
    #        reponse = jsonify({'succes': True})
    #    else:
    #        reponse = jsonify({'succes': False})

    graph.close()
    return "reponse"

# SDC - Requete routine
@app.route('/sdc/routine', methods=['POST'])
def sdc_routine():
    graph = Database_connect()
    data = request.get_json()
    print(data)

    composants = data.get('composants')
    
    if composants:
        for composant in composants :
            c_idObjet = composant.get("idObjet")
            c_libelleObjet = composant.get("libelleObjet")
            c_date_comp = composant.get("lastConnect")
            c_fonctions = composant.get("fonction")
            print(str(c_idObjet) + "/" + c_libelleObjet + "/" + c_date_comp)

            query = """MATCH (u: Objet {id_obj: $idObjet}) RETURN u"""

            with graph.session() as session:
                result = session.run(query, idObjet=c_idObjet)
                if result.single():
                    query2 = """MATCH (n:Objet {id_obj: $idObjet}) SET """
                    set_clause = ''
                    for fonction in c_fonctions :
                        set_clause += f"n.{fonction.get('libelle')} = '{json.dumps(fonction)}', "
                    set_clause = set_clause.rstrip(", ")
                    query2 += set_clause
                    print(query2)
                    result2 = session.run(query2, idObjet=c_idObjet)
    graph.close()
    return jsonify({'succes': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)