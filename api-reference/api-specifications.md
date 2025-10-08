# Spécifications API MecaPy

## Vue d'ensemble

L'API MecaPy est construite avec FastAPI et fournit des services d'authentification, upload de fichiers, et calculs scientifiques sécurisés.

## Base URL

- **Production** : `https://api.mecapy.com`
- **Développement** : `http://localhost:8000`

## Authentification

### OAuth2 + PKCE via Keycloak

L'API utilise OAuth2 avec PKCE (Proof Key for Code Exchange) pour l'authentification sécurisée :

- **Authorization Server** : Keycloak
- **Realm** : `mecapy`
- **Client ID** : `mecapy-api`
- **Grant Type** : Authorization Code with PKCE
- **Token Type** : JWT (RS256)

### Headers requis

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Endpoints

### Authentification

#### `POST /auth/login`

Initie le processus d'authentification OAuth2.

**Réponse :**
```json
{
  "authorization_url": "https://keycloak.mecapy.com/auth/realms/mecapy/protocol/openid-connect/auth?...",
  "code_verifier": "generated_pkce_verifier"
}
```

#### `POST /auth/callback`

Traite le callback OAuth2 et échange le code d'autorisation contre un token.

**Corps de la requête :**
```json
{
  "code": "authorization_code",
  "code_verifier": "pkce_verifier"
}
```

**Réponse :**
```json
{
  "access_token": "jwt_token",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token"
}
```

### Upload de fichiers

#### `POST /upload`

🔐 **Requiert authentification**

Upload un fichier vers Scaleway Object Storage.

**Corps de la requête :** `multipart/form-data`
- `file`: Fichier à uploader

**Réponse :**
```json
{
  "filename": "example.pdf",
  "file_url": "https://mecapy-uploads.s3.fr-par.scw.cloud/user123/example.pdf",
  "file_size": 1024,
  "upload_timestamp": "2024-01-15T10:30:00Z"
}
```

### Utilitaires

#### `GET /`

Endpoint racine avec informations sur l'API.

**Réponse :**
```json
{
  "message": "Bienvenue sur l'API MecaPy",
  "status": "running",
  "version": "1.0.0"
}
```

#### `GET /health`

Health check pour monitoring.

**Réponse :**
```json
{
  "status": "ok"
}
```

#### `GET /docs`

Documentation OpenAPI interactive (Swagger UI).

#### `GET /redoc`

Documentation OpenAPI alternative (ReDoc).

## Modèles de données

### Utilisateur JWT

```json
{
  "sub": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "preferred_username": "jocelyn.lopez",
  "email": "jocelyn.lopez@mecapy.com",
  "given_name": "Jocelyn",
  "family_name": "LOPEZ",
  "realm_access": {
    "roles": ["user", "scientist"]
  },
  "exp": 1642248600,
  "iat": 1642245000,
  "iss": "https://keycloak.mecapy.com/realms/mecapy"
}
```

### Erreurs

```json
{
  "detail": "Description de l'erreur",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Codes de statut HTTP

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (token manquant/invalide)
- `403` - Forbidden (permissions insuffisantes)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Sécurité

### Validation JWT

- **Algorithme** : RS256
- **Vérification signature** : Clés publiques JWKS
- **Vérification expiration** : Obligatoire
- **Vérification audience** : `mecapy-api`
- **Vérification issuer** : `https://keycloak.mecapy.com/realms/mecapy`

### Headers de sécurité

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

### CORS

- **Origins autorisées** : `https://mecapy.com`
- **Méthodes** : `GET, POST, PUT, DELETE, OPTIONS`
- **Headers** : `Content-Type, Authorization`
- **Credentials** : Autorisées

## Rate Limiting

*À implémenter* : Limites par utilisateur et endpoint.

## Versioning

Versioning via header `Accept` :

```http
Accept: application/vnd.mecapy.v1+json
```

## Pagination

*À implémenter* pour les endpoints retournant des listes :

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

## Exemples d'utilisation

### JavaScript/TypeScript

```typescript
// Authentification
const loginResponse = await fetch('/auth/login', {
  method: 'POST'
});
const { authorization_url, code_verifier } = await loginResponse.json();

// Redirection vers Keycloak
window.location.href = authorization_url;

// Après callback, échanger le code
const tokenResponse = await fetch('/auth/callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code, code_verifier })
});
const { access_token } = await tokenResponse.json();

// Upload avec token
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});
```

### Python

```python
import httpx

# Client authentifié
class MecaPyClient:
    def __init__(self, base_url: str, token: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={'Authorization': f'Bearer {token}'}
        )
    
    async def upload_file(self, file_path: Path) -> dict:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await self.client.post('/upload', files=files)
            return response.json()
```

## Monitoring et observabilité

### Logs

- **Format** : JSON structuré
- **Niveau** : INFO en production, DEBUG en développement
- **Contenu** : Request ID, User ID, endpoint, durée, status code

### Métriques

*À implémenter* avec Prometheus :

- Temps de réponse par endpoint
- Nombre de requêtes par statut HTTP
- Taux d'erreur d'authentification
- Utilisation du stockage

### Health checks

- `/health` : Status API
- Vérification connectivité Keycloak
- Vérification connectivité Scaleway Object Storage
- Vérification base de données

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2024-01-15