# SID Platform AI Module API Documentation

Cette documentation détaille l'API du module d'intelligence artificielle de la plateforme SID, qui fournit des fonctionnalités de prédiction d'indicateurs et de regroupement de communes.

## Table des matières

1. [Informations générales](#informations-générales)
2. [Installation](#installation)
3. [Démarrage de l'API](#démarrage-de-lapi)
4. [Points de terminaison (Endpoints)](#points-de-terminaison-endpoints)
   - [Vérification de santé](#vérification-de-santé)
   - [Ressources disponibles](#ressources-disponibles)
   - [Prédiction des indicateurs](#prédiction-des-indicateurs)
   - [Clustering des communes](#clustering-des-communes)
   - [Données du tableau de bord](#données-du-tableau-de-bord)
5. [Structure des réponses](#structure-des-réponses)
6. [Exemples d'utilisation](#exemples-dutilisation)

## Informations générales

- **Version**: 1.0.0
- **Base URL**: `http://localhost:8080` (en développement local)
- **Format de réponse**: JSON

## Installation

1. Assurez-vous que Python 3.8+ est installé sur votre système.
2. Clonez le dépôt contenant le code de l'API.
3. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## Démarrage de l'API

Pour démarrer l'API en mode développement :

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

Pour le déploiement en production :

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app -b 0.0.0.0:8080
```

## Points de terminaison (Endpoints)

### Vérification de santé

#### GET /health

Vérifie l'état de l'API et du module d'intelligence artificielle.

**Réponse** :

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "communes_count": 77,
    "years_available": [2016, 2017, 2018, 2019, 2020],
    "indicators_count": 10
  },
  "message": "System is healthy",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

### Ressources disponibles

#### GET /communes

Récupère la liste de toutes les communes disponibles.

**Réponse** :

```json
{
  "success": true,
  "data": [
    {"id": 1, "nom": "BANIKOARA", "departement_id": 1},
    {"id": 2, "nom": "GOGOUNOU", "departement_id": 1},
    // ... autres communes
  ],
  "message": "Successfully retrieved 77 communes",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

#### GET /indicators

Récupère la liste de tous les indicateurs disponibles.

**Réponse** :

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Nombre de sessions ordinaires du conseil municipal"},
    {"id": 2, "name": "Taux de participation aux sessions"},
    // ... autres indicateurs
  ],
  "message": "Successfully retrieved 10 indicators",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

#### GET /years

Récupère la liste de toutes les années disponibles.

**Réponse** :

```json
{
  "success": true,
  "data": [2016, 2017, 2018, 2019, 2020],
  "message": "Successfully retrieved 5 years",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

### Prédiction des indicateurs

#### POST /predict

Prédit les valeurs des indicateurs pour les années futures.

**Corps de la requête** :

```json
{
  "years_to_predict": 3,
  "commune_ids": [1, 2, 3],
  "indicator_ids": [1, 2, 3]
}
```

**Paramètres** :

- `years_to_predict` (obligatoire) : Nombre d'années à prédire
- `commune_ids` (facultatif) : Liste des IDs de communes pour lesquelles prédire. Si non spécifié, toutes les communes sont incluses.
- `indicator_ids` (facultatif) : Liste des IDs d'indicateurs à prédire. Si non spécifié, tous les indicateurs sont inclus.

**Réponse** :

```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "commune_id": 1,
        "indicateur_id": 1,
        "year": 2020,
        "predicted_value": 78.5,
        "is_prediction": true
      },
      // ... autres prédictions et données historiques
    ],
    "years_predicted": 3,
    "communes": [1, 2, 3],
    "indicators": [1, 2, 3]
  },
  "message": "Successfully generated predictions for 9 data points",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

### Clustering des communes

#### POST /cluster

Regroupe les communes selon leur profil de digitalisation.

**Corps de la requête** :

```json
{
  "n_clusters": 4,
  "max_clusters": 10
}
```

**Paramètres** :

- `n_clusters` (facultatif) : Nombre de clusters à créer. Si non spécifié, le nombre optimal est déterminé automatiquement.
- `max_clusters` (facultatif) : Nombre maximum de clusters à essayer lors de la détermination du nombre optimal.

**Réponse** :

```json
{
  "success": true,
  "data": {
    "clusters": {
      "commune_ids": [1, 2, 3, ...],
      "cluster_labels": [0, 1, 2, ...],
      "n_clusters": 4,
      "pca_explained_variance": [0.45, 0.25, 0.15, ...],
      "cluster_centers_pca": [[0.1, 0.2], [-0.3, 0.4], ...],
      "commune_coords_pca": [[0.15, 0.22], [-0.37, 0.41], ...]
    },
    "characteristics": {
      "cluster_means": {
        "0": {"1": 75.3, "2": 45.6, ...},
        // ... autres clusters
      },
      "distinctive_indicators": {
        "0": {
          "top_indicators": [1, 3, 5, ...],
          "mean_values": {"1": 75.3, "3": 62.4, ...},
          "top_indicators_with_names": [
            {
              "id": 1,
              "name": "Nombre de sessions ordinaires du conseil municipal",
              "value": 75.3
            },
            // ... autres indicateurs
          ]
        },
        // ... autres clusters
      },
      "commune_counts": {"0": 15, "1": 22, ...}
    },
    "communes_with_clusters": [
      {
        "commune_id": 1,
        "commune_name": "BANIKOARA",
        "cluster": 0
      },
      // ... autres communes
    ],
    "n_clusters": 4
  },
  "message": "Successfully clustered communes into 4 groups",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

### Données du tableau de bord

#### GET /dashboard

Récupère toutes les données nécessaires pour le tableau de bord, combinant les prédictions et le clustering.

**Paramètres de requête** :

- `years_to_predict` (facultatif) : Nombre d'années à prédire. Par défaut : 2.

**Réponse** :

```json
{
  "success": true,
  "data": {
    "indicator_data": [...],
    "clusters": {...},
    "cluster_characteristics": {...},
    "communes": [...],
    "years": [...],
    "indicators": [...]
  },
  "message": "Successfully generated dashboard data",
  "timestamp": "2025-07-05T14:30:45.123456"
}
```

## Structure des réponses

Toutes les réponses de l'API suivent la structure suivante :

```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "timestamp": string (ISO format)
}
```

- `success` : Indique si la requête a réussi ou échoué
- `data` : Contient les données de la réponse (peut être null en cas d'erreur)
- `message` : Message descriptif sur le résultat de l'opération
- `timestamp` : Horodatage de la réponse

## Exemples d'utilisation

### Exemple avec cURL

#### Récupérer la liste des communes

```bash
curl -X GET http://localhost:8000/communes
```

#### Prédire les indicateurs

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"years_to_predict": 3, "commune_ids": [1, 2, 3]}'
```

#### Effectuer le clustering

```bash
curl -X POST http://localhost:8000/cluster \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Exemple avec JavaScript (fetch)

#### Prédire les indicateurs

```javascript
async function predictIndicators() {
  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      years_to_predict: 3,
      commune_ids: [1, 2, 3],
      indicator_ids: [1, 2, 3]
    }),
  });
  
  const data = await response.json();
  console.log(data);
}
```

#### Effectuer le clustering

```javascript
async function clusterCommunes() {
  const response = await fetch('http://localhost:8000/cluster', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      n_clusters: 4
    }),
  });
  
  const data = await response.json();
  console.log(data);
}
```

### Exemple avec PHP (Laravel)

#### Prédire les indicateurs

```php
public function getPredictions()
{
    $client = new \GuzzleHttp\Client();
    $response = $client->post('http://localhost:8000/predict', [
        'json' => [
            'years_to_predict' => 3,
            'commune_ids' => [1, 2, 3],
            'indicator_ids' => [1, 2, 3]
        ]
    ]);
    
    $data = json_decode($response->getBody(), true);
    return $data;
}
```

#### Effectuer le clustering

```php
public function getClusterData()
{
    $client = new \GuzzleHttp\Client();
    $response = $client->post('http://localhost:8000/cluster', [
        'json' => [
            'n_clusters' => null // Utilise le clustering automatique
        ]
    ]);
    
    $data = json_decode($response->getBody(), true);
    return $data;
}
```