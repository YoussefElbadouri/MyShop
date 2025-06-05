# 🛍️ MyShop 

**MyShop** est une application web simple de e-commerce développée avec **Flask**

---

## ⚙️ Installation (sur une instance Ubuntu EC2)

### 1. Cloner le dépôt

```bash
git clone https://github.com/YoussefElbadouri/MyShop.git
cd MyShop/setup
```

### 2. Donner les droits d'exécution au script et l'exécuter

```bash
chmod +x setup_MyShop.sh
./setup_MyShop.sh
```

Ce script va :
- Installer les dépendances système (Python, pip, MySQL, etc.)
- Créer un environnement virtuel
- Installer les packages Python (`requirements.txt`)
- Créer la base de données `MyShop` avec les tables `users` et `otp_flows`
- Générer les fichiers `config.py` et `products.xml`
- Créer le service systemd `myshop.service` et lancer l'application

---

## 📧 Configuration Email

Dans `config.py`, configure les variables suivantes :

```python
EMAIL_ADDRESS = "votre-email@gmail.com"
EMAIL_PASSWORD = "votre-mot-de-passe-d'application"
```

🔐 **Pour Gmail**, créez un mot de passe d'application ici :  
https://myaccount.google.com/apppasswords

---

## 🌐 Accéder à l'application

Accédez à votre instance EC2 via navigateur :

```
http://<votre-ip-ec2>:5000
```

⚠️ **Assurez-vous que le port 5000 est ouvert dans votre groupe de sécurité AWS.**

---

## 🛠️ Gestion du service systemd

```bash
sudo systemctl status myshop      # Voir l'état du service
sudo systemctl restart myshop     # Redémarrer le service
sudo systemctl stop myshop        # Arrêter le service
```

---

## 📁 Structure du projet

```
MyShop/
├── app.py                    # Application Flask principale
├── config.py                # Configuration de l'application
├── products.xml             # Base de données des produits
├── requirements.txt         # Dépendances Python
├── setup.sh                # Script d'installation automatique
├── templates/              # Templates HTML
└── static/                 # Fichiers CSS/JS/Images
```

---

## 🚀 Fonctionnalités

- **Authentification** : Inscription, connexion, déconnexion
- **Gestion des rôles** : Utilisateur standard et administrateur
- **Récupération de mot de passe** : OTP envoyé par email
- **Catalogue produits** : Affichage et gestion des produits
- **Interface admin** : Gestion complète des produits et utilisateurs

---

## 🔧 Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : MySQL
- **Frontend** : HTML/CSS/JavaScript
- **Déploiement** : systemd (Ubuntu)
- **Email** : SMTP Gmail

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

---

## 📞 Support

Pour toute question ou problème, contactez : [votre-email@example.com]