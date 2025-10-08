# Schéma de base de données MecaPy

## Vue d'ensemble

MecaPy utilise une architecture hybride combinant :
- **Keycloak** : Gestion des utilisateurs et authentification
- **Base de données applicative** : Métadonnées et données métier
- **Scaleway Object Storage** : Stockage des fichiers

## Technologies

- **ORM** : SQLModel (SQLAlchemy + Pydantic)
- **Base de données** : PostgreSQL (recommandée) / SQLite (développement)
- **Migrations** : Alembic
- **Validation** : Pydantic v2

## Modèles de données

### Utilisateurs

#### Table `users`

```python
class User(SQLModel, table=True):
    """Utilisateur MecaPy avec référence Keycloak."""
    
    # Identifiant principal
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Référence Keycloak (unique)
    keycloak_id: str = Field(unique=True, index=True, max_length=255)
    
    # Informations utilisateur (synchronisées depuis Keycloak)
    username: str = Field(index=True, max_length=100)
    email: str = Field(index=True, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=200)
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    # Relations
    files: List["UserFile"] = Relationship(back_populates="owner")
    calculations: List["Calculation"] = Relationship(back_populates="user")
```

**Index :**
- `ix_users_keycloak_id` : Index unique sur keycloak_id
- `ix_users_username` : Index sur username
- `ix_users_email` : Index sur email

### Fichiers utilisateur

#### Table `user_files`

```python
class UserFile(SQLModel, table=True):
    """Fichiers uploadés par les utilisateurs."""
    
    # Identifiant
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Propriétaire
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Informations fichier
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_size: int = Field(ge=0)  # Taille en octets
    content_type: str = Field(max_length=100)
    
    # Stockage Scaleway
    s3_key: str = Field(unique=True, max_length=500)  # Clé S3
    s3_bucket: str = Field(max_length=100)
    s3_url: str = Field(max_length=1000)  # URL d'accès
    
    # Métadonnées
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = Field(default=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Hash pour déduplication
    file_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    
    # Relations
    owner: User = Relationship(back_populates="files")
    calculations: List["Calculation"] = Relationship(back_populates="input_files")
```

**Index :**
- `ix_user_files_user_id` : Index sur user_id
- `ix_user_files_file_hash` : Index sur file_hash
- `ix_user_files_s3_key` : Index unique sur s3_key

### Calculs scientifiques

#### Table `calculations`

```python
class Calculation(SQLModel, table=True):
    """Calculs scientifiques exécutés par les utilisateurs."""
    
    # Identifiant
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Propriétaire
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Informations calcul
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    
    # Exécution
    status: CalculationStatus = Field(default=CalculationStatus.PENDING)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Code et paramètres
    code: str = Field(max_length=10000)  # Code Python à exécuter
    parameters: Optional[str] = Field(default=None, max_length=5000)  # JSON
    
    # Résultats
    result_data: Optional[str] = Field(default=None, max_length=50000)  # JSON
    error_message: Optional[str] = Field(default=None, max_length=2000)
    execution_time: Optional[float] = Field(default=None, ge=0)  # Secondes
    
    # Ressources utilisées
    memory_used: Optional[int] = Field(default=None, ge=0)  # Mo
    cpu_time: Optional[float] = Field(default=None, ge=0)  # Secondes CPU
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    user: User = Relationship(back_populates="calculations")
    input_files: List[UserFile] = Relationship(
        link_table="calculation_files",
        back_populates="calculations"
    )


class CalculationStatus(str, Enum):
    """Statuts d'exécution des calculs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**Index :**
- `ix_calculations_user_id` : Index sur user_id
- `ix_calculations_status` : Index sur status
- `ix_calculations_created_at` : Index sur created_at

#### Table de liaison `calculation_files`

```python
class CalculationFile(SQLModel, table=True):
    """Liaison entre calculs et fichiers d'entrée."""
    __tablename__ = "calculation_files"
    
    calculation_id: int = Field(foreign_key="calculations.id", primary_key=True)
    file_id: int = Field(foreign_key="user_files.id", primary_key=True)
    
    # Métadonnées de la liaison
    added_at: datetime = Field(default_factory=datetime.utcnow)
    file_role: str = Field(max_length=50, default="input")  # input, config, etc.
```

### Outils scientifiques

#### Table `tools`

```python
class Tool(SQLModel, table=True):
    """Outils scientifiques disponibles."""
    
    # Identifiant
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Informations outil
    name: str = Field(max_length=100, unique=True)
    display_name: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    
    # Version et code
    version: str = Field(max_length=20)
    code_template: str = Field(max_length=10000)  # Template Python
    
    # Configuration Docker
    docker_image: str = Field(max_length=200)
    memory_limit: int = Field(default=256)  # Mo
    cpu_limit: float = Field(default=0.5)  # CPU cores
    timeout: int = Field(default=30)  # Secondes
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Auteur/mainteneur
    author_id: int = Field(foreign_key="users.id")
    
    # Relations
    author: User = Relationship()
    tool_versions: List["ToolVersion"] = Relationship(back_populates="tool")
```

**Index :**
- `ix_tools_name` : Index unique sur name
- `ix_tools_author_id` : Index sur author_id
- `ix_tools_is_active` : Index sur is_active

## Vues et requêtes communes

### Statistiques utilisateur

```sql
-- Statistiques par utilisateur
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT f.id) as total_files,
    COALESCE(SUM(f.file_size), 0) as total_storage_bytes,
    COUNT(DISTINCT c.id) as total_calculations,
    COUNT(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) as completed_calculations
FROM users u
LEFT JOIN user_files f ON u.id = f.user_id
LEFT JOIN calculations c ON u.id = c.user_id
GROUP BY u.id, u.username;
```

### Calculs récents

```sql
-- Calculs récents avec détails utilisateur
CREATE VIEW recent_calculations AS
SELECT 
    c.id,
    c.name,
    c.status,
    c.created_at,
    c.execution_time,
    u.username,
    u.display_name
FROM calculations c
JOIN users u ON c.user_id = u.id
ORDER BY c.created_at DESC;
```

## Migrations

### Structure Alembic

```
alembic/
├── versions/
│   ├── 001_initial_tables.py
│   ├── 002_add_calculations.py
│   └── 003_add_tools.py
├── env.py
└── alembic.ini
```

### Commandes utiles

```bash
# Générer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir à une version précédente
alembic downgrade -1

# Voir l'historique
alembic history
```

## Configuration base de données

### Variables d'environnement

```bash
# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@host:5432/mecapy

# SQLite (développement)
DATABASE_URL=sqlite:///./mecapy.db

# Pool de connexions
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### Configuration SQLModel

```python
from sqlmodel import create_engine

# Engine PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # True pour debug SQL
)

# Engine SQLite (développement)
engine = create_engine(
    "sqlite:///./mecapy.db",
    connect_args={"check_same_thread": False},
    echo=True
)
```

## Sauvegarde et restauration

### PostgreSQL

```bash
# Sauvegarde
pg_dump -h hostname -U username -d mecapy > backup.sql

# Restauration
psql -h hostname -U username -d mecapy < backup.sql

# Sauvegarde compressée
pg_dump -h hostname -U username -d mecapy | gzip > backup.sql.gz
```

### SQLite

```bash
# Sauvegarde
cp mecapy.db mecapy_backup_$(date +%Y%m%d_%H%M%S).db

# Export SQL
sqlite3 mecapy.db .dump > backup.sql
```

## Optimisations

### Index recommandés

```sql
-- Performance requêtes utilisateur
CREATE INDEX CONCURRENTLY idx_user_files_user_created 
    ON user_files(user_id, uploaded_at DESC);

-- Performance calculs
CREATE INDEX CONCURRENTLY idx_calculations_user_status_created 
    ON calculations(user_id, status, created_at DESC);

-- Recherche fichiers par hash
CREATE INDEX CONCURRENTLY idx_user_files_hash_size 
    ON user_files(file_hash, file_size);
```

### Partitioning

Pour les grandes volumes, considérer le partitioning par date :

```sql
-- Partitioning des calculs par mois
CREATE TABLE calculations_y2024m01 
    PARTITION OF calculations 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Monitoring

### Métriques à surveiller

- Taille base de données
- Nombre connexions actives
- Temps de réponse requêtes
- Locks et deadlocks
- Utilisation index

### Requêtes de surveillance

```sql
-- Connexions actives
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Requêtes lentes
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Taille tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2024-01-15