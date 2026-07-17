# dzair.co

Annuaire collaboratif des sites algériens.

## Description

**dzair.co** est un annuaire en ligne regroupant les sites officiels de l'État algérien : présidence, gouvernement, ministères, wilayas, universités, organismes publics et banques, mais aussi le secteur privé. Le projet est open source et communautaire.

**Site en ligne :** [https://dzair.co](https://dzair.co)

## Fonctionnalités

- **Recherche en temps réel** — filtre instantané des liens par mot-clé
- **Catégories organisées** — Pouvoirs publics, Ministères, Institutions, Universités, Wilayas, Banques
- **Responsive** — fonctionne sur mobile, tablette et bureau
- **SEO optimisé** — Open Graph, Twitter Cards, données structurées JSON-LD
- **Analytics respectueux** — Plausible (respectueux de la vie privée)

## Technologies

- HTML5
- CSS3 (inline, variables CSS, Grid responsive)
- JavaScript vanilla (filtrage côté client)

Aucun framework, aucune dépendance, aucun outil de build.

## Structure du projet

```
dzair-co/
├── index.html      # Page principale : annuaire avec toutes les catégories
├── about.html      # Page « À propos » du projet
├── howto.html      # Guide d'utilisation
└── README.md       # Ce fichier
```

## Utilisation

1. Ouvrez `index.html` dans un navigateur
2. Ou servez le projet localement :
   ```bash
   python -m http.server 8000
   ```
3. Accédez à `http://localhost:8000`

## Contribuer

1. Forkez le dépôt
2. Créez une branche (`git checkout -b feature/nom`)
3. Modifiez `index.html` pour ajouter ou corriger des liens
4. Soumettez une Pull Request

Les contributions sont les bienvenues : ajout de liens, corrections, améliorations du design.

## Auteur

**Nazim Boudeffa** — [GitHub](https://github.com/nazimboudeffa)

## Communauté

Des sous-domaines gratuits `*.dzair.co` sont disponibles pour les membres de la communauté.

## Licence

Ce projet est open source. N'hésitez pas à contribuer.
