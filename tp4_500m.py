import requests
from haversine import haversine, Unit
from pymongo import MongoClient

# Configuration de MongoDB
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client["velib_db"]
collection = db["velib_disponibilite_realtime_01_500m"]

# URL de l'API pour les données Vélib (si tu veux récupérer les données directement de l'API)
velib_api_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"


# Fonction pour récupérer les coordonnées à partir d'une adresse en utilisant l'API Nominatim
def get_coordinates_from_address(address):
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    response = requests.get(nominatim_url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            return (float(data[0]['lat']), float(data[0]['lon']))
        else:
            raise ValueError("Adresse non trouvée")
    else:
        raise Exception("Erreur lors de la requête à Nominatim")


# Fonction pour filtrer les stations Vélib avec des ebikes à moins de 500m
def find_velib_stations_nearby(address, distance_limit=500):
    # Obtenir les coordonnées de l'adresse donnée
    address_coords = get_coordinates_from_address(address)
    print(f"Les coordonnées de l'adresse sont : {address_coords}")

    # Récupérer les stations Vélib' depuis la base de données MongoDB
    stations = collection.find({"ebike": {"$gt": 0}})  # Filtrer uniquement les stations avec des vélos électriques

    # Filtrer les stations à moins de 500m de l'adresse donnée
    nearby_stations = []
    for station in stations:
        station_coords = (station['coordonnees_geo']['lat'], station['coordonnees_geo']['lon'])
        distance = haversine(address_coords, station_coords, unit=Unit.METERS)
        if distance <= distance_limit:
            station_info = {
                "name": station['name'],
                "latitude": station['coordonnees_geo']['lat'],
                "longitude": station['coordonnees_geo']['lon'],
                "ebike": station['ebike'],
                "distance_meters": round(distance, 2)
            }
            nearby_stations.append(station_info)

    return nearby_stations


# Adresse d'entrée
address_input = "Champs-Élysées, "

# Récupérer les stations Vélib' proches avec des ebikes disponibles
stations_nearby = find_velib_stations_nearby(address_input)

# Afficher les résultats
if stations_nearby:
    print(f"Stations Vélib' à moins de 500m avec des ebikes autour de '{address_input}':")
    for station in stations_nearby:
        print(
            f"Station: {station['name']} | Distance: {station['distance_meters']}m | Ebikes disponibles: {station['ebike']}")
else:
    print(f"Aucune station avec des ebikes à moins de 500m autour de '{address_input}'.")
