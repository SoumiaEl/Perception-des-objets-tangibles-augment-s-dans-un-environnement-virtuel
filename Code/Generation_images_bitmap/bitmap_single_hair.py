# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 21:51:24 2024

@author: Soumia
"""

import numpy as np
from PIL import Image

def spirale(n):
    """Génère des indices pour parcourir une matrice nxn en spirale depuis le bord droit vers le centre."""
    x, y = n - 1, 0  # Débuter du bord droit, en haut
    dx, dy = 0, 1   # Commencer par se déplacer vers le bas
    steps = n
    direction_changes = 0
    spiral_path = []

    while len(spiral_path) < n**2:
        if 0 <= x < n and 0 <= y < n and (x, y) not in spiral_path:
            spiral_path.append((x, y))

        
        if direction_changes % 2 == 0 and steps > 0:
            steps -= 1  

        
        x, y = x + dx, y + dy
        if x >= n or y >= n or x < 0 or y < 0 or (x, y) in spiral_path:  
            dx, dy = -dy, dx  
            direction_changes += 1
            x, y = x + dx, y + dy  
    return spiral_path


def creer_cheveu(hauteur_actuelle, largeur_base):
    # Commencer avec une matrice pleine (tout en blanc)
    cheveu = np.full((largeur_base, largeur_base), fill_value=255, dtype=np.uint8)
    
    # Obtenir la séquence en spirale
    indices_spirale = spirale(largeur_base)

    # Pour chaque couche après la première, commencer à retirer des pixels selon l'ordre de la spirale
    if hauteur_actuelle > 0:
        for i in range(hauteur_actuelle):
            if i < len(indices_spirale):
                x, y = indices_spirale[i]
                cheveu[x, y] = 0  

    return cheveu

# Paramètres de la structure capillaire (à modifier en fonction de la longueur souhaitée et de la taille de la base)
hauteur_cheveu = 9  
largeur_base = 3  # Largeur de la base du cheveu en pixels

# Générer et sauvegarder les images pour chaque couche
for couche in range(hauteur_cheveu):
    image_bitmap = creer_cheveu(couche, largeur_base)
    img = Image.fromarray(image_bitmap, 'L') 
    img.save(f'couche_{couche:03d}.bmp')

print("Génération terminée.")