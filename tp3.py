import requests
import folium
from pymongo import MongoClient
import webbrowser
import os
import time

# Configuration de MongoDB
mongo_uri = "mongodb://localhost:27017/"  # Modifie ceci si nécessaire
client = MongoClient(mongo_uri)

# Accéder à la base de données et à la collection
db = client["velib_db"]
collection = db["velib_disponibilite_realtime"]

# URL de l'API
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"

# Paramètres initiaux pour la pagination
params = {
    'limit': 100,  # Limite de 100 résultats par page
    'offset': 0    # Offset pour la pagination
}

# Fonction pour récupérer et insérer les données en temps réel
def fetch_and_insert_data_realtime():
    while True:
        total_documents = 0
        params['offset'] = 0  # Réinitialiser l'offset pour chaque cycle

        while True:
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

            # Supprimer les anciennes données et insérer les nouvelles
            collection.delete_many({})  # Supprimer les données précédentes pour avoir toujours des données à jour
            if documents:
                collection.insert_many(documents)
                total_documents += len(documents)
                print(f"{len(documents)} documents insérés dans la collection {collection.name}.")

            # Si le nombre de résultats est inférieur à la limite, arrêter la boucle de pagination
            if len(data['results']) < params['limit']:
                break

            # Incrémenter l'offset pour récupérer la prochaine page de résultats
            params['offset'] += params['limit']

        print(f"Total de {total_documents} documents insérés dans la collection.")

        # Mettre à jour la carte après chaque cycle de récupération
        update_map()

        # Attendre un intervalle de temps avant de récupérer à nouveau (par exemple, 60 secondes)
        time.sleep(60)

# Fonction pour créer et mettre à jour la carte Folium
def update_map():
    # Créer une carte Folium centrée sur Paris
    map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    # Récupérer les données de la collection
    stations = collection.find()

    # Ajouter des marqueurs pour chaque station sur la carte
    for station in stations:
        name = station['name']
        lat = station['coordonnees_geo']['lat']
        lon = station['coordonnees_geo']['lon']
        num_bikes = station['numbikesavailable']

        # Ajouter un marqueur à la carte
        folium.Marker(
            location=[lat, lon],
            popup=f"{name} - Vélos disponibles: {num_bikes}",
            icon=folium.Icon(color='blue')
        ).add_to(map_paris)  # Parenthèse correctement fermée ici

    # Enregistrer la carte dans un fichier HTML
    map_file = 'map_paris_velib_realtime.html'
    map_paris.save(map_file)

    # Ouvrir la carte dans le navigateur par défaut
    webbrowser.open('file://' + os.path.realpath(map_file))

    print("La carte a été mise à jour et ouverte dans le navigateur.")

# Lancer la récupération des données en temps réel
fetch_and_insert_data_realtime()
