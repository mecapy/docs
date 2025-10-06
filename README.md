# MecaPy Documentation

Documentation officielle de la plateforme MecaPy, hébergée sur [Mintlify](https://mintlify.com).

## 🚀 Développement local

### Installation

```bash
npm install -g mintlify
```

### Lancer le serveur de développement

```bash
mintlify dev
```

Ouvre automatiquement votre navigateur sur `http://localhost:3000`.

## 📁 Structure

```
docs/
├── mint.json                 # Configuration Mintlify
├── introduction.mdx          # Page d'accueil
├── quickstart.mdx           # Guide de démarrage rapide
├── manifest/                # Documentation du manifest
│   ├── overview.mdx
│   ├── syntax.mdx
│   ├── handlers.mdx
│   ├── schemas.mdx
│   └── examples.mdx
└── api-reference/           # Référence API
    └── introduction.mdx
```

## 🎨 Composants Mintlify

### Cards

```mdx
<CardGroup cols={2}>
  <Card title="Titre" icon="rocket" href="/lien">
    Description
  </Card>
</CardGroup>
```

### Accordions

```mdx
<AccordionGroup>
  <Accordion title="Question">
    Réponse
  </Accordion>
</AccordionGroup>
```

### Tabs

```mdx
<Tabs>
  <Tab title="Tab 1">
    Contenu 1
  </Tab>
  <Tab title="Tab 2">
    Contenu 2
  </Tab>
</Tabs>
```

### Notes & Warnings

```mdx
<Note>Message informatif</Note>
<Warning>Message d'avertissement</Warning>
<Tip>Conseil utile</Tip>
<Info>Information</Info>
```

### Code Groups

```mdx
<CodeGroup>
```yaml mecapy.yml
name: example
```

```python code.py
def hello():
    print("Hello")
```
</CodeGroup>
```

## 📝 Contribuer

1. Modifier les fichiers `.mdx`
2. Tester localement avec `mintlify dev`
3. Commit et push

Les changements seront automatiquement déployés sur la documentation en ligne.

## 🔗 Liens utiles

- [Mintlify Documentation](https://mintlify.com/docs)
- [MecaPy Website](https://mecapy.com)
- [MecaPy API](https://api.mecapy.com)
- [Dashboard](https://app.mecapy.com)

## 📧 Support

Pour toute question : [support@mecapy.com](mailto:support@mecapy.com)
