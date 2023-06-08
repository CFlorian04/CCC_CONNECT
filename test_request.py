import requests

path = 'https://floriancodebecq.pythonanywhere.com/api'
url = path + 'connexion'

# myobj = { "id_util": "110", "mail_util": "codebecq.florian@gmail.com", "nom_util": "Codebecq", "password": "florian", "prenom_util": "Florian" }
myobj = {"mail": "codebecq.florian@gmail.com", "password": "florian"}

x = requests.post(url, json=myobj)

print(x.text)
