import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np

class CameraRawLikeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur JPEG v4 - Corrigé")
        self.currentimage = None
        self.originalimage = None
        self.displayimage = None # Image pleine résolution pour la sauvegarde
        self.sliderrefs = []
        
        # Taille maximale de l'aperçu pour un affichage cohérent
        self.PREVIEW_MAX_SIZE = (800, 600)

        self.setupui()

    def setupui(self):
        mainframe = tk.Frame(self.root)
        mainframe.pack(fill='both', expand=True)

        # Le label qui contiendra l'image redimensionnée
        self.imagelabel = tk.Label(mainframe, bd=2, relief='sunken')
        self.imagelabel.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        rightframe = tk.Frame(mainframe, width=200) # Frame de droite avec une largeur fixe
        rightframe.pack(side='right', fill='y', padx=10, pady=10)
        rightframe.pack_propagate(False) # Empêche la frame de changer de taille

        btnopen = tk.Button(rightframe, text="Ouvrir une photo", command=self.openimage)
        btnopen.pack(pady=(0, 8), fill='x')

        self.btn_crop = tk.Button(rightframe, text="Recadrer", command=self.crop_image, state='disabled')
        self.btn_crop.pack(pady=(0, 15), fill='x')

        self.btnauto = tk.Button(rightframe, text="Retouche auto", command=self.autoenhance, state='disabled')
        self.btnauto.pack(pady=(0, 15), fill='x')
        
        btnsave = tk.Button(rightframe, text="Sauvegarder", command=self.saveimage)
        btnsave.pack(pady=(0, 15), fill='x')

        # Variables et sliders
        self.varexpo = tk.DoubleVar(value=0)
        self.varcontrast = tk.DoubleVar(value=1)
        self.varsatur = tk.DoubleVar(value=1)
        self.vartemp = tk.DoubleVar(value=0)
        self.varsharp = tk.DoubleVar(value=1)

        sliders_data = [
            ("Exposition", self.varexpo, -2, 2, 0.1), ("Contraste", self.varcontrast, 0.5, 2, 0.05),
            ("Saturation", self.varsatur, 0.5, 2, 0.05), ("Température", self.vartemp, -50, 50, 1),
            ("Netteté", self.varsharp, 1, 3, 0.1),
        ]

        for text, var, mn, mx, res in sliders_data:
            lbl = tk.Label(rightframe, text=text)
            lbl.pack(anchor='w')
            sld = tk.Scale(rightframe, variable=var, orient='horizontal', from_=mn, to=mx, resolution=res, length=180, command=self.updateimage)
            sld.pack(pady=(0, 10), anchor='w')
            self.sliderrefs.append(sld)

        self.setslidersstate('disabled')

    def setslidersstate(self, state):
        for sld in self.sliderrefs: sld.config(state=state)

    def openimage(self):
        filepath = filedialog.askopenfilename(title="Sélectionner une photo", filetypes=[('Fichiers JPEG', '*.jpg *.jpeg')])
        if filepath: self.openimagepath(filepath)

    def openimagepath(self, filepath):
        try:
            img = Image.open(filepath).convert('RGB')
            self.originalimage = img
            self.currentimage = img.copy()

            # Réinitialisation des sliders
            self.varexpo.set(0); self.varcontrast.set(1); self.varsatur.set(1); self.vartemp.set(0); self.varsharp.set(1)

            # Activation des contrôles
            self.setslidersstate('normal')
            self.btnauto.config(state='normal')
            self.btn_crop.config(state='normal')
            
            self.updateimage()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")
            
    def crop_image(self):
        if self.currentimage is None: return
        
        opencv_image = cv2.cvtColor(np.array(self.currentimage), cv2.COLOR_RGB2BGR)
        
        # Redimensionner l'image pour la fenêtre de sélection si elle est trop grande
        h, w, _ = opencv_image.shape
        max_dim = 1200 # Limite pour l'écran de sélection
        if h > max_dim or w > max_dim:
            scale = max_dim / max(h, w)
            preview_img = cv2.resize(opencv_image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
        else:
            scale = 1.0
            preview_img = opencv_image
            
        roi = cv2.selectROI("Recadrage", preview_img, fromCenter=False, showCrosshair=True)
        cv2.destroyAllWindows()
        
        if roi[2] > 0 and roi[3] > 0:
            # Re-calculer les coordonnées pour l'image originale
            x, y, w, h = [int(v / scale) for v in roi]
            self.currentimage = self.currentimage.crop((x, y, x + w, y + h))
            self.updateimage()

    def updateimage(self, *args):
        if self.currentimage is None: return

        # Appliquer les retouches
        img_processed = self.applysliders(self.currentimage.copy())
        
        # Conserver l'image traitée en pleine résolution pour la sauvegarde
        self.displayimage = img_processed

        # Créer une copie pour l'affichage et la redimensionner
        img_for_display = img_processed.copy()
        img_for_display.thumbnail(self.PREVIEW_MAX_SIZE, Image.Resampling.LANCZOS)
        
        imgtk = ImageTk.PhotoImage(img_for_display)
        self.imagelabel.config(image=imgtk)
        self.imagelabel.image = imgtk # Garder une référence pour éviter la suppression par le garbage collector

    def applysliders(self, img):
        img = ImageEnhance.Brightness(img).enhance(2**self.varexpo.get())
        img = ImageEnhance.Contrast(img).enhance(self.varcontrast.get())
        img = ImageEnhance.Color(img).enhance(self.varsatur.get())
        
        temp = self.vartemp.get()
        if temp != 0:
            arr = np.array(img, dtype=np.float32)
            arr[..., 0] += temp
            arr[..., 2] -= temp
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            
        return ImageEnhance.Sharpness(img).enhance(self.varsharp.get())
    
    # ... Les autres méthodes (autoenhance, saveimage, etc.) restent inchangées ...

    def autoenhance(self):
        if self.originalimage is None: messagebox.showwarning("Aucune image", "Veuillez d'abord ouvrir une image."); return
        arr = self.processautomatically(np.array(self.originalimage))
        self.currentimage = Image.fromarray(arr)
        self.varexpo.set(0); self.varcontrast.set(1); self.varsatur.set(1); self.vartemp.set(0); self.varsharp.set(1)
        self.updateimage()

    def saveimage(self):
        if self.displayimage is None: messagebox.showwarning("Aucune image", "Veuillez d'abord ouvrir une image."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Fichiers JPEG", "*.jpg *.jpeg")])
        if filepath:
            self.displayimage.save(filepath, "JPEG", quality=95)
            messagebox.showinfo("Info", "Image sauvegardée avec succès.")

    def processautomatically(self, arr):
        arr = self.balancewhite(arr)
        return self.autolevels(arr)

    def balancewhite(self, img_array):
        mean = np.mean(img_array, axis=(0, 1))
        scale = mean.mean() / (mean + 1e-8)
        return np.clip(img_array.astype(np.float32) * scale, 0, 255).astype(np.uint8)

    def autolevels(self, img_array):
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)
        return cv2.cvtColor(cv2.merge((l2, a, b)), cv2.COLOR_LAB2RGB)

if __name__ == '__main__':
    root = tk.Tk()
    app = CameraRawLikeEditor(root)
    root.mainloop()
