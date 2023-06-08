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

    return jsonify({'success': "True"})

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


# Vérifier la connexion Android
@app.route('/connexion', methods=['POST'])
def get_android_connexion():
    graph = Database_connect()
    #data = request.get_json()

    email = request.form.get('mail_util')
    password = request.form.get('password')

    print(email, password)

    query = """MATCH (u:Utilisateur {mail_util: $mail, password : $password}) RETURN COUNT(u) AS count"""
    print(query)

    with graph.session() as session:
        result = session.run(query,  mail=email, password=function.encrypt_password(password))
        count = result.single()["count"]

        if count > 0:
            reponse = jsonify({"success": "True"})
        else:
            reponse = jsonify({'success': "False"})

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
    
# SDC - Requete routine
@app.route('/sdc/routine', methods=['POST'])
def sdc_routine():
    graph = Database_connect()
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

# SDC - Requete Inscription Appareil
@app.route('/inscription_appareil', methods=['POST'])
def inscription_appareil():
    graph = Database_connect()
    data = request.get_json()
    #print(data)

    device = data.get("device")
    id_device = data.get("id")
    public_key_device = data.get("public_key")

    query = """MATCH (u: SDC {id_sdc: $idSDC}) RETURN u"""

    with graph.session() as session:
        result = session.run(query, idSDC=id_device)

        #private_key = function.create_private_key()
        #public_key = function.create_public_key(private_key)
        #private_key = function.bytes_private_key(private_key)
        #private_key = function.bytes_public_key(public_key)

        private_key = "xxx"
        public_key = "xxx"

        cur_date = function.get_current_date()

        if result.single():
            # Mettre à jour le SDC
            query2 = f"MATCH (n:SDC {{id_sdc: '{id_device}'}}) SET  n.public_key_sdc = '{public_key}', n.private_key_sdc = '{private_key}', n.exp_key_sdc = '{cur_date}' "
            result2 = session.run(query2)
        else :
            # Créer le SDC
            query_max_id = """MATCH (n:SDC) RETURN MAX(toInteger(n.id_sdc)) AS max_id"""
            result_max_id = session.run(query_max_id)
            max_id = result_max_id.single()["max_id"]
            if max_id is None :
                max_id = 0
            new_id = max_id + 1
            id_device = new_id
            query2 = f"CREATE (p:SDC {{id_sdc: '{id_device}', public_key_sdc: '{public_key}', private_key_sdc: '{private_key}', exp_key_sdc: '{cur_date}'}})"
            result2 = session.run(query2)
    graph.close()
    return jsonify({'succes': True, 'id': id_device, 'session_key': public_key})





if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)