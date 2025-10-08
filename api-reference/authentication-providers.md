# Guide des Fournisseurs d'Authentification

MecaPy supporte maintenant différents fournisseurs d'identité OIDC/OAuth2. Cette documentation explique comment configurer votre application pour différents providers.

## Configuration Générique

### Variables d'Environnement API

```bash
# Obligatoires
AUTH_ISSUER=https://your-provider.com/
AUTH_CLIENT_SECRET=your-client-secret
AUTH_CLIENT_ID=your-client-id

# Optionnelles
AUTH_PROVIDER=generic  # keycloak, auth0, generic
AUTH_JWT_ALGORITHM=RS256
AUTH_JWKS_URI=https://custom-jwks-url.com/.well-known/jwks.json  # Override auto-discovery
```

### Variables d'Environnement SDK

```bash
# Obligatoires
MECAPY_AUTH_ISSUER=https://your-provider.com/
MECAPY_AUTH_CLIENT_ID=your-public-client-id

# Optionnelles
MECAPY_AUTH_PROVIDER=generic  # keycloak, auth0, generic
MECAPY_API_URL=https://api.mecapy.com
```

## Fournisseurs Supportés

### 1. Keycloak

**Configuration API** (`dev/env.local.keycloak`) :
```bash
AUTH_ISSUER=http://localhost:8080/realms/mecapy
AUTH_CLIENT_SECRET=your-keycloak-client-secret
AUTH_CLIENT_ID=mecapy-api
AUTH_PROVIDER=keycloak
```

**Configuration SDK** (`dev/env.local.keycloak`) :
```bash
MECAPY_AUTH_ISSUER=http://localhost:8080/realms/mecapy
MECAPY_AUTH_CLIENT_ID=mecapy-api-public
MECAPY_AUTH_PROVIDER=keycloak
```

**URLs Construites Automatiquement** :
- JWKS : `{issuer}/protocol/openid-connect/certs`
- Discovery : `{issuer}/.well-known/openid-configuration`

### 2. Auth0

**Configuration API** (`dev/env.local.auth0`) :
```bash
AUTH_ISSUER=https://your-tenant.auth0.com/
AUTH_CLIENT_SECRET=your-auth0-client-secret
AUTH_CLIENT_ID=your-auth0-client-id
AUTH_PROVIDER=auth0
```

**Configuration SDK** (`dev/env.local.auth0`) :
```bash
MECAPY_AUTH_ISSUER=https://your-tenant.auth0.com/
MECAPY_AUTH_CLIENT_ID=your-auth0-spa-client-id
MECAPY_AUTH_PROVIDER=auth0
```

**URLs Construites Automatiquement** :
- JWKS : `{issuer}/.well-known/jwks.json`
- Discovery : `{issuer}/.well-known/openid-configuration`

### 3. Fournisseur Générique

Pour tout autre fournisseur OIDC conforme aux standards :

```bash
AUTH_ISSUER=https://your-oidc-provider.com/
AUTH_CLIENT_SECRET=your-client-secret
AUTH_CLIENT_ID=your-client-id
AUTH_PROVIDER=generic
```

## Migration depuis Keycloak

Si vous utilisez l'ancienne configuration Keycloak avec `KEYCLOAK_*`, migrez vers :

**Ancien** :
```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=mecapy
KEYCLOAK_CLIENT_ID=mecapy-api
```

**Nouveau** :
```bash
AUTH_ISSUER=http://localhost:8080/realms/mecapy
AUTH_CLIENT_ID=mecapy-api
AUTH_PROVIDER=keycloak
```

## Utilisation en Développement

### Démarrer l'API avec Keycloak :
```bash
cd repos/api
ENV_FILE=dev/env.local.keycloak uv run uvicorn mecapy_api.main:app --reload
```

### Démarrer l'API avec Auth0 :
```bash
cd repos/api
ENV_FILE=dev/env.local.auth0 uv run uvicorn mecapy_api.main:app --reload
```

### Tester le SDK :
```bash
cd repos/python-sdk
ENV_FILE=dev/env.local.keycloak uv run python mecapy/auth.py
```

## Configuration Avancée

### URLs Personnalisées

Vous pouvez spécifier manuellement les endpoints OIDC :

```bash
AUTH_ISSUER=https://custom-provider.com/
AUTH_JWKS_URI=https://custom-provider.com/custom/jwks
AUTH_AUTHORIZATION_ENDPOINT=https://custom-provider.com/custom/auth
AUTH_TOKEN_ENDPOINT=https://custom-provider.com/custom/token
```

### Algorithmes de Signature

Supportés : `RS256` (par défaut), `RS384`, `RS512`, `ES256`, `ES384`, `ES512`

```bash
AUTH_JWT_ALGORITHM=ES256
```

## Dépannage

### Vérifier la Configuration
```bash
cd repos/api
uv run python test_generic_auth.py
```

### Erreurs Communes

1. **"Invalid issuer"** : Vérifiez que `AUTH_ISSUER` correspond exactement au champ `iss` du token JWT
2. **"JWKS not found"** : Vérifiez que l'URL JWKS est accessible
3. **"Invalid audience"** : Assurez-vous que `AUTH_CLIENT_ID` est dans la liste `aud` du token

### Debug JWT

Utilisez [jwt.io](https://jwt.io) pour décoder vos tokens et vérifier les champs `iss`, `aud`, `exp`.