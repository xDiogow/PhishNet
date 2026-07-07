# PhishNet

**B2B Phishing Simulation & Security Awareness Platform**

PhishNet is a full-stack application for conducting phishing simulations and security awareness training. Built for defensive security purposes, it enables organisations to test and improve employee awareness of phishing attacks.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** (for Vite 7.3)
- **Git**
- **An SMTP provider** : [Mailtrap](https://mailtrap.io/) (free) works well for testing

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PhishNet
```

### 2. Docker Containers setup
```bash
cp .env.example .env

# Configure the .env (SMTP credentials, secrets, etc.)
docker compose up -d
```

## ⚙️ Configuration

```bash
# PostgreSQL Database Configuration
POSTGRES_DB=phishnet
POSTGRES_USER=phishnet
POSTGRES_PASSWORD=changeme_secure_password_here

# Flask Backend Configuration
SECRET_KEY=changeme_secret_key
JWT_SECRET_KEY=changeme_jwt_secret_key
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Database URL
DATABASE_URL=postgresql://phishnet:changeme_secure_password_here@db:5432/phishnet

# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:80

# Frontend Configuration
FRONTEND_PORT=80

# SMTP, configure to match your mail provider (e.g. Mailtrap, SendGrid, SES)
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=phishnet@company.com

# Public base URL used to build tracking links embedded in phishing emails
APP_BASE_URL=http://localhost
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest            # Run all tests
pytest -v         # Verbose output
```

**Test Coverage:** 212 tests passing, 80% code coverage

### Frontend Tests

```bash
cd frontend
npm test               # Run tests
npm run test:ui        # Run tests with UI
npm run test:coverage  # Coverage report
```

**Test Coverage:** 78 tests passing (includes automated RGAA/WCAG 2.1 AA accessibility tests via axe-core)

---

## 📊 Features

✅ **Backend**
- Flask REST API with JWT authentication and multi-tenancy
- Native phishing engine, sends emails via SMTP, no external dependencies
- UUID-based tracking tokens per target per campaign
- Open tracking (1×1 GIF pixel), click tracking, credential submission tracking
- Tenant invitation system: Quick Code (one-time shareable code) or email invite (recipient shown as Pending until registration)
- Named permission system: manage_campaigns, manage_templates, manage_targets, manage_team, granular per-member attribution
- GDPR Art. 17 erasure: anonymize PII in campaign results then delete target
- Audit log for all admin and campaign actions

✅ **Frontend**
- React dashboard with real-time campaign statistics
- Campaign creation and lifecycle management (launch, view results, stop)
- Template editor supporting HTML email + landing page
- Team management: invite modal (Quick Code / Send via Email), permission attribution per member (gear icon → checkbox modal), Pending badge for unregistered invitees
- Target management with GDPR erasure
- Tenant administration (admin only)
- Audit log viewer with CSV export

---

## 🔀 Version Control

Branch-based workflow: each feature is developed on its own branch and merged into `main` via Pull Request. The CI pipeline (pytest + vitest + lint) runs automatically on every PR. Note: at the start of the project we worked directly on `main`, we adopted the feature-branch + PR model after learning collaborative Git practices on a joint project.

See [`docs/openapi.yaml`](docs/openapi.yaml) for the full API contract (OpenAPI 3.0, endpoints, request/response payloads).

---

## 📖 API Endpoints

### Auth
- `POST /api/auth/login`, Login a user (JWT stored in HttpOnly cookie)
- `POST /api/auth/register`, Register a new user using an invitation code
- `POST /api/auth/logout`, Logout (revokes JWT in Redis blocklist, clears HttpOnly cookie)

### Campaigns
- `GET /api/campaigns`, List all campaigns for your tenant
- `POST /api/campaigns`, Create a campaign (launches immediately, or scheduled if `scheduled_start_at` is set)
- `GET /api/campaigns/<id>`, Get campaign details
- `GET /api/campaigns/<id>/summary`, Live stats + per-target result list
- `POST /api/campaigns/<id>/complete`, Stop a running campaign
- `DELETE /api/campaigns/<id>`, Delete a campaign

### Tenants (Admin Only)
- `GET /api/tenants`, List all tenants
- `POST /api/tenants`, Create a tenant and generate its first invitation
- `GET /api/tenants/<id>`, Get tenant details
- `PUT /api/tenants/<id>`, Update tenant
- `DELETE /api/tenants/<id>`, Delete a tenant (must have no users)

### Tenant Invitations
- `POST /api/tenant-invitations`, Generate a new invitation code (requires manage_team)
- `POST /api/tenant-invitations/validate`, Check if an invitation code is valid
- `GET /api/tenant-invitations/<codeShort>`, Get invitation details
- `GET /api/tenant-invitations/tenant/<id>`, List all invitations for a tenant (requires manage_team)

### Templates (Admin Only for write operations)
- `GET /api/templates`, List all templates
- `POST /api/templates`, Create a template (Admin only)
- `GET /api/templates/<id>`, Get full template content (Admin only)
- `PUT /api/templates/<id>`, Update a template (Admin only)
- `DELETE /api/templates/<id>`, Delete a template (Admin only)

### Team
- `GET /api/team`, List all users in your tenant (with their permissions[])
- `PUT /api/team/<member_id>/permissions`, Set named permissions for a member (requires manage_team)
- `GET /api/team/targets`, List phishing targets for your tenant
- `POST /api/team/targets`, Add a phishing target (requires manage_targets)
- `DELETE /api/team/targets/<id>`, Remove a phishing target (requires manage_targets)
- `DELETE /api/team/targets/<id>/gdpr`, GDPR Art. 17 erasure: anonymize PII in campaign results then delete target (requires manage_targets)

### Tracking (public, no authentication)
- `GET /px/<token>`, Open tracking pixel (1×1 GIF)
- `GET /r/<token>`, Click tracking redirect → landing page
- `GET /secure/<token>`, Serve phishing landing page
- `POST /secure/<token>`, Record submission timestamp → redirect to /caught (no credentials stored)
- `GET /report/<token>`, Record phishing report (aware behaviour), redirect to /caught?reported=true (rate limit: 10/hour)

### Audit Logs
- `GET /api/audit-logs`, List audit log entries for your tenant
- `GET /api/audit-logs/export`, Export audit log as CSV

---

## 📚 Documentation

The `docs/` folder contains all project documentation.

| Document | Description |
|---|---|
| [Cahier des Charges](docs/Cahier_des_Charges_PhishNet.docx) | Functional requirements, MoSCoW priorities, user stories (BC02.C5) |
| [Architecture logicielle](docs/uml/architecture.png) | Layered architecture diagram, API → Service → Repository → DB |
| [Diagramme ER](docs/uml/er-diagram.png) | Database schema : 10 tables, FK constraints, indexes |
| [Wireframes](docs/wireframes.pdf) | UI mockups for all protected pages |
| [Dossier de Projet RNCP](docs/Dossier_Projet_PhishNet_RNCP37873.docx) | Project dossier for TP CDA certification, RNCP 37873 Niveau 6 |
| [Procédure de déploiement](docs/deployment.md) | Step-by-step deployment guide, Docker Compose, CI/CD, rollback, backups (BC03) |

> Each backend test class references the functional requirement(s) it validates (e.g. `EF01`, `EF08`).
> See `docs/Cahier_des_Charges_PhishNet.docx` for the full requirements table.
