# Configuration Keycloak pour l'API MecaPy

Ce document décrit les étapes manuelles nécessaires pour configurer Keycloak afin qu'il puisse être utilisé avec l'API MecaPy.

## Prérequis

- Keycloak installé et en cours d'exécution (version 21.0.0 ou supérieure recommandée)
- Accès à l'interface d'administration de Keycloak

## 1. Création du realm

1. Connectez-vous à l'interface d'administration de Keycloak (http://localhost:8080/admin)
2. Cliquez sur le bouton "Create realm" dans le menu déroulant en haut à gauche
3. Entrez "mecapy" comme nom du realm
4. Cliquez sur "Create"

### Configuration de l'auto-registration

Pour permettre aux utilisateurs de créer un compte depuis le frontend :

1. Dans le realm "mecapy", allez dans "Realm settings" > "Login"
2. Activez les options suivantes :
   - ✅ **User registration** : `ON` (permet aux utilisateurs de s'inscrire)
   - ✅ **Forgot password** : `ON` (reset de mot de passe)
   - ✅ **Remember me** : `ON` (session persistante)
   - ✅ **Verify email** : `ON` (vérification email obligatoire)
   - ✅ **Login with email** : `ON` (connexion avec email ou username)

3. Configurez les paramètres email dans "Realm settings" > "Email" :
   - **From** : `noreply@mecapy.com`
   - **From display name** : `MecaPy`
   - **Host** : Votre serveur SMTP
   - **Port** : 587 (ou 465 pour SSL)
   - **Authentication** : `ON`
   - **Username/Password** : Vos identifiants SMTP

### Attribution automatique du rôle "user"

Pour que tous les nouveaux utilisateurs reçoivent automatiquement le rôle "user" :

1. Dans le realm "mecapy", allez dans "Realm settings" > "User registration"
2. Cliquez sur "Default roles" (ou "Roles" selon la version)
3. Cliquez sur "Assign role"
4. Sélectionnez "Filter by realm roles"
5. Cochez le rôle **"user"**
6. Cliquez sur "Assign"

## 2. Configuration des clients

### 2.1. Client API confidentiel (pour l'API backend)

1. Dans le realm "mecapy", allez dans le menu "Clients" dans la barre latérale
2. Cliquez sur "Create client"
3. Configurez le client avec les paramètres suivants:
   - Client ID: `mecapy-api`
   - Name: `MecaPy API Backend`
   - Description: `Client confidentiel pour l'API MecaPy (validation des tokens)`
   - Always display in UI : `ON`
   - Enabled: `ON`
   - Client authentication: `ON` (client confidentiel)
   - Authorization: `OFF`
   - Authentication flow:
     - Standard flow: `ON` (pour le flux Authorization Code)
     - Direct access grants: `OFF` (pas utilisé par le backend)
     - Implicit flow: `OFF`
     - Service accounts roles: `ON` (pour l'authentification client-to-client)
4. Cliquez sur "Next"
5. Configurez les paramètres d'accès:

   **Pour le développement local:**
   - Root URL: `http://localhost:8000`
   - Valid redirect URIs: `http://localhost:8000/*`
   - Web origins: `http://localhost:8000`

   **Pour la production (domaine mecapy.com):**
   - Root URL: `https://api.mecapy.com`
   - Home URL: Laisser vide (car API)
   - Valid redirect URIs: 
     ```
     https://api.mecapy.com/auth/callback
     https://api.mecapy.com/oauth/callback
     ```
   - Web origins: 
     ```
     https://api.mecapy.com
     ```

   **⚠️ Note de sécurité:** En production, évitez les wildcards (`*`) dans les Valid redirect URIs. Préférez des URLs explicites pour limiter la surface d'attaque et respecter le principe de moindre privilège. Les URLs explicites sont plus sécurisées que `https://api.mecapy.com/*` qui autoriserait toutes les URLs sous ce domaine.

6. Cliquez sur "Save"

### 2.2. Client API public (pour les utilisateurs finaux)

Ce client permet aux utilisateurs finaux d'obtenir des tokens directement pour utiliser votre API.

1. Dans le realm "mecapy", allez dans le menu "Clients"
2. Cliquez sur "Create client"
3. Configurez le client avec les paramètres suivants:
   - Client ID: `mecapy-api-public`
   - Name: `MecaPy API Public`
   - Description: `Client public pour l'accès direct des utilisateurs à l'API`
   - Always display in UI: `ON`
   - Enabled: `ON`
   - Client authentication: `OFF` (client public - pas de secret)
   - Authorization: `OFF`
   - Authentication flow:
     - Standard flow: `OFF` (pas nécessaire pour l'accès direct)
     - Direct access grants: `ON` (ESSENTIEL - permet le grant_type=password)
     - Implicit flow: `OFF`
     - Service accounts roles: `OFF`
4. Cliquez sur "Next"
5. Configurez les paramètres d'accès:
   - Laissez tous les champs vides (Root URL, Valid redirect URIs, etc.)
   - Ce client ne nécessite pas de configuration d'URLs car il est utilisé uniquement pour l'authentification directe
6. Cliquez sur "Save"

**⚠️ Avantages du client public :**
- ✅ **Pas de secret à partager** avec les utilisateurs finaux
- ✅ **Plus sécurisé** que de distribuer un client secret
- ✅ **Simplifie l'intégration** pour les développeurs tiers
- ✅ **Conforme aux bonnes pratiques** OAuth2 pour les clients publics

## 3. Configuration des secrets du client

1. Allez dans l'onglet "Credentials" du client
2. Vérifiez que "Client Authenticator" est sur "Client Id and Secret" (recommandé pour ce projet)
3. Notez le "Client secret" généré (vous en aurez besoin pour configurer l'API)
4. Si nécessaire, vous pouvez régénérer le secret en cliquant sur "Regenerate"

**⚠️ Note importante sur le Client Authenticator :**

Le "Client Authenticator" définit comment votre API s'authentifie auprès de Keycloak, ce qui est différent de l'authentification des utilisateurs :

- **Client Authenticator** = Comment le **client** (votre API) s'authentifie auprès de Keycloak
- **JWT tokens** = Comment les **utilisateurs** s'authentifient auprès de votre API

**Pourquoi "Client Id and Secret" est approprié :**
- ✅ **Simplicité** : Plus facile à configurer et maintenir
- ✅ **Compatibilité** : Fonctionne avec tous les flux OAuth2/OIDC
- ✅ **Sécurité suffisante** : Le secret est stocké de manière sécurisée côté serveur
- ✅ **Sécurité JWT optimale** : Votre API utilise déjà JWT RS256 avec validation JWKS pour l'authentification des utilisateurs

Les alternatives comme "Signed JWT" sont recommandées pour des environnements hautement sécurisés (banque, santé) ou des architectures microservices distribuées, mais ne sont pas nécessaires pour ce projet.

## 4. Configuration des mappers de protocole

Pour s'assurer que les tokens contiennent toutes les informations nécessaires:

1. Allez dans l'onglet "Client scopes" du client (Clients->mecapy-api-->Client scopes)
2. Vérifiez que les scopes suivants sont assignés comme "Default" :
   - `profile` (pour given_name, family_name)
   - `email` (pour l'email)
   - `roles` (pour les rôles)
3. Vérifiez que les mappers suivants existent (sinon, créez-les) :

   a. Mapper pour les rôles de realm (CRITIQUE pour l'autorisation):
   - Nom: `realm roles`
   - Mapper type: `User Realm Role`
   - Multivalued: `ON`
   - Token Claim Name: `realm_access.roles`
   - Claim JSON Type: `String`
   - Add to ID token: `ON`
   - Add to access token: `ON`
   - Add to userinfo: `ON`
   - Add to lightweight access token: `ON` (essentiel pour l'autorisation)
   - Add to token introspection: `ON` (nécessaire pour valider les permissions)

   b. Mapper pour le nom d'utilisateur (IMPORTANT pour l'identification):
   - Nom: `username`
   - Mapper type: `User Property`
   - Property: `username`
   - Token Claim Name: `preferred_username`
   - Claim JSON Type: `String`
   - Add to ID token: `ON`
   - Add to access token: `ON`
   - Add to userinfo: `ON`
   - Add to lightweight access token: `ON` (utile pour l'identification)
   - Add to token introspection: `ON` (utile pour les logs/audit)

   c. Mapper pour l'email (MODÉRÉ):
   - Nom: `email`
   - Mapper type: `User Property`
   - Property: `email`
   - Token Claim Name: `email`
   - Claim JSON Type: `String`
   - Add to ID token: `ON`
   - Add to access token: `ON`
   - Add to userinfo: `ON`
   - Add to lightweight access token: `OFF` (non critique pour l'autorisation)
   - Add to token introspection: `ON` (utile pour l'identification)

   d. Mapper pour le prénom (OPTIONNEL):
   - Nom: `given name`
   - Mapper type: `User Property`
   - Property: `firstName`
   - Token Claim Name: `given_name`
   - Claim JSON Type: `String`
   - Add to ID token: `ON`
   - Add to access token: `ON`
   - Add to userinfo: `ON`
   - Add to lightweight access token: `OFF` (non critique)
   - Add to token introspection: `OFF` (non nécessaire pour la validation)

   e. Mapper pour le nom de famille (OPTIONNEL):
   - Nom: `family name`
   - Mapper type: `User Property`
   - Property: `lastName`
   - Token Claim Name: `family_name`
   - Claim JSON Type: `String`
   - Add to ID token: `ON`
   - Add to access token: `ON`
   - Add to userinfo: `ON`
   - Add to lightweight access token: `OFF` (non critique)
   - Add to token introspection: `OFF` (non nécessaire pour la validation)

### Explication des champs supplémentaires

**Add to lightweight access token :**
- Les "lightweight access tokens" sont des tokens d'accès optimisés pour la performance
- Ils contiennent moins d'informations pour réduire la taille et améliorer les performances
- ✅ **ON** pour les claims essentiels à l'autorisation (rôles, username)
- ❌ **OFF** pour les informations non critiques (email, prénom, nom)

**Add to token introspection :**
- L'endpoint d'introspection (`/token/introspect`) permet de vérifier la validité d'un token
- Retourne les métadonnées du token (validité, expiration, claims, etc.)
- ✅ **ON** pour les claims nécessaires à la validation et autorisation
- ❌ **OFF** pour les informations purement cosmétiques

**Résumé des recommandations :**

| Mapper | Lightweight | Introspection | Justification |
|--------|-------------|---------------|---------------|
| **realm roles** | ✅ ON | ✅ ON | Critique pour l'autorisation |
| **username** | ✅ ON | ✅ ON | Important pour l'identification |
| **email** | ❌ OFF | ✅ ON | Utile mais non critique |
| **given name** | ❌ OFF | ❌ OFF | Décoratif uniquement |
| **family name** | ❌ OFF | ❌ OFF | Décoratif uniquement |

Cette configuration optimise les performances tout en conservant toutes les informations nécessaires pour votre API MecaPy.

## 5. Configuration des rôles

1. Allez dans le menu "Realm roles" dans la barre latérale
2. Créez les rôles suivants:
   - Cliquez sur "Create role"
   - Nom: `admin`
   - Description: `Administrateur avec accès complet`
   - Cliquez sur "Save"

   - Cliquez sur "Create role"
   - Nom: `user`
   - Description: `Utilisateur standard`
   - Cliquez sur "Save"

## 6. Création d'utilisateurs de test

### Utilisateur admin

1. Allez dans le menu "Users" dans la barre latérale
2. Cliquez sur "Add user"
3. Configurez l'utilisateur:
   - Username: `admin`
   - Email: `admin@mecapy.com`
   - First name: `Jocelyn`
   - Last name: `LOPEZ`
   - Email verified: `ON`
   - Enabled: `ON`
4. Cliquez sur "Create"
5. Allez dans l'onglet "Credentials" de l'utilisateur
6. Cliquez sur "Set password"
7. Entrez un mot de passe et désactivez "Temporary" si vous ne voulez pas que l'utilisateur change son mot de passe à la première connexion
8. Allez dans l'onglet "Role mapping" de l'utilisateur
9. Cliquez sur "Assign role" puis "Filter by realm roles"
10. Sélectionnez le rôle "admin" et cliquez sur "Assign"

### Utilisateur standard

1. Allez dans le menu "Users" dans la barre latérale
2. Cliquez sur "Add user"
3. Configurez l'utilisateur:
   - Username: `user`
   - Email: `user@example.com`
   - First name: `Standard`
   - Last name: `User`
   - Email verified: `ON`
   - Enabled: `ON`
4. Cliquez sur "Create"
5. Allez dans l'onglet "Credentials" de l'utilisateur
6. Cliquez sur "Set password"
7. Entrez un mot de passe et désactivez "Temporary" si vous ne voulez pas que l'utilisateur change son mot de passe à la première connexion
8. Allez dans l'onglet "Role mapping" de l'utilisateur
9. Cliquez sur "Assign role" puis "Filter by realm roles"
10. Sélectionnez le rôle "user" et cliquez sur "Assign"

## 7. Configuration des variables d'environnement de l'API

Une fois Keycloak configuré, vous devez configurer l'API avec les informations appropriées:

**Pour le développement local:**
```
CC_KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=mecapy
KEYCLOAK_CLIENT_ID=mecapy-api
KEYCLOAK_CLIENT_SECRET=<votre-client-secret-dev>
```

**Pour la production:**
```
CC_KEYCLOAK_URL=https://auth.mecapy.com
KEYCLOAK_REALM=mecapy
KEYCLOAK_CLIENT_ID=mecapy-api
KEYCLOAK_CLIENT_SECRET=<votre-client-secret-production>
```

**⚠️ Important:** Utilisez toujours HTTPS en production pour la sécurité des tokens d'authentification.

## 8. Test de la configuration

### 8.1. Test pour les utilisateurs finaux (client public)

Pour que vos utilisateurs obtiennent un token d'authentification :

**Développement local :**
```bash
curl -X POST \
  http://localhost:8080/realms/mecapy/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=mecapy-api-public' \
  -d 'username=user@example.com' \
  -d 'password=<mot-de-passe>'
```

**Production :**
```bash
curl -X POST \
  https://auth.mecapy.com/realms/mecapy/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=mecapy-api-public' \
  -d 'username=user@example.com' \
  -d 'password=<mot-de-passe>'
```

**⚠️ Avantages de cette approche :**
- ✅ **Pas de client_secret** à gérer côté utilisateur
- ✅ **Plus sécurisé** pour l'accès public à votre API
- ✅ **Facilite l'intégration** pour les développeurs tiers

### 8.2. Test avec le token obtenu

Utilisez le token obtenu pour accéder à un endpoint protégé de l'API:

**Développement local :**
```bash
curl -X GET \
  http://localhost:8000/auth/me \
  -H 'Authorization: Bearer <votre-token>'
```

**Production :**
```bash
curl -X GET \
  https://api.mecapy.com/auth/me \
  -H 'Authorization: Bearer <votre-token>'
```

### 8.3. Test pour l'API backend (client confidentiel)

Cette méthode est utilisée par votre API backend pour valider les tokens (pas par les utilisateurs finaux) :

```bash
curl -X POST \
  https://auth.mecapy.com/realms/mecapy/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=mecapy-api' \
  -d 'client_secret=<votre-secret-client>' \
  -d 'username=user' \
  -d 'password=<votre-password>'
```

Si tout est correctement configuré, vous devriez recevoir les informations de l'utilisateur en réponse.

## 9. Configuration du client Frontend

### Création du client frontend (dashboard)

1. Dans le realm "mecapy", allez dans le menu "Clients"
2. Cliquez sur "Create client"
3. Configurez le client avec les paramètres suivants:
   - Client ID: `mecapy-dashboard`
   - Name: `MecaPy Dashboard`
   - Description: `Client pour l'application dashboard MecaPy`
   - Always display in UI: `ON`
   - Enabled: `ON`
   - Client authentication: `OFF` (client public)
   - Authorization: `OFF`
   - Authentication flow:
     - Standard flow: `ON` (Authorization Code + PKCE)
     - Direct access grants: `OFF` (pas recommandé pour SPA)
     - Implicit flow: `OFF` (obsolète et non sécurisé)
     - Service accounts roles: `OFF`
4. Cliquez sur "Next"
5. Configurez les paramètres d'accès:

   **Pour le développement local:**
   - Root URL: `http://localhost:3000`
   - Valid redirect URIs: `http://localhost:3000/auth/callback`
   - Valid post logout redirect URIs: `http://localhost:3000`
   - Web origins: `http://localhost:3000`

   **Pour la production:**
   - Root URL: `https://dashboard.mecapy.com`
   - Valid redirect URIs: `/auth/callback`
   - Valid post logout redirect URIs: `+`
   - Web origins: `+`

6. Cliquez sur "Save"

### Configuration avancée du client frontend

1. Allez dans l'onglet "Settings" du client `mecapy-dashboard`
2. Configurez les paramètres avancés:
   - **Proof Key for Code Exchange Code Challenge Method**: `S256` (obligatoire pour PKCE)
   - **Access Token Lifespan**: `5 minutes` (courte durée pour la sécurité)
   - **Client Session Idle**: `30 minutes`
   - **Client Session Max**: `12 hours`

### Configuration des Client Scopes

1. Allez dans l'onglet "Client scopes" du client `mecapy-dashboard`
2. Assignez les scopes suivants comme "Default":
   - ✅ **email** (pour l'email utilisateur)
   - ✅ **profile** (pour prénom, nom, username)
   - ✅ **roles** (pour les rôles utilisateur)
   - ✅ **web-origins** (pour CORS, généralement auto-assigné)

**Note :** Le scope `openid` est automatiquement inclus par Keycloak pour tous les clients OIDC, c'est pourquoi il n'apparaît pas dans la liste des scopes disponibles.

### Variables d'environnement pour le frontend (dashboard)

**Pour le développement local:**
```env
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=mecapy
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=mecapy-dashboard
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000/auth/callback
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Pour la production:**
```env
NEXT_PUBLIC_KEYCLOAK_URL=https://auth.mecapy.com
NEXT_PUBLIC_KEYCLOAK_REALM=mecapy
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=mecapy-dashboard
NEXT_PUBLIC_REDIRECT_URI=https://dashboard.mecapy.com/auth/callback
NEXT_PUBLIC_API_URL=https://api.mecapy.com
```

### Architecture de sécurité

L'architecture MecaPy utilise **3 clients Keycloak distincts** pour différents cas d'usage :

#### 1. Client API Public (`mecapy-api-public`)
**Usage :** Utilisateurs finaux et développeurs tiers accédant directement à l'API
- ✅ Client public (pas de secret)
- ✅ Grant type `password` activé
- ✅ Sécurisé pour la distribution publique
- ✅ Simplifie l'intégration pour les développeurs

**Flow d'authentification :**
```
Utilisateur final → Keycloak (avec username/password)
                 ← Token d'accès (sans client secret)
Utilisateur final → API MecaPy (avec token)
```

#### 2. Client API Backend (`mecapy-api`)
**Usage :** Votre API backend pour valider et gérer les tokens
- 🔒 Client confidentiel (avec secret)
- 🔒 Validation des tokens JWT via JWKS
- 🔒 Gestion des permissions et autorisations
- 🔒 Service accounts pour les opérations internes

#### 3. Client Dashboard (`mecapy-dashboard`)
**Usage :** Application frontend web (SPA)
- ✅ Client public sans secret
- ✅ PKCE pour sécuriser le flow Authorization Code
- ✅ Tokens stockés en mémoire (pas en localStorage)
- ✅ Auto-refresh des tokens

**Flow d'authentification Dashboard :**
```
1. Dashboard → Keycloak (pages de login/signup)
2. Keycloak → Dashboard (code d'autorisation + PKCE)
3. Dashboard → Keycloak (échange code contre tokens avec PKCE)
4. Dashboard → API (requêtes avec access token)
5. API → Keycloak (validation via JWKS)
```

#### Résumé des cas d'usage

| Client | Type | Usage | Avantages |
|--------|------|-------|-----------|
| `mecapy-api-public` | Public | Utilisateurs finaux | Pas de secret à partager |
| `mecapy-api` | Confidentiel | Backend API | Sécurité maximale |
| `mecapy-dashboard` | Public | Frontend SPA | PKCE + sécurité web |

Cette architecture offre **flexibilité** et **sécurité** pour tous les modes d'accès à votre API.


