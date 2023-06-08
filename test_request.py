import requests

#path = 'https://floriancodebecq.pythonanywhere.com/api'
# path = 'https://floriancodebecq.pythonanywhere.com/api'
path = 'http://192.168.0.45:5000/'
url = path + 'sdc/routine'

# myobj = { "id_util": "110", "mail_util": "codebecq.florian@gmail.com", "nom_util": "Codebecq", "password": "florian", "prenom_util": "Florian" }
#myobj = {"mail": "codebe.florian@gmail.com", "password": "florian"}
# myobj = {"mail": "codebe.florian@gmail.com", "password": "florian"}

myobj = {
   "composants":[
      {
         "idObjet":1,
         "libelleObjet":"lampe",
         "lastConnect":"27/12/2022 10:09:20",
         "fonctions":[
            {
               "idFonction":"1",
               "libelle":"power",
               "type":"switch",
               "data":[
                  "1"
               ]
            },
            {
               "idFonction":"2",
               "libelle":"color",
               "type":"ColorInput",
               "data":[
                  "1",
                  "34",
                  "23"
               ]
            }
         ]
      },
      {
         "idObjet":2,
         "libelleObjet":"capteurTemperature",
         "lastConnect":"27/12/2022 10:09:20",
         "fonctions":[
            {
               "idFonction":"1",
               "libelle":"temperature",
               "type":"read",
               "data":[
                  "1"
               ]
            }
         ]
      }
   ]
}


x = requests.post(url, json=myobj)

print(x.text)