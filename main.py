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
    query = f"MATCH (u : Utilisateur) WHERE u.id_util = {id} RETURN u"

    with graph.session() as session:
        result = session.run(query)
        
        for record in result:
            utilisateur = {}

            for key in record["u"].keys():
                utilisateur[key] = record["u"][key]
                
            return jsonify({'utilisateur': utilisateur})
          

# creation d'un utilisateur - inscription
@app.route('/utilisateur', methods=['POST'])
def create_utilisateur():
    graph = Database_connect()
 
    id_util = request.form.get('id_util')
    nom_util = request.form.get('nom_util')
    prenom_util = request.form.get('prenom_util')
    mail_util = request.form.get('mail_util')
    password = request.form.get('password')

    with graph.session() as session:
        query = f"CREATE (p:Utilisateur {{id_util: '{id_util}', nom_util: '{nom_util}', prenom_util: '{prenom_util}', mail_util: '{mail_util}', password: '{function.encrypt_password(password)}'}})"
        result = session.run(query)

    return jsonify({'success': "True"})

   
# recuperer les infos d'un composant par son id
@app.route('/object', methods=['GET'])
def get_object():    
    graph = Database_connect()
    id = request.args.get('id', default = 1, type = int)

    query = f"MATCH (u:Objet) WHERE u.id_obj = {id} RETURN u"
    with graph.session() as session:
        result = session.run(query)

        for record in result:
            composant = {}
 
            for key in record["u"].keys():
                composant[key] = record["u"][key]

        return jsonify({'composant': composant})

#connexion via l'application android
@app.route('/connexion', methods=['POST'])
def get_android_connexion():
    graph = Database_connect()
    data = request.get_json()

    # email = request.form.get('mail_util')
    # password = request.form.get('password')

    email = data.get('mail_util')
    password = data.get('password')

    query = """MATCH (u:Utilisateur {mail_util: $mail, password : $password}) RETURN COUNT(u) AS count"""

    with graph.session() as session:
        result = session.run(query,  mail=email, password=password)
        count = result.single()["count"]

        if count > 0:
            reponse = jsonify({"response": "True"})
        else:
            reponse = jsonify({'response': "False"})

    graph.close()
    return reponse

# recuperer la liste des objets IoT
@app.route('/objects', methods=['GET'])
def get_objects():
    graph = Database_connect()
    query = f"MATCH (u) RETURN *"

    with graph.session() as session:
        result = session.run(query)
        objects = []

        for record in result:
            obj = record["u"]
            obj_dict = dict(obj)
            objects.append(obj_dict)

        return jsonify({'objects': objects})

# SDC - Requete routine
@app.route('/sdc/routine', methods=['POST'])
def sdc_routine():
    graph = function.Database_connect()
    data = request.get_json()
    #print(data)

    composants = data.get('composants')

    if composants:
        # Parcourir les composants
        for composant in composants:
            c_idObjet = composant.get("idObjet")
            c_libelleObjet = composant.get("libelleObjet")
            c_date_comp = composant.get("lastConnect")
            c_fonctions = composant.get("fonctions")

            # Regarder si l'objet existe
            query = """MATCH (u: Objet {id_obj: $idObjet}) RETURN u"""

            with graph.session() as session:
                result = session.run(query, idObjet=c_idObjet)

                if result.single():
                    # Mettre à jour l'objet existant
                    query2 = """MATCH (n:Objet {id_obj: $idObjet}) SET """

                    set_clause = f"n.lib_obj = '{c_libelleObjet}', n.date_lc_obj = '{c_date_comp}',"
                    for fonction in c_fonctions:
                        set_clause += f"n.{fonction.get('libelle')} = '{json.dumps(fonction)}', "
                    set_clause = set_clause.rstrip(", ")
                    query2 += set_clause

                    result2 = session.run(query2, idObjet=c_idObjet)

                    #Mettre l'historisation - Modification Objet ?

                elif c_idObjet == 0:
                    # Créer un nouvel objet
                    query_max_id = """MATCH (n:Objet) RETURN MAX(toInteger(n.id_obj)) AS max_id"""
                    result_max_id = session.run(query_max_id)
                    max_id = result_max_id.single()["max_id"]
                    new_id = max_id + 1

                    query2 = """CREATE (n:Objet {id_obj: $idObjet}) SET """

                    set_clause = f"n.id_obj = '{new_id}', n.lib_obj = '{c_libelleObjet}', n.date_lc_obj = '{c_date_comp}',"
                    for fonction in c_fonctions:
                        set_clause += f"n.{fonction.get('libelle')} = '{json.dumps(fonction)}', "
                    set_clause = set_clause.rstrip(", ")
                    query2 += set_clause

                    result2 = session.run(query2, idObjet=c_idObjet)

                    #Mettre l'historisation - Ajout objet ?

    graph.close()
    return jsonify({'succes': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='192.168.1.78', port=port)