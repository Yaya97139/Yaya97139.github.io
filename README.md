# 🚀 Portfolio — Yannis MONDUC

Portfolio technique en ligne, déployé via **GitHub Pages**.  
**URL cible :** `https://yannis-monduc.github.io`

---

## 📁 Structure du projet

```
Portfolio/
├── index.html          # Page principale du portfolio
├── style.css           # Styles (dark theme, responsive)
├── script.js           # Animations, particules, QR code
├── CV_Yannis_MONDUC.pdf  # ← Ajouter votre CV ici
└── README.md
```

---

## 🛠️ Mise en ligne — GitHub Pages (étape par étape)

### 1. Créer le dépôt GitHub

1. Aller sur [github.com](https://github.com) → **New repository**
2. Nom du dépôt : **`yannis-monduc.github.io`** (exactement ce format)
3. Visibilité : **Public**
4. Ne pas initialiser avec README
5. Cliquer **Create repository**

### 2. Uploader les fichiers

**Option A — Interface web (plus simple) :**
1. Sur la page du dépôt vide → cliquer **uploading an existing file**
2. Glisser-déposer tous les fichiers du dossier `Portfolio/`
3. Commit message : `Initial portfolio deployment`
4. Cliquer **Commit changes**

**Option B — Git (terminal) :**
```bash
cd "d:/Stage  IEMN + Projets/Portfolio"
git init
git remote add origin https://github.com/yannis-monduc/yannis-monduc.github.io.git
git add .
git commit -m "Initial portfolio deployment"
git branch -M main
git push -u origin main
```

### 3. Activer GitHub Pages

1. Aller dans le dépôt → **Settings** → **Pages** (menu gauche)
2. Source : **Deploy from a branch**
3. Branch : **main** / **(root)**
4. Cliquer **Save**
5. Attendre 1-2 minutes → le site sera disponible à `https://yannis-monduc.github.io`

---

## 📄 Ajouter votre CV

Placez votre CV au format PDF dans ce dossier sous le nom :
```
CV_Yannis_MONDUC.pdf
```
Il sera téléchargeable via le bouton du portfolio.

---

## 📷 Ajouter votre photo

Dans `index.html`, remplacer le bloc `photo-placeholder` :
```html
<!-- Remplacer ceci : -->
<div class="photo-placeholder">
  <i class="fas fa-user"></i>
  <span>Photo</span>
</div>

<!-- Par ceci : -->
<img src="photo.jpg" alt="Yannis MONDUC" />
```
Puis placer `photo.jpg` dans le dossier `Portfolio/`.

---

## 🔗 QR Code

Le QR code est généré automatiquement et pointe vers `https://yannis-monduc.github.io`.

**Pour l'intégrer dans votre CV :**
1. Une fois le site en ligne, ouvrir la section Contact du portfolio
2. Faire un screenshot du QR code affiché
3. Insérer l'image dans votre CV (Word/LaTeX) avec la légende :
   *"Scanner pour accéder à mon portfolio complet"*

Ou générer un QR code haute résolution sur [qr-code-generator.com](https://www.qr-code-generator.com) avec l'URL `https://yannis-monduc.github.io`.

---

## 🔧 Personnaliser le portfolio

### Changer l'URL GitHub dans le QR code
Dans `script.js`, ligne ~95 :
```js
const portfolioURL = 'https://yannis-monduc.github.io';
```

### Ajouter des liens GitHub vers vos projets
Dans `index.html`, chercher :
```html
href="https://github.com/yannis-monduc/uwb-indoor-localization"
```
Remplacer par l'URL réelle de vos dépôts GitHub.

### Ajouter des captures d'écran de projets
Dans chaque `.project-card`, ajouter avant `<p class="project-desc">` :
```html
<img src="assets/projet-uwb.png" alt="Système UWB" class="project-img" />
```

---

## ✅ Checklist avant déploiement

- [ ] Ajouter `CV_Yannis_MONDUC.pdf` dans le dossier
- [ ] Ajouter `photo.jpg` et mettre à jour `index.html`
- [ ] Créer le dépôt `yannis-monduc.github.io` sur GitHub
- [ ] Uploader tous les fichiers
- [ ] Activer GitHub Pages dans les Settings
- [ ] Vérifier que `https://yannis-monduc.github.io` fonctionne
- [ ] Mettre à jour les liens GitHub des projets dans `index.html`
- [ ] Générer le QR code final et l'intégrer au CV

---

## 📬 Contact

**Yannis MONDUC** — monducyannis97@gmail.com  
[linkedin.com/in/yannis-monduc](https://www.linkedin.com/in/yannis-monduc)
