import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np

class CameraRawLikeEditor:

    def open_image_path(self, file_path):
        """Ouvre une image JPEG à partir d'un chemin passé en argument"""
        
        try:
            img = Image.open(file_path).convert("RGB")
            self.original_image = img
            self.current_image = img.copy()
            # Réinit sliders
            self.var_expo.set(0)
            self.var_contrast.set(1)
            self.var_satur.set(1)
            self.var_temp.set(0)
            self.var_sharp.set(1)
            # Active sliders et bouton auto
            self.set_sliders_state("normal")
            self.btn_auto.config(state="normal")
            self.update_image()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier :\n{e}")

    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur JPEG façon Camera Raw")
        # Pas d'image à charger au début !
        self.current_image = None
        self.original_image = None
        self.display_image = None
        self.setup_ui()

    
    def setup_ui(self):
        # --- Frame principale image + sliders
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # --- Zone image
        self.image_label = tk.Label(main_frame, bd=2, relief="sunken", width=480, height=360)
        self.image_label.pack(side="left", padx=10, pady=10)
        
        # --- Zone des boutons et sliders
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Bouton d'ouverture d'image
        btn_open = tk.Button(right_frame, text="📁 Ouvrir une photo", command=self.open_image)
        btn_open.pack(pady=(0,8), fill="x")

        # Bouton retouche auto (désactivé tant qu'aucune image)
        self.btn_auto = tk.Button(right_frame, text="✨ Retouche auto", command=self.auto_enhance, state='disabled')
        self.btn_auto.pack(pady=(0,15), fill="x")

        # Bouton sauvegarder l'image
        btn_save = tk.Button(right_frame, text="💾 Sauvegarder", command=self.save_image)
        btn_save.pack(pady=(0,15), fill="x")
        
        # --- Définition des sliders pour réglage manuel
        self.var_expo = tk.DoubleVar(value=0)
        self.var_contrast = tk.DoubleVar(value=1)
        self.var_satur = tk.DoubleVar(value=1)
        self.var_temp = tk.DoubleVar(value=0)
        self.var_sharp = tk.DoubleVar(value=1)

        sliders = [
            ("Exposition", self.var_expo, -2, 2, 0.1),
            ("Contraste", self.var_contrast, 0.5, 2, 0.05),
            ("Saturation", self.var_satur, 0.5, 2, 0.05),
            ("Température", self.var_temp, -50, 50, 1),
            ("Netteté", self.var_sharp, 1, 3, 0.1),
        ]
        self.slider_refs = []  # Pour activer/désactiver dynamiquement
        
        for text, var, mn, mx, res in sliders:
            lbl = tk.Label(right_frame, text=text)
            lbl.pack()
            sld = tk.Scale(right_frame, variable=var, orient="horizontal",
                           from_=mn, to=mx, resolution=res, length=180,
                           command=lambda v: self.update_image())
            sld.pack(pady=(0,10))
            self.slider_refs.append(sld)

        # Sliders désactivés tant qu'il n'y a pas d'image
        self.set_sliders_state("disabled")

    def set_sliders_state(self, state):
        for sld in self.slider_refs:
            sld.config(state=state)

    def open_image(self):
        """Ouvre une image JPEG et l'affiche brute (prêt pour auto ou sliders)"""
        ftypes = [("Fichiers JPEG", "*.jpg *.jpeg")]
        file_path = filedialog.askopenfilename(title="Sélectionner une photo JPEG", filetypes=ftypes)
        if not file_path:
            return
        try:
            img = Image.open(file_path).convert("RGB")
            self.original_image = img
            self.current_image = img.copy()  # Toujours partir de la version brute
            # Réinit sliders (pour repartir à zéro)
            self.var_expo.set(0)
            self.var_contrast.set(1)
            self.var_satur.set(1)
            self.var_temp.set(0)
            self.var_sharp.set(1)
            # Active sliders et bouton auto
            self.set_sliders_state("normal")
            self.btn_auto.config(state="normal")
            self.update_image()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")

    def auto_enhance(self):
        """Applique la retouche automatique et recharge pour ajustements manuels"""
        if self.original_image is None:
            messagebox.showwarning("Aucune image", "Veuillez d'abord ouvrir une image.")
            return
        arr = np.array(self.original_image)
        arr = self.process_automatically(arr)
        self.current_image = Image.fromarray(arr)
        # Reset sliders (on repart sur retouche à zéro)
        self.var_expo.set(0)
        self.var_contrast.set(1)
        self.var_satur.set(1)
        self.var_temp.set(0)
        self.var_sharp.set(1)
        self.update_image()

    def save_image(self):
        """Sauvegarde l'image affichée avec les ajustements"""
        if self.display_image is None:
            messagebox.showwarning("Aucune image", "Veuillez d'abord ouvrir une image.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG", "*.jpg *.jpeg")])
        if file_path:
            self.display_image.convert("RGB").save(file_path, "JPEG", quality=95)
            messagebox.showinfo("Info", "Image sauvegardée.")

    def process_automatically(self, arr):
        """Algorithme de retouche automatique (balance des blancs + niveaux/CLAHE)"""
        arr = self.balance_white(arr)
        arr = self.auto_levels(arr)
        return arr

    def balance_white(self, img_array):
        """Balance des blancs automatique par canal"""
        mean = np.mean(img_array, axis=(0,1))
        gray = mean.mean()
        scale = gray / (mean + 1e-8)
        img = img_array.astype(np.float32) * scale
        img = np.clip(img, 0, 255)
        return img.astype(np.uint8)

    def auto_levels(self, img_array):
        """Correction automatique des niveaux sur la luminance (LAB+CLAHE)"""
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l2 = clahe.apply(l)
        out = cv2.merge([l2, a, b])
        return cv2.cvtColor(out, cv2.COLOR_LAB2RGB)

    def update_image(self, *args):
        """Affiche la version courante avec tous les ajustements sliders"""
        if self.current_image is None:
            messagebox.showwarning("Aucune image", "Veuillez d'abord ouvrir une image.")
            return
        img = self.current_image.copy()
        img = self.apply_sliders(img)
        img_tk = self.pil_to_tk(img, (480, 360))
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk  # Pour ne pas perdre la référence
        self.display_image = img         # Pour la sauvegarde

    def apply_sliders(self, img):
        """Applique les sliders de réglage manuels sur une image PIL"""
        arr = np.array(img).astype(np.float32)
        # Exposition (multiplicatif)
        expo = self.var_expo.get()
        arr = np.clip(arr * 2**expo, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        # Contraste
        img = ImageEnhance.Contrast(img).enhance(self.var_contrast.get())
        # Saturation
        img = ImageEnhance.Color(img).enhance(self.var_satur.get())
        # Température (modifie canaux R/B)
        temp = self.var_temp.get()
        arr = np.array(img).astype(np.float32)
        arr[:,:,0] += temp   # Rouge
        arr[:,:,2] -= temp   # Bleu
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        # Netteté
        img = ImageEnhance.Sharpness(img).enhance(self.var_sharp.get())
        return img

    def pil_to_tk(self, img, max_size):
        """Convertit une image PIL pour affichage Tkinter avec réduction si besoin"""
        img_disp = img.copy()
        img_disp.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img_disp)

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale

    ftypes = [("Fichiers JPEG", "*.jpg *.jpeg")]
    file_path = filedialog.askopenfilename(title="Sélectionner une photo JPEG", filetypes=ftypes)

    if not file_path:
        sys.exit("Aucun fichier sélectionné.")

    root.deiconify()  # Affiche la fenêtre principale

    app = CameraRawLikeEditor(root)       # PAS de file_path ici !
    app.open_image_path(file_path)        # <-- C'est ici qu'on passe le chemin sélectionné
    root.mainloop()




