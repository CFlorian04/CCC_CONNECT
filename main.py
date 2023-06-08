import os
import function
from neo4j import GraphDatabase, basic_auth
from flask import Flask, app, jsonify, request

graph = GraphDatabase.driver("bolt://44.193.205.141:7687",auth=basic_auth("neo4j", "oscillator-runs-voids"))
app = Flask(__name__)

# recuperer un utilisateur par son id
@app.route('/api/utilisateur', methods=['GET'])
def get_utilisateur():
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
@app.route('/api/utilisateur', methods=['POST'])
def create_utilisateur():
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


# Android - Connexion
@app.route('/api/connexion', methods=['POST'])
def get_android_connexion():
    data = request.get_json()
    print(data)

    mail = data.get('mail')
    password = data.get('password')

    query = f"MATCH (u) WHERE u.mail = {mail} RETURN u"
    print(query)

    with graph.session() as session:
        result = session.run(query)

    return jsonify({'test': True})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)