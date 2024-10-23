import requests
import folium
import webbrowser
import os

# URL de l'API
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"

# Paramètres initiaux
params = {
    'limit': 100,  # Limite de 100 résultats par page
    'offset': 0  # Pour la pagination, commence à 0
}

# Créer une carte Folium centrée sur Paris
map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=12)


# Fonction pour récupérer toutes les données de manière paginée
def fetch_all_data():
    all_stations = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()

        # Ajouter les données récupérées à la liste complète
        all_stations.extend(data['results'])  # Les données sont sous la clé 'results'

        # Si le nombre de résultats est inférieur à la limite, on sait qu'on a tout récupéré
        if len(data['results']) < params['limit']:
            break

        # Incrémenter l'offset pour la prochaine page
        params['offset'] += params['limit']

    return all_stations


# Récupérer toutes les données des stations
stations = fetch_all_data()

# Parcourir les résultats et ajouter des marqueurs pour chaque station
for station in stations:
    name = station['name']  # Nom de la station
    lat = station['coordonnees_geo']['lat']  # Latitude
    lon = station['coordonnees_geo']['lon']  # Longitude
    num_bikes = station['numbikesavailable']  # Nombre de vélos disponibles

    # Ajouter un marqueur à la carte
    folium.Marker(
        location=[lat, lon],
        popup=f"{name} - Vélos disponibles: {num_bikes}",
        icon=folium.Icon(color='blue')
    ).add_to(map_paris)

# Enregistrer la carte dans un fichier HTML
map_file = 'map_paris_velib.html'
map_paris.save(map_file)

# Ouvrir la carte dans le navigateur
webbrowser.open('file://' + os.path.realpath(map_file))

print("La carte a été créée et ouverte dans le navigateur.")
