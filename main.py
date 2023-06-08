import os
import function
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
    query = f"MATCH (u : Utilisateur) WHERE u.id_util = {id} RETURN u"
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
    # data = request.get_json()
    # print(data)

    id_util = request.form.get('id_util')
    nom_util = request.form.get('nom_util')
    prenom_util = request.form.get('prenom_util')
    mail_util = request.form.get('mail_util')
    password = request.form.get('password')

    
    with graph.session() as session:
        query = f"CREATE (p:Utilisateur {{id_util: '{id_util}', nom_util: '{nom_util}', prenom_util: '{prenom_util}', mail_util: '{mail_util}', password: '{function.encrypt_password(password)}'}})"
        result = session.run(query)

    return jsonify({'succes': True})


# Android - Connexion
@app.route('/connexion', methods=['POST'])
def get_android_connexion():
    graph = Database_connect()
    data = request.get_json()
    print(data)

    mail = data.get('mail')
    password = data.get('password')

    query = """MATCH (u:Utilisateur {mail_util: $mail, password : $password}) RETURN u.id_util as user_id"""
    print(query)

    with graph.session() as session:
        result = session.run(query, mail=mail, password= function.encrypt_password(password))
        if result.single():
            reponse = jsonify({'succes': True})
        else:
            reponse = jsonify({'succes': False})

    graph.close()
    return reponse


# recuperer la liste des objets IoT
@app.route('/objects', methods=['GET'])
def get_objects():
    graph = Database_connect()
    query = f"MATCH (u) RETURN *"
    print(query)
    with graph.session() as session:
        result = session.run(query)

        for record in result:
            objects = {}
            # print(record["u"].keys())

            for key in record["u"].keys():
                print(key)
                objects[key] = record["u"][key]

        return jsonify({'objects': objects})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)