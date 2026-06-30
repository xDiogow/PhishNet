# PhishNet — Procédure de déploiement

**Projet :** PhishNet (B2B Phishing Simulation Platform)
**Certification :** RNCP 37873 — CDA Niveau 6 (BC03)
**Auteur :** Diogo Gomes Lopes
**Date :** Juin 2026
**Version :** 1.0

---

## 1. Architecture de déploiement

PhishNet repose sur quatre conteneurs Docker orchestrés par Docker Compose :

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Serveur (Ubuntu 22.04 LTS)                     │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  phishnet-frontend  (Nginx :80 → :443)   │  │
│  │  React SPA + proxy /api → backend        │  │
│  └──────────────────┬───────────────────────┘  │
│                     │ réseau Docker interne     │
│  ┌──────────────────▼───────────────────────┐  │
│  │  phishnet-backend   (Gunicorn :5000)      │  │
│  │  Flask REST API — 4 workers               │  │
│  └──────┬─────────────────────┬─────────────┘  │
│         │                     │                 │
│  ┌──────▼──────┐    ┌─────────▼──────────┐     │
│  │  phishnet-db│    │  phishnet-redis     │     │
│  │  PostgreSQL │    │  Redis 7 (sessions  │     │
│  │  15          │    │  + rate limiting)   │     │
│  └─────────────┘    └────────────────────┘     │
└─────────────────────────────────────────────────┘
```

| Conteneur | Image de base | Rôle |
|---|---|---|
| `phishnet-frontend` | `nginx:1.25-alpine` | Sert le SPA React, proxy `/api/*` et `/track/*` vers le backend |
| `phishnet-backend` | `python:3.11-slim` (multi-stage) | API Flask + Gunicorn, migrations Alembic |
| `phishnet-db` | `postgres:15-alpine` | Base de données relationnelle principale |
| `phishnet-redis` | `redis:7-alpine` | Blocklist JWT (sessions révoquées) + rate limiting |

Les images backend et frontend sont publiées automatiquement sur **GitHub Container Registry** (`ghcr.io`) à chaque push validé sur `main`.

---

## 2. Prérequis serveur

### Matériel minimum

| Ressource | Minimum | Recommandé |
|---|---|---|
| CPU | 1 vCPU | 2 vCPU |
| RAM | 1 Go | 2 Go |
| Disque | 10 Go | 20 Go SSD |

### Logiciels

```bash
# Ubuntu 22.04 LTS
docker --version   # >= 24.0
docker compose version  # >= 2.20  (plugin, pas docker-compose v1)
git --version
```

### Réseau

- Port **80** ouvert (HTTP → redirigé vers HTTPS)
- Port **443** ouvert (HTTPS)
- Port **25 / 587** sortant autorisé (envoi d'emails SMTP)

---

## 3. Variables d'environnement

Créer un fichier `.env` à la racine du projet à partir du modèle :

```bash
cp .env.example .env
```

| Variable | Exemple | Description |
|---|---|---|
| `POSTGRES_DB` | `phishnet` | Nom de la base de données |
| `POSTGRES_USER` | `phishnet` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | *(secret)* | Mot de passe PostgreSQL — **ne jamais commiter** |
| `SECRET_KEY` | *(secret 64 chars)* | Clé Flask pour les cookies/sessions |
| `JWT_SECRET_KEY` | *(secret 64 chars)* | Clé de signature des tokens JWT |
| `DATABASE_URL` | `postgresql://…` | URL complète de connexion (construite depuis les variables ci-dessus) |
| `REDIS_URL` | `redis://redis:6379/0` | URL Redis (nom du service Docker) |
| `CORS_ORIGINS` | `https://phishnet.example.com` | Origines CORS autorisées |
| `APP_BASE_URL` | `https://phishnet.example.com` | URL publique — sert à construire les liens de tracking dans les emails |
| `MAIL_SERVER` | `smtp.mailtrap.io` | Serveur SMTP |
| `MAIL_PORT` | `587` | Port SMTP (587 = TLS STARTTLS) |
| `MAIL_USE_TLS` | `True` | Activer STARTTLS |
| `MAIL_USERNAME` | *(credentials SMTP)* | Identifiant SMTP |
| `MAIL_PASSWORD` | *(secret)* | Mot de passe SMTP |
| `MAIL_FROM` | `phishnet@company.com` | Adresse d'expédition |
| `FRONTEND_PORT` | `80` | Port exposé par Nginx sur l'hôte |

Génération de clés sécurisées :

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Déploiement initial (première installation)

### 4.1 Cloner le dépôt

```bash
git clone https://github.com/<org>/phishnet.git
cd phishnet
```

### 4.2 Configurer l'environnement

```bash
cp .env.example .env
# Éditer .env avec les valeurs de production
nano .env
```

### 4.3 Lancer les conteneurs

```bash
docker compose up -d
```

Docker Compose va :
1. Construire les images backend et frontend depuis les `Dockerfile` locaux (ou les pull depuis GHCR si disponibles)
2. Démarrer PostgreSQL et Redis
3. Attendre que la base de données soit prête (healthcheck)
4. Exécuter les migrations Alembic (`flask db upgrade`)
5. Peupler les templates intégrés (`flask seed-templates`)
6. Démarrer Gunicorn (4 workers) et Nginx

### 4.4 Vérifier le démarrage

```bash
# Statut des conteneurs
docker compose ps

# Logs en temps réel
docker compose logs -f backend

# Healthcheck backend
curl http://localhost/api/health
# Réponse attendue : {"status": "ok"}
```

### 4.5 Créer le premier compte administrateur

```bash
docker compose exec backend flask shell
```

```python
from app import db
from app.models.user import User
from app.models.tenant import Tenant

# Créer le tenant racine
tenant = Tenant(name="Admin")
db.session.add(tenant)
db.session.flush()

# Créer l'utilisateur admin
admin = User(
    email="admin@company.com",
    tenant_id=tenant.id,
    is_admin=True,
    is_operator=True,
)
admin.set_password("ChangeMe123!")
db.session.add(admin)
db.session.commit()
print("Admin créé.")
```

---

## 5. Déploiement des mises à jour (pipeline CI/CD)

### 5.1 Flux automatique

```
git push origin main
    │
    ▼
GitHub Actions — CI
  ├── backend-lint    (ruff)
  ├── backend-tests   (pytest, 125 tests)
  ├── frontend-lint   (ESLint)
  ├── frontend-tests  (Vitest, 47 tests)
  └── frontend-build  (Vite)
    │  (uniquement si CI = success)
    ▼
GitHub Actions — CD
  └── Build & push images → ghcr.io/<org>/phishnet/backend:latest
                           ghcr.io/<org>/phishnet/frontend:latest
```

### 5.2 Déploiement sur le serveur après mise à jour des images

```bash
# Sur le serveur de production
cd /opt/phishnet

# Récupérer les nouvelles images publiées par le CD
docker compose pull

# Redémarrer les services mis à jour (zéro downtime pour les services stateless)
docker compose up -d --no-build

# Vérifier
docker compose ps
curl http://localhost/api/health
```

### 5.3 Environnement de staging

Pour valider avant la production :

```bash
# Démarrer en mode staging (port 8080, LOG_LEVEL=DEBUG, volume isolé)
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Accès : http://<serveur>:8080
```

Le staging utilise un volume PostgreSQL séparé (`postgres_staging_data`) pour ne pas interférer avec la production.

---

## 6. Procédure de rollback

En cas de régression détectée après une mise à jour :

### 6.1 Identifier l'image précédente

```bash
# Lister les images disponibles localement avec leurs tags SHA
docker images ghcr.io/<org>/phishnet/backend
docker images ghcr.io/<org>/phishnet/frontend
```

### 6.2 Revenir à une version antérieure

```bash
# Éditer docker-compose.yml pour pointer vers un tag SHA spécifique
# Exemple : image: ghcr.io/<org>/phishnet/backend:a1b2c3d

docker compose up -d --no-build

# Vérifier
docker compose ps
curl http://localhost/api/health
```

### 6.3 Rollback de base de données

Les migrations Alembic supportent le rollback d'une version :

```bash
docker compose exec backend flask db downgrade -1
```

Revenir à une révision spécifique :

```bash
docker compose exec backend flask db downgrade <revision_id>
```

> Les identifiants de révision sont listés dans `backend/migrations/versions/`.

---

## 7. Sauvegarde et restauration

### 7.1 Sauvegarde PostgreSQL

```bash
# Dump compressé de la base de données
docker compose exec db pg_dump \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_DB} \
  -F c \
  -f /tmp/phishnet_$(date +%Y%m%d_%H%M%S).dump

# Copier sur l'hôte
docker cp phishnet-db:/tmp/phishnet_*.dump ./backups/
```

### 7.2 Restauration

```bash
# Arrêter le backend avant la restauration
docker compose stop backend

# Restaurer
docker compose exec db pg_restore \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_DB} \
  --clean \
  /tmp/phishnet_backup.dump

# Redémarrer
docker compose start backend
```

### 7.3 Sauvegarde Redis

Redis est utilisé uniquement pour les sessions actives (blocklist JWT, rate limiting). Les données sont volatiles par nature. Aucune sauvegarde n'est nécessaire — un redémarrage Redis force simplement la re-authentification des utilisateurs connectés.

---

## 8. Surveillance et logs

### 8.1 Logs applicatifs

```bash
# Logs de tous les services
docker compose logs -f

# Logs backend uniquement (requêtes HTTP + erreurs applicatives)
docker compose logs -f backend

# Logs Nginx (accès + erreurs)
docker compose logs -f frontend
```

### 8.2 Healthchecks Docker

Chaque conteneur expose un healthcheck natif :

| Conteneur | Commande de vérification | Intervalle |
|---|---|---|
| `backend` | `curl -f http://localhost:5000/api/health` | 30 s |
| `frontend` | `wget --spider http://localhost/` | 30 s |
| `db` | `pg_isready` | 10 s |
| `redis` | `redis-cli ping` | 10 s |

```bash
# Vérifier l'état de santé de tous les conteneurs
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
```

### 8.3 Métriques clés à surveiller

| Métrique | Commande |
|---|---|
| Utilisation mémoire | `docker stats --no-stream` |
| Espace disque (volumes) | `docker system df -v` |
| Connexions PostgreSQL actives | `docker compose exec db psql -U phishnet -c "SELECT count(*) FROM pg_stat_activity;"` |

---

## 9. Récapitulatif des commandes courantes

| Action | Commande |
|---|---|
| Démarrer tous les services | `docker compose up -d` |
| Arrêter tous les services | `docker compose down` |
| Redémarrer un service | `docker compose restart backend` |
| Voir les logs | `docker compose logs -f` |
| Appliquer les migrations | `docker compose exec backend flask db upgrade` |
| Accéder au shell backend | `docker compose exec backend flask shell` |
| Mettre à jour vers la dernière version | `docker compose pull && docker compose up -d --no-build` |
| Lancer en staging | `docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d` |
| Rollback migration | `docker compose exec backend flask db downgrade -1` |
| Sauvegarder la BDD | `docker compose exec db pg_dump -U phishnet -d phishnet -F c -f /tmp/backup.dump` |
