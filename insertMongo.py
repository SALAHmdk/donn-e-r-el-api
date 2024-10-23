import requests
from pymongo import MongoClient

# Configuration de MongoDB
mongo_uri = "mongodb://localhost:27017/"  # Modifie ceci si nécessaire
client = MongoClient(mongo_uri)

# Accéder à la base de données et à la collection
db = client["velib_db"]
collection = db["velib_disponibilite_10_32"]  # Nom de la collection modifié

# URL de l'API
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"

# Paramètres initiaux pour la pagination
params = {
    'limit': 100,  # Limite de 100 résultats par page
    'offset': 0    # Offset pour la pagination
}

# Fonction pour récupérer toutes les données et les insérer dans MongoDB
def fetch_and_insert_data():
    total_documents = 0
    while True:
        # Faire la requête vers l'API avec pagination
        response = requests.get(url, params=params)
        data = response.json()

        # Préparer les documents à insérer
        documents = []
        for station in data['results']:
            document = {
                "stationcode": station['stationcode'],
                "name": station['name'],
                "is_installed": station['is_installed'],
                "capacity": station['capacity'],
                "numdocksavailable": station['numdocksavailable'],
                "numbikesavailable": station['numbikesavailable'],
                "mechanical": station['mechanical'],
                "ebike": station['ebike'],
                "is_renting": station['is_renting'],
                "is_returning": station['is_returning'],
                "duedate": station['duedate'],
                "coordonnees_geo": {
                    "lon": station['coordonnees_geo']['lon'],
                    "lat": station['coordonnees_geo']['lat']
                },
                "nom_arrondissement_communes": station['nom_arrondissement_communes'],
                "code_insee_commune": station['code_insee_commune']
            }
            documents.append(document)

        # Insérer les documents dans MongoDB
        if documents:
            collection.insert_many(documents)
            total_documents += len(documents)
            print(f"{len(documents)} documents insérés dans la collection {collection.name}.")
        else:
            print("Aucun document à insérer.")

        # Si le nombre de résultats est inférieur à la limite, arrêter la boucle
        if len(data['results']) < params['limit']:
            break

        # Incrémenter l'offset pour récupérer la prochaine page de résultats
        params['offset'] += params['limit']

    print(f"Total de {total_documents} documents insérés dans la collection.")

# Appeler la fonction pour récupérer et insérer les données
fetch_and_insert_data()

# Fermer la connexion à la base de données
client.close()
