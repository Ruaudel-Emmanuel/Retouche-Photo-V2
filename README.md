# readme Retouche photo V2

**README.md** complet et adapté au projet Python de retouche photo façon Camera Raw, basé sur le fichier fourni.[^1]

***

# Éditeur Photo JPEG façon Camera Raw

Ce projet est une interface graphique Python permettant de **retoucher facilement des fichiers JPEG** :

- Prévisualisation en temps réel
- Retouche automatique par simple clic
- Sliders interactifs pour ajustements manuels (exposition, contraste, saturation, température, netteté)
- Support des fichiers **JPEG uniquement**
- Interface rappelant l’ergonomie de Camera Raw
- Dépendances : `tkinter`, `pillow`, `opencv-python`, `numpy`

***

## Fonctionnalités

- **Ouvrir une photo JPEG** (dialogue au démarrage ou via bouton)
- **Retouche automatique** : balance des blancs et amélioration de la luminosité
- **Réglages manuels** via sliders :
    - Exposition
    - Contraste
    - Saturation
    - Température de couleur (jaune/bleu)
    - Netteté
- **Sauvegarder l’image retouchée** au format JPEG, qualité maximale
- Interface claire, intuitive et légère

***

## Installation

Installe les dépendances requises avec :

```bash
pip install pillow opencv-python numpy
```

**Tkinter** est inclus d’office avec Python standard pour Windows et macOS. Sur Linux :

```bash
sudo apt install python3-tk
```


***

## Utilisation

1. Lance le programme Python :

```bash
python retouche-photo-2.py
```

2. Dès l’ouverture, sélectionne l’image JPEG à traiter.
3. L’interface s’ouvre, l’image est affichée :
    - Clique sur **“✨ Retouche auto”** pour une correction automatique
    - Utilise les **sliders** pour ajuster les réglages selon tes préférences
    - Clique sur **“💾 Sauvegarder”** pour enregistrer ta retouche
4. Le bouton **“📁 Ouvrir une photo”** permet de charger une nouvelle image à tout moment.

***

## Exemple d’interface

- Zone photo principale à gauche
- Panel de sliders et boutons d’actions à droite
- Tout reste actif et utilisable à chaque instant

***

## Code principal (extrait)

```python
if __name__ == "__main__":
    import sys
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Sélectionner une photo JPEG", filetypes=[("Fichiers JPEG", "*.jpg *.jpeg")])
    if not file_path:
        sys.exit("Aucun fichier sélectionné.")
    root.deiconify()
    app = CameraRawLikeEditor(root)
    app.open_image_path(file_path)
    root.mainloop()
```


***

## Dépendances

- Python ≥ 3.7
- Pillow
- OpenCV-Python (`cv2`)
- Numpy
- Tkinter

***

## Auteur

Développé par [Emmanuel Ruaudel] pour projet de démonstration d’édition photo type Camera Raw.

***

## License

Ce projet est sous licence MIT (modifiez selon usage).

***

[^1]: retouche-photo-2.py

