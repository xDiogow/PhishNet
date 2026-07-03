# PhishNet — Plan de Tests v1.1

**Projet :** PhishNet (B2B Phishing Simulation Platform)
**Certification :** RNCP 37873 — CDA Niveau 6 (BC03)
**Auteur :** Diogo Gomes Lopes
**Date :** Juin 2026

---

## 1. Tableau de bord — Résultats globaux

| Indicateur | Valeur |
|---|---|
| Tests au total | **290** |
| Tests passés | **290 ✓** |
| Tests backend (pytest) | 212 |
| Tests frontend (vitest) | 78 |
| Couverture backend | **80%** |

> Les 212 tests backend couvrent : authentification, campagnes (création immédiate + planifiée, scheduling automatique), tracking (pixel, clic, soumission, signalement), templates (global + tenant), tenants, invitations, gestion d'équipe (membres, permissions, GDPR), audit logs, session Redis, et les couches service/repository (campaign_service, email_service, scheduler, stats repo, campaign repo, session repo).
> Routes de tracking : `/px/<token>` (pixel), `/r/<token>` (redirect clic), `/secure/<token>` (landing page GET/POST), `/report/<token>` (signalement comportement conscient).

Exécution automatique à chaque push via GitHub Actions CI.
Rapport de couverture backend généré en XML (artifact `backend-coverage`).

---

## 2. Objectifs et périmètre

### 2.1 Objectifs

- Vérifier que chaque exigence fonctionnelle (EF01–EF18) est couverte par au moins un cas de test automatisé.
- Garantir l'isolation multi-tenant : un utilisateur ne peut accéder qu'aux ressources de son tenant.
- Valider la conformité accessibilité RGAA / WCAG 2.1 AA des pages principales.
- Vérifier le comportement responsive des composants clés sur mobile (viewport 375 px).
- S'assurer que les endpoints protégés refusent les requêtes sans JWT valide (HTTP 401).
- Valider la révocation de tokens JWT via le `SessionRepository` (couche NoSQL Redis).

### 2.2 Dans le périmètre

- API backend Flask : authentification (`login`, `register`, `logout`), campagnes, templates, équipe, tenants, tracking, audit logs
- Couche NoSQL : `SessionRepository` (Redis) — stockage et vérification des JTIs révoqués
- Frontend React : pages Dashboard, Campaigns, ViewCampaign, Templates, Tenants
- Accessibilité (axe-core, RGAA)
- Responsive design (Tailwind breakpoints)
- Sécurité : JWT, rate-limiting, isolation tenant, révocation de session

### 2.3 Hors périmètre

- Tests de charge / performance (non requis pour le TP CDA)
- Tests de compatibilité navigateurs croisés (Chrome, Firefox, Safari)
- Tests de pénétration (pentest) formels

---

## 3. Stratégie de tests

| Type | Outil / Framework | Couche | Description |
|---|---|---|---|
| Intégration | pytest 8 + SQLAlchemy (SQLite in-memory) | Backend | Teste chaque endpoint via le client Flask de test. Base SQLite recréée avant chaque classe. Fixtures pytest pour les données de test. |
| Composants React | Vitest 4 + @testing-library/react | Frontend | Monte les composants en isolation, simule les appels API (`vi.mock`), vérifie le rendu et les interactions. |
| Accessibilité | axe-core + jest-axe (RGAA / WCAG 2.1 AA) | Frontend | Analyse automatique des violations d'accessibilité sur les pages Login et Dashboard. |
| Responsive | Vitest — vérification des classes Tailwind | Frontend | Vérifie la présence des classes `sm:` et `lg:` garantissant l'adaptation mobile/desktop. |
| Session / NoSQL | pytest + unittest.mock (`patch.object`) | Backend | Teste la révocation de tokens JWT via `SessionRepository` (Redis). Les appels Redis sont remplacés par des mocks en mémoire pour garantir l'isolation des tests sans dépendance à un Redis réel. |
| Manuel E2E | Navigateur + Mailtrap | E2E | Vérification manuelle du flux complet : envoi email → ouverture → clic → soumission → page caught. |

---

## 4. Environnements de tests

### CI (GitHub Actions)

- OS : ubuntu-latest
- Python 3.12 + pip cache
- Node 20 + npm cache
- DB : SQLite in-memory
- Redis : désactivé pour les tests (`SESSION_BLOCKLIST_ENABLED = False`, `RATELIMIT_STORAGE_URI = memory://`)

### Local (développeur)

- Python 3.12 / Node 22
- SQLite (tests) ou PostgreSQL (dev)
- Docker Compose dev
- `pytest -v` / `npm test`

### Staging

- Docker Compose staging
- PostgreSQL 15 isolé
- Redis 7 (rate limiting + blocklist JWT)
- Gunicorn 2 workers
- Mailtrap SMTP

---

## 5. Catalogue des cas de tests

### A — Authentification

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-A-01 | Login avec identifiants valides | Utilisateur actif en BDD, email + mot de passe corrects | HTTP 200 + JWT token + données user (email, is_admin, permissions[]) | Intégration | EF01 | ✅ Passé |
| TC-A-02 | Login avec mot de passe incorrect | Utilisateur actif, mauvais mot de passe | HTTP 401 + message « Invalid credentials » | Intégration | EF01 | ✅ Passé |
| TC-A-03 | Login avec compte inactif | Utilisateur avec is_active=False | HTTP 403 + message « User account is inactive » | Intégration | EF01 | ✅ Passé |
| TC-A-04 | Inscription via code d'invitation valide | Code d'invitation non utilisé + non expiré en BDD | HTTP 201 + utilisateur créé + invitation marquée is_used=True | Intégration | EF02 | ✅ Passé |
| TC-A-05 | Inscription avec code d'invitation déjà utilisé | Invitation is_used=True | HTTP 400 + message d'erreur | Intégration | EF02 | ✅ Passé |
| TC-A-06 | Rate limiting sur /auth/login (brute-force) | 6 requêtes POST successives en moins d'une minute | HTTP 429 à partir de la 6e requête | Sécurité | EF17 | ✅ Passé |

### B — Campagnes

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-B-01 | Lister les campagnes de son tenant | JWT valide, 1 campagne créée pour le tenant | HTTP 200 + liste contenant 1 campagne (id, name, status) | Intégration | EF13 | ✅ Passé |
| TC-B-02 | Isolation tenant — ne pas voir les campagnes d'un autre tenant | JWT valide tenant A, campagne créée pour tenant B | HTTP 200 + liste vide (campagne du tenant B absente) | Sécurité | EF17 | ✅ Passé |
| TC-B-03 | Créer une campagne avec template + cibles existants | Template en BDD + 1 cible associée au tenant, mock email_service | HTTP 201 + campaign.status = RUNNING + audit_log CREATE_CAMPAIGN | Intégration | EF08 | ✅ Passé |
| TC-B-04 | Créer une campagne sans cibles | Tenant sans cibles enregistrées | HTTP 400 + message « No targets found » | Intégration | EF08 | ✅ Passé |
| TC-B-05 | Arrêter une campagne en cours | Campagne status=RUNNING | HTTP 200 + campaign.status = STOPPED + stopped_at renseigné | Intégration | EF09 | ✅ Passé |
| TC-B-06 | Statistiques en temps réel d'une campagne | Campagne avec CampaignResult rows | HTTP 200 + summary {total, sent, opened, clicked, submitted} + results[] | Intégration | EF13 | ✅ Passé |
| TC-B-07 | Accéder à une campagne d'un autre tenant (isolation) | JWT tenant A, ID campagne du tenant B | HTTP 404 (campagne non trouvée) | Sécurité | EF17 | ✅ Passé |
| TC-B-08 | Créer une campagne avec `scheduled_start_at` futur → status SCHEDULED | Template + cibles en BDD, `scheduled_start_at` = now + 1h | HTTP 201 + campaign.status = SCHEDULED + aucun email envoyé | Intégration | EF08 | ✅ Passé |
| TC-B-09 | Scheduler lance automatiquement une campagne planifiée à l'heure prévue | Campagne status=SCHEDULED, `scheduled_start_at` dépassé | campaign.status = RUNNING + launched_at renseigné + emails envoyés | Intégration | EF08 | ✅ Passé |
| TC-B-10 | Scheduler arrête automatiquement une campagne dont `scheduled_end_at` est dépassé | Campagne status=RUNNING, `scheduled_end_at` dépassé | campaign.status = STOPPED + stopped_at renseigné | Intégration | EF09 | ✅ Passé |

### C — Tracking (endpoints publics)

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-C-01 | Pixel d'ouverture : première ouverture enregistrée | CampaignResult avec tracking_token valide, opened_at=NULL | HTTP 200 image/gif + opened_at renseigné + status='Opened' | Intégration | EF11 | ✅ Passé |
| TC-C-02 | Pixel d'ouverture : seconde ouverture non rédupliquée | opened_at déjà renseigné | HTTP 200 image/gif + opened_at inchangé | Intégration | EF11 | ✅ Passé |
| TC-C-03 | Tracking clic : redirect vers landing page | Token valide | HTTP 302 vers /secure/{token} + clicked_at renseigné | Intégration | EF12 | ✅ Passé |
| TC-C-04 | Landing page servie avec personnalisation (FirstName, Email) | Template avec `{{.FirstName}}`, cible John Doe | HTML retourné contenant « John » (placeholder remplacé) | Intégration | EF10 | ✅ Passé |
| TC-C-05 | Soumission credentials → redirect /caught | POST /secure/{token} | HTTP 302 vers /caught + submitted_at renseigné + status='Submitted Data' (aucun credential stocké) | Intégration | EF14 | ✅ Passé |

### D — Templates

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-D-01 | Créer un template (admin) | JWT admin, données template valides | HTTP 201 + template en BDD | Intégration | EF05 | ✅ Passé |
| TC-D-02 | Créer un template (non admin) → refus | JWT utilisateur standard | HTTP 403 | Sécurité | EF05 | ✅ Passé |
| TC-D-03 | Accéder à l'endpoint sans JWT | Aucun header Authorization | HTTP 401 | Sécurité | EF17 | ✅ Passé |
| TC-D-04 | Modifier un template utilisé par une campagne RUNNING → refus | Template lié à une campagne status=RUNNING | HTTP 409 + message "running campaign" + nom de la campagne | Intégration | EF05 | ✅ Passé |
| TC-D-05 | Modifier un template après arrêt de la campagne → autorisé | Campagne passée de RUNNING à STOPPED | HTTP 200 + template mis à jour | Intégration | EF05 | ✅ Passé |
| TC-D-06 | Supprimer un template utilisé par une campagne RUNNING → refus | Template lié à une campagne status=RUNNING | HTTP 409 + message "running campaign" | Intégration | EF05 | ✅ Passé |

### E — Tenants & Invitations

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-E-01 | Créer un tenant (admin) | JWT is_admin=True | HTTP 201 + tenant en BDD + invitation générée automatiquement | Intégration | EF03 | ✅ Passé |
| TC-E-02 | Supprimer un tenant avec des utilisateurs → refus | Tenant avec 1+ utilisateurs | HTTP 400 + message d'erreur | Intégration | EF04 | ✅ Passé |
| TC-E-03 | Valider un code d'invitation | Code valide (is_used=False, non expiré) | HTTP 200 + tenant name retourné | Intégration | EF02 | ✅ Passé |
| TC-E-04 | Créer une invitation (opérateur avec manage_team) | JWT avec permission manage_team | HTTP 201 + invitation_code générée | Intégration | EF05 | ✅ Passé |
| TC-E-05 | Créer une invitation → refus si non manage_team | JWT sans permission manage_team | HTTP 403 + Permission denied | Sécurité | EF05 | ✅ Passé |
| TC-E-06 | Invitation email — champ email persisté | POST avec email dans le body | HTTP 201 + invitation.email renseigné en BDD | Intégration | EF05 | ✅ Passé |
| TC-E-07 | Invitation code invalide → refus | Code inexistant ou expiré | HTTP 400 + message d'erreur | Intégration | EF02 | ✅ Passé |

### J — Gestion d'équipe & Permissions

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-J-01 | Lister les membres du tenant | JWT valide | HTTP 200 + liste avec email, permissions[], is_admin, is_active | Intégration | EF06 | ✅ Passé |
| TC-J-02 | Isolation tenant — membres d'un autre tenant absents | JWT tenant A, membres tenant B en BDD | HTTP 200 + membres tenant B absents de la liste | Sécurité | EF17 | ✅ Passé |
| TC-J-03 | Attribuer des permissions à un membre (manage_team) | JWT avec manage_team, membre du même tenant | HTTP 200 + permissions mises à jour en BDD | Intégration | EF06 | ✅ Passé |
| TC-J-04 | Attributions permissions → refus si non manage_team | JWT sans manage_team | HTTP 403 + Permission denied | Sécurité | EF06 | ✅ Passé |
| TC-J-05 | GDPR Art. 17 — suppression cible + anonymisation PII | JWT avec manage_targets, cible avec résultats de campagne | HTTP 200 + target supprimée + email/nom anonymisés dans campaign_results | Intégration | EF16 | ✅ Passé |
| TC-J-06 | GDPR — isolation tenant (cible d'un autre tenant) | JWT tenant A, cible tenant B | HTTP 404 | Sécurité | EF17 | ✅ Passé |

### F — Audit Logs

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-F-01 | Lister les logs d'audit du tenant (paginé) | JWT valide, logs en BDD | HTTP 200 + {logs[], total, page, per_page, total_pages} | Intégration | EF15 | ✅ Passé |
| TC-F-02 | Exporter les logs en CSV | JWT valide | HTTP 200 + Content-Type: text/csv + en-têtes valides | Intégration | EF16 | ✅ Passé |

### G — Accessibilité (RGAA / WCAG 2.1 AA)

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-G-01 | Page Login — aucune violation axe-core | Rendu jsdom du composant Login | axe(container) → zéro violation AA | Accessibilité | EF18 | ✅ Passé |
| TC-G-02 | Page Dashboard — aucune violation axe-core | Dashboard chargé avec données mockées | axe(container) → zéro violation AA | Accessibilité | EF18 | ✅ Passé |

### H — Responsive Design

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-H-01 | Grille de stats Dashboard — breakpoints responsifs | Dashboard rendu | HTML contient `sm:grid-cols-2` et `lg:grid-cols-4` | Responsive | EF18 | ✅ Passé |
| TC-H-02 | Bloc CTA — passe de colonne à ligne sur desktop | Dashboard rendu | HTML contient `sm:flex-row` | Responsive | EF18 | ✅ Passé |
| TC-H-03 | Section contenu — grille 2 colonnes sur desktop | Dashboard rendu | HTML contient `lg:grid-cols-2` | Responsive | EF18 | ✅ Passé |

### I — Session / Déconnexion (NoSQL Redis)

> Couche testée : `SessionRepository` (`app/repository/session_repository.py`).
> Redis est mocké via `unittest.mock.patch.object` — aucune connexion réseau requise.

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-I-01 | Déconnexion sans token → refus | Aucun header Authorization | HTTP 401 | Sécurité | EF17 | ✅ Passé |
| TC-I-02 | Déconnexion réussie — revoke_token appelé avec le JTI | JWT valide, `session_repo.revoke_token` mocké | HTTP 200 + message "Successfully logged out" + `revoke_token` appelé 1× avec `(jti: str, ttl: int > 0)` | Sécurité | EF17 | ✅ Passé |
| TC-I-03 | Token révoqué → accès protégé refusé | `SESSION_BLOCKLIST_ENABLED=True`, JTI stocké en mémoire après logout | GET /api/campaigns avec token révoqué → HTTP 401 | Sécurité | EF17 | ✅ Passé |
| TC-I-04 | Token valide non révoqué → accès accordé | `is_token_revoked` retourne False (mock) | GET /api/campaigns → HTTP 200 | Sécurité | EF01 | ✅ Passé |

### T — Tracking — Route Signalement (`/report/<token>`)

| ID | Description | Préconditions | Résultat attendu | Type | Réf. EF | Statut |
|---|---|---|---|---|---|---|
| TC-T-10 | GET /report/\<token\> — enregistre reported_at et status=Reported | CampaignResult avec tracking_token valide | reported_at renseigné en BDD + status='Reported' | Intégration | EF11 | ✅ Passé |
| TC-T-11 | GET /report/\<token\> — redirection vers /caught?reported=true | Token valide | HTTP 302 vers /caught?reported=true | Intégration | EF11 | ✅ Passé |
| TC-T-12 | GET /report/\<token\> idempotent — second appel ne réécrit pas reported_at | reported_at déjà renseigné | reported_at inchangé après second appel | Intégration | EF11 | ✅ Passé |
| TC-T-13 | GET /report/\<token inconnu\> — redirige sans 404 | Token inexistant en BDD | HTTP 302 vers /caught?reported=true (pas de 404) | Intégration | EF11 | ✅ Passé |
| TC-T-14 | GET /report/\<token\> — incrémente reported_count dans CampaignStats | CampaignStats en BDD pour la campagne | reported_count + 1 après appel | Intégration | EF11 | ✅ Passé |

### K — Tests Couche Service & Repository

> +50 tests unitaires/intégration couvrant les couches service et repository.

| Classe de test | Tests | Couche | Description |
|---|---|---|---|
| `TestCampaignService` | 15 | Service | Création, lancement, arrêt, scheduling, envoi emails, statistiques — logique métier isolée (mocks repos) |
| `TestEmailService` | 16 | Service | Construction des emails, remplacement placeholders (`{{FirstName}}`, `{{REPORT_URL}}`), envoi SMTP mocké |
| `TestScheduler` | 3 | Service | Lancement automatique des campagnes planifiées à l'heure prévue |
| `TestCampaignStatsRepository` | 4 | Repository | `_increment_stat`, `reported_count`, accès concurrent |
| `TestCampaignRepository` | 3 | Repository | Requêtes filtrées par tenant, isolation multi-tenant |
| `TestSessionRepository` | 4 | Repository | Révocation JTI Redis, TTL, `is_token_revoked` |

---

## 6. Critères d'entrée et de sortie

### Critères d'entrée (pour lancer les tests)

- Le code est fusionné sur la branche `main` ou une PR est ouverte
- L'environnement CI est opérationnel (GitHub Actions)
- Les dépendances sont installées (`requirements.txt`, `package-lock.json`)
- La configuration de test est disponible (`TestingConfig`, `vitest.config.js`)

### Critères de sortie (pour valider les tests)

- 100 % des tests passent (0 échec, 0 erreur)
- Aucune violation d'accessibilité AA détectée par axe-core
- Le build frontend (`npm run build`) réussit sans avertissement bloquant
- Le rapport de couverture backend est généré et uploadé comme artifact CI

---

## 7. Intégration CI/CD

| Job GitHub Actions | Commande | Déclencheur |
|---|---|---|
| `backend-lint` | `ruff check . && ruff format --check .` | push/PR → main |
| `backend-tests` | `pytest tests/ -v --cov=app --cov-report=xml` | après backend-lint |
| `frontend-lint` | `npm run lint` (ESLint) | push/PR → main |
| `frontend-tests` | `npm test -- --run` (Vitest) | après frontend-lint |
| `frontend-build` | `npm run build` (Vite) | après frontend-tests |
