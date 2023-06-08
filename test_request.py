import requests

#path = 'https://floriancodebecq.pythonanywhere.com/api'
path = 'http://192.168.0.45:5000/'
url = path + 'connexion'

# myobj = { "id_util": "110", "mail_util": "codebecq.florian@gmail.com", "nom_util": "Codebecq", "password": "florian", "prenom_util": "Florian" }
myobj = {"mail": "codebe.florian@gmail.com", "password": "florian"}

x = requests.post(url, json=myobj)

print(x.text)
