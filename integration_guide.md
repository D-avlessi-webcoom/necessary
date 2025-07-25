# Guide d'intégration du module IA avec Laravel

Ce document décrit comment intégrer l'API du module d'intelligence artificielle avec une application Laravel existante. Cette intégration permettra à l'application Laravel d'utiliser les fonctionnalités de prédiction d'indicateurs et de regroupement de communes.

## Table des matières

1. [Prérequis](#prérequis)
2. [Déploiement du module IA](#déploiement-du-module-ia)
3. [Configuration de l'application Laravel](#configuration-de-lapplication-laravel)
4. [Création des services de communication](#création-des-services-de-communication)
5. [Intégration avec les contrôleurs Laravel](#intégration-avec-les-contrôleurs-laravel)

## Prérequis

- Python 3.8+ installé sur le serveur
- PHP 8.0+ avec Laravel 8+
- Composer installé
- Accès aux données des indicateurs
- Guzzle HTTP Client pour Laravel (si non installé déjà)

## Déploiement du module IA

### 1. Copier les fichiers

Transférez les fichiers suivants sur le serveur d'application :

- `api.py` - L'API FastAPI
- `requirements.txt` - Les dépendances Python
- Dossier contenant les données extraites (`extracted_data`)
- `ai_module.py` - Le module IA

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Lancer l'API

En développement :

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

En production :

```bash
# Option 1: Uvicorn directement
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Option 2: Avec Gunicorn pour plus de robustesse
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app -b 0.0.0.0:8000 &
```

Pour démarrer automatiquement le service au démarrage du serveur, vous pouvez créer un service systemd (Linux) :

```bash
sudo nano /etc/systemd/system/sid-ai-module.service
```

Contenu du fichier service :

```
[Unit]
Description=SID Platform AI Module API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/dossier/api
ExecStart=/usr/bin/python3 -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activer et démarrer le service :

```bash
sudo systemctl enable sid-ai-module
sudo systemctl start sid-ai-module
```

## Configuration de l'application Laravel

### 1. Installer Guzzle HTTP Client

Si ce n'est pas déjà fait, installez Guzzle pour les requêtes HTTP :

```bash
composer require guzzlehttp/guzzle
```

### 2. Configurer les variables d'environnement

Ajoutez les variables suivantes à votre fichier `.env` :

```
AI_MODULE_API_URL=http://localhost:8000
AI_MODULE_TIMEOUT=30
```

## Création des services de communication

### 1. Créer un service d'API

Créez un nouveau service pour communiquer avec l'API du module IA :

```bash
php artisan make:provider AIModuleServiceProvider
```

Ensuite, créez une classe de service dans `app/Services` :

```bash
mkdir -p app/Services
touch app/Services/AIModuleService.php
```

Contenu de `app/Services/AIModuleService.php` :

```php
<?php

namespace App\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;
use Illuminate\Support\Facades\Log;

class AIModuleService
{
    protected $client;
    protected $baseUrl;

    public function __construct()
    {
        $this->baseUrl = env('AI_MODULE_API_URL', 'http://localhost:8000');
        $this->client = new Client([
            'base_uri' => $this->baseUrl,
            'timeout' => env('AI_MODULE_TIMEOUT', 30),
        ]);
    }

    /**
     * Get health status of the AI module
     */
    public function getHealth()
    {
        try {
            $response = $this->client->get('/health');
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('AI Module health check failed: ' . $e->getMessage());
            return [
                'success' => false,
                'data' => null,
                'message' => 'AI Module service is unavailable',
                'timestamp' => now()->toIso8601String()
            ];
        }
    }

    /**
     * Get communes from the AI module
     */
    public function getCommunes()
    {
        try {
            $response = $this->client->get('/communes');
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('Failed to get communes: ' . $e->getMessage());
            throw new \Exception('Failed to retrieve communes from AI Module');
        }
    }

    /**
     * Get indicators from the AI module
     */
    public function getIndicators()
    {
        try {
            $response = $this->client->get('/indicators');
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('Failed to get indicators: ' . $e->getMessage());
            throw new \Exception('Failed to retrieve indicators from AI Module');
        }
    }

    /**
     * Predict indicator values
     * 
     * @param int $yearsToPredict Number of years to predict
     * @param array|null $communeIds List of commune IDs to predict for
     * @param array|null $indicatorIds List of indicator IDs to predict
     * @return array
     */
    public function predictIndicators($yearsToPredict, $communeIds = null, $indicatorIds = null)
    {
        try {
            $payload = [
                'years_to_predict' => $yearsToPredict
            ];
            
            if ($communeIds !== null) {
                $payload['commune_ids'] = $communeIds;
            }
            
            if ($indicatorIds !== null) {
                $payload['indicator_ids'] = $indicatorIds;
            }
            
            $response = $this->client->post('/predict', [
                'json' => $payload
            ]);
            
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('Failed to predict indicators: ' . $e->getMessage());
            throw new \Exception('Failed to predict indicators from AI Module');
        }
    }

    /**
     * Cluster communes
     * 
     * @param int|null $nClusters Number of clusters
     * @param int|null $maxClusters Maximum clusters to try
     * @return array
     */
    public function clusterCommunes($nClusters = null, $maxClusters = null)
    {
        try {
            $payload = [];
            
            if ($nClusters !== null) {
                $payload['n_clusters'] = $nClusters;
            }
            
            if ($maxClusters !== null) {
                $payload['max_clusters'] = $maxClusters;
            }
            
            $response = $this->client->post('/cluster', [
                'json' => $payload
            ]);
            
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('Failed to cluster communes: ' . $e->getMessage());
            throw new \Exception('Failed to cluster communes from AI Module');
        }
    }

    /**
     * Get dashboard data
     * 
     * @param int $yearsToPredict Number of years to predict
     * @return array
     */
    public function getDashboardData($yearsToPredict = 2)
    {
        try {
            $response = $this->client->get('/dashboard', [
                'query' => [
                    'years_to_predict' => $yearsToPredict
                ]
            ]);
            
            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            Log::error('Failed to get dashboard data: ' . $e->getMessage());
            throw new \Exception('Failed to retrieve dashboard data from AI Module');
        }
    }
}
```

### 2. Enregistrer le service

Modifiez votre `AIModuleServiceProvider.php` :

```php
<?php

namespace App\Providers;

use App\Services\AIModuleService;
use Illuminate\Support\ServiceProvider;

class AIModuleServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register(): void
    {
        $this->app->singleton(AIModuleService::class, function ($app) {
            return new AIModuleService();
        });
    }

    /**
     * Bootstrap services.
     */
    public function boot(): void
    {
        //
    }
}
```

Ajoutez le fournisseur à `config/app.php` :

```php
'providers' => [
    // ...
    App\Providers\AIModuleServiceProvider::class,
],
```

## Intégration avec les contrôleurs Laravel

### 1. Créer les contrôleurs

Créez un contrôleur pour gérer les fonctionnalités du module IA :

```bash
php artisan make:controller AIModuleController
```

Contenu de `app/Http/Controllers/AIModuleController.php` :

```php
<?php

namespace App\Http\Controllers;

use App\Services\AIModuleService;
use Illuminate\Http\Request;

class AIModuleController extends Controller
{
    protected $aiService;

    public function __construct(AIModuleService $aiService)
    {
        $this->aiService = $aiService;
    }

    /**
     * Display the AI dashboard view
     */
    public function dashboard()
    {
        return view('ai.dashboard');
    }

    /**
     * Get health status of AI module
     */
    public function health()
    {
        return $this->aiService->getHealth();
    }

    /**
     * Get communes
     */
    public function communes()
    {
        return $this->aiService->getCommunes();
    }

    /**
     * Get indicators
     */
    public function indicators()
    {
        return $this->aiService->getIndicators();
    }

    /**
     * Predict indicators
     */
    public function predict(Request $request)
    {
        $validated = $request->validate([
            'years_to_predict' => 'required|integer|min:1|max:10',
            'commune_ids' => 'nullable|array',
            'commune_ids.*' => 'integer',
            'indicator_ids' => 'nullable|array',
            'indicator_ids.*' => 'integer',
        ]);

        return $this->aiService->predictIndicators(
            $validated['years_to_predict'],
            $validated['commune_ids'] ?? null,
            $validated['indicator_ids'] ?? null
        );
    }

    /**
     * Cluster communes
     */
    public function cluster(Request $request)
    {
        $validated = $request->validate([
            'n_clusters' => 'nullable|integer|min:2|max:10',
            'max_clusters' => 'nullable|integer|min:3|max:20',
        ]);

        return $this->aiService->clusterCommunes(
            $validated['n_clusters'] ?? null,
            $validated['max_clusters'] ?? null
        );
    }

    /**
     * Get dashboard data
     */
    public function dashboardData(Request $request)
    {
        $validated = $request->validate([
            'years_to_predict' => 'nullable|integer|min:1|max:10',
        ]);

        return $this->aiService->getDashboardData(
            $validated['years_to_predict'] ?? 2
        );
    }
}
```

### 2. Définir les routes

Ajoutez les routes suivantes à `routes/web.php` ou `routes/api.php` selon vos besoins :

```php
// Pour routes/web.php - Interface utilisateur

Route::prefix('ai')->group(function () {
    Route::get('dashboard', [AIModuleController::class, 'dashboard'])->name('ai.dashboard');
});

// Pour routes/api.php - API REST

Route::prefix('api/ai')->group(function () {
    Route::get('health', [AIModuleController::class, 'health']);
    Route::get('communes', [AIModuleController::class, 'communes']);
    Route::get('indicators', [AIModuleController::class, 'indicators']);
    Route::post('predict', [AIModuleController::class, 'predict']);
    Route::post('cluster', [AIModuleController::class, 'cluster']);
    Route::get('dashboard-data', [AIModuleController::class, 'dashboardData']);
});
```

N'oubliez pas d'ajouter l'importation du contrôleur :

```php
use App\Http\Controllers\AIModuleController;
```