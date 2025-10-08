# FIRECRACKER SUR SCALEWAY - ANALYSE DE FAISABILITÉ

## ❌ RÉPONSE COURTE : NON, impossible sur Serverless Containers

---

## 🔍 POURQUOI FIRECRACKER NE FONCTIONNE PAS

### **Contrainte 1 : Accès KVM requis**

Firecracker nécessite un **accès direct au kernel KVM** (`/dev/kvm`)

```bash
# Firecracker a besoin de:
ls -l /dev/kvm
crw-rw-rw- 1 root kvm 10, 232 Jan 1 12:00 /dev/kvm

# Et de lancer des VMs avec:
firecracker --api-sock /tmp/firecracker.socket
```

**Dans Serverless Containers** :
- ❌ Pas d'accès `/dev/kvm` (sandboxé)
- ❌ Pas de privilèges kernel
- ❌ Runtime conteneur standard (runc/gVisor)

**Analogie** : Demander à une voiture de voler → Mauvaise catégorie de véhicule

---

### **Contrainte 2 : Nested Virtualization**

Firecracker = **Hyperviseur de niveau 1**

```
Architecture nécessaire:
┌─────────────────────────────────┐
│  Bare Metal Server (KVM)        │  ← Accès physique requis
│  ├─ Firecracker microVM 1       │
│  ├─ Firecracker microVM 2       │
│  └─ Firecracker microVM 3       │
└─────────────────────────────────┘

Scaleway Serverless Containers:
┌─────────────────────────────────┐
│  Hyperviseur Scaleway           │  ← Niveau 0 (caché)
│  └─ Container (runsc/runc)      │  ← Niveau 1 (votre code)
│      └─ Firecracker ❌          │  ← Niveau 2 (IMPOSSIBLE)
└─────────────────────────────────┘
```

**Nested virtualization** :
- Techniquement possible sur certaines plateformes (AWS Nitro, Google Cloud)
- ❌ **PAS disponible** sur Serverless Containers Scaleway
- ❌ Même sur VMs Scaleway standard, nested virt est désactivé

---

### **Contrainte 3 : Privilèges requis**

Firecracker a besoin de :

```bash
# Capabilities Linux
CAP_NET_ADMIN      # Gestion réseau TAP devices
CAP_SYS_ADMIN      # Montage filesystems
CAP_SYS_RESOURCE   # Modification limits

# Accès devices
/dev/kvm           # KVM hyperviseur
/dev/net/tun       # Network TAP

# Cgroups control
/sys/fs/cgroup/*   # Resource isolation
```

**Serverless Containers Scaleway** :
```bash
# Capabilities droppées (sécurité)
docker run --cap-drop=ALL ...

# Pas d'accès /dev
read-only filesystem (sauf /tmp)

# Pas de cgroups control
géré par la plateforme
```

---

## ✅ OÙ FIRECRACKER PEUT TOURNER

### **Option 1 : Bare Metal Servers (Scaleway Dedibox)**

```yaml
Type: Bare Metal
Accès: Root complet
KVM: ✅ Disponible
Coût: ~€15/mois (Dedibox Start-2-S-SATA)
```

**Setup** :
```bash
# Sur Dedibox
apt-get install firecracker

# Lancer microVM
firecracker --api-sock /tmp/firecracker.socket
```

**Avantages** :
- ✅ Contrôle total
- ✅ Performances maximales
- ✅ Multi-tenancy sécurisé

**Inconvénients** :
- 🔴 Gestion infra complète (vous)
- 🔴 Pas d'auto-scaling natif
- 🔴 Single point of failure

---

### **Option 2 : Scaleway Instances (VMs) avec nested virt**

❌ **PAS SUPPORTÉ actuellement**

Scaleway désactive nested virtualization sur ses instances :

```bash
# Vérification
cat /sys/module/kvm_intel/parameters/nested
N  # ← Désactivé

# Même sur instances GP1/PRO
```

**Pourquoi** :
- Sécurité multi-tenant
- Performance overhead
- Support complexe

---

### **Option 3 : AWS EC2 (si vous acceptez de sortir de l'Europe)**

```yaml
Type: EC2 Bare Metal (i3.metal, c5.metal)
KVM: ✅ Native support
Nested: ✅ Activé
Région: eu-west-3 (Paris) existe
Coût: ~€500/mois (c5.metal)
```

**AWS = Créateur de Firecracker** → Support natif

---

### **Option 4 : OVHcloud Bare Metal**

```yaml
Type: Bare Metal Servers
Région: 🇫🇷 France (Gravelines, Roubaix)
KVM: ✅ Disponible
Coût: ~€50/mois (Advance-1)
```

**Meilleure alternative européenne pour Firecracker**

---

## 🏗️ ARCHITECTURE RÉALISTE AVEC FIRECRACKER (OVH)

### **Si vous DEVEZ absolument utiliser Firecracker :**

```
┌─────────────────────────────────────────────────────┐
│  API FastAPI (Scaleway Serverless Container)       │
│  - Reçoit requêtes utilisateurs                     │
│  - Enqueue dans Redis                               │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴─────────────┐
        │                            │
┌───────▼──────────┐      ┌─────────▼────────┐
│  Redis Queue     │      │  PostgreSQL      │
│  (Scaleway)      │      │  (Scaleway)      │
└───────┬──────────┘      └──────────────────┘
        │
        │
┌───────▼────────────────────────────────────────────┐
│  OVH Bare Metal Server (Firecracker Host)          │
│  - Worker Python poll Redis                        │
│  - Lance Firecracker microVMs                      │
│  - 1 microVM = 1 calcul utilisateur                │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ MicroVM 1│  │ MicroVM 2│  │ MicroVM N│        │
│  │ Python   │  │ Python   │  │ Python   │        │
│  │ NumPy    │  │ SciPy    │  │ Custom   │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘
```

**Coût architecture hybride** :
- API + Redis + DB (Scaleway) : €40/mois
- Bare Metal OVH : €50/mois
- **Total : €90/mois**

**Complexité** : 🔴 **ÉLEVÉE** (gérer bare metal)

---

## 📊 COMPARAISON : Firecracker vs Docker-in-Docker

### **Performance**

| Métrique | Firecracker | Docker-in-Docker |
|----------|-------------|------------------|
| **Boot time** | 125ms | 2-5s |
| **Memory overhead** | 5MB | 100-200MB |
| **CPU overhead** | ~1% | ~5% |
| **Isolation** | Kernel complète (VM) | Namespace (conteneur) |

**→ Firecracker = 10-40x plus rapide**

### **Mais au prix de :**

| Aspect | Firecracker | Docker-in-Docker |
|--------|-------------|------------------|
| **Hébergement** | Bare metal only | ✅ Anywhere |
| **Gestion infra** | 🔴 Élevée | 🟢 Minimal |
| **Auto-scaling** | 🟡 Manuel | ✅ Natif (Scaleway) |
| **Coût minimum** | €50/mois (bare metal) | €40/mois (serverless) |
| **Complexité** | 🔴 Expert | 🟢 Intermédiaire |

---

## 🎯 RECOMMANDATIONS PAR SCÉNARIO

### **Scénario 1 : MVP / Solo Developer / Budget limité**

**✅ Docker-in-Docker sur Scaleway Serverless Containers**

```yaml
Raison:
  - Zéro gestion infra
  - Auto-scaling natif
  - Coût optimal
  - Overhead acceptable (2-5s pour calculs > 10s)

Coût: €40-70/mois
Complexité: 🟢 Gérable solo
```

---

### **Scénario 2 : Calculs ultra-rapides (< 5s) à haute fréquence**

**✅ Firecracker sur OVH Bare Metal**

```yaml
Raison:
  - Boot 125ms (vs 2-5s Docker)
  - Critique si calculs courts répétés

Coût: €90/mois (hybride Scaleway + OVH)
Complexité: 🔴 Nécessite expertise DevOps
```

**Setup OVH** :
```bash
# Sur bare metal OVH
apt-get install firecracker

# Worker Python
python worker.py  # Poll Redis → Lance microVMs
```

---

### **Scénario 3 : Enterprise / Haute charge / Budget confortable**

**✅ Firecracker sur AWS EC2 Bare Metal (eu-west-3 Paris)**

```yaml
Raison:
  - Support natif Firecracker (AWS = créateur)
  - Auto-scaling avec ASG
  - Monitoring avancé (CloudWatch)

Coût: €500-1000/mois
Complexité: 🟡 Managed AWS mais cher
```

**Mais perd l'avantage "provider français exclusif"**

---

## 🔥 ALTERNATIVE : gVisor (Meilleur compromis ?)

### **gVisor = Sécurité proche de Firecracker, utilisable sur Serverless**

```
gVisor = Runtime container avec syscall interception
→ Pas besoin KVM
→ Fonctionne sur Serverless Containers (avec --runtime=runsc)
```

**Architecture** :
```
Scaleway Serverless Container
  └─ Worker Python
      └─ Lance container avec gVisor runtime
          → Isolation forte (syscalls filtrés)
          → Pas de VM overhead
```

**Comparaison** :

| | Firecracker | gVisor | Docker standard |
|-|-------------|--------|-----------------|
| **Isolation** | VM (parfaite) | Syscall filter (très forte) | Namespace (forte) |
| **Boot time** | 125ms | 500ms-1s | 2-5s |
| **Overhead** | 1% | 10-20% | 5% |
| **KVM requis** | ✅ OUI | ❌ NON | ❌ NON |
| **Serverless compat** | ❌ NON | ⚠️ Possible | ✅ OUI |

**Setup gVisor sur Scaleway** :
```dockerfile
# Dockerfile worker
FROM google/gvisor-runsc:latest

# Worker lance containers avec --runtime=runsc
CMD ["python", "worker.py"]
```

```python
# worker.py
container = docker_client.containers.run(
    image='python:3.12',
    runtime='runsc',  # gVisor runtime
    ...
)
```

**Limites** :
- ⚠️ Scaleway peut bloquer runtime custom
- ⚠️ Besoin de tester compatibilité

---

## ✅ DÉCISION FINALE

### **Pour votre cas (développeur solo, provider français) :**

#### **Phase 1 (MVP) : Docker-in-Docker** 🏆
```
Scaleway Serverless Containers + Docker-in-Docker
Coût: €40-70/mois
Overhead: 2-5s (acceptable)
Gestion: Minimal
```

#### **Phase 2 (Si performance critique) : OVH Bare Metal + Firecracker**
```
API Scaleway + Worker OVH Bare Metal avec Firecracker
Coût: €90/mois
Overhead: 125ms
Gestion: Élevée (mais faisable)
```

#### **Alternative explorée : gVisor**
```
Tester gVisor runtime sur Scaleway Serverless
Si compatible → meilleur des deux mondes
```

---

## 📋 CHECKLIST DÉCISION

**Utilisez Firecracker SI :**
- ✅ Calculs très courts (< 5s) répétés
- ✅ Budget > €100/mois
- ✅ Expertise DevOps bare metal
- ✅ Besoin performance ultime

**Utilisez Docker-in-Docker SI :**
- ✅ Développeur solo
- ✅ Budget limité (< €100/mois)
- ✅ Calculs > 10s (overhead négligeable)
- ✅ Veut se concentrer sur le produit

---

**🎯 VERDICT : Docker-in-Docker pour démarrer, Firecracker seulement si vraiment nécessaire plus tard**

**Document généré le** : 2025-09-30
**Version** : 1.0 - Analyse Firecracker faisabilité
