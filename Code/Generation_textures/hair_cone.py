# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:02:03 2024

@author: Soumia
"""

from abaqus import *
from abaqusConstants import *
import part
import assembly
import regionToolset


    
def create_cuboid(model, width, depth, height):
    # Créer le croquis pour le cuboïde
    cuboid_sketch = model.ConstrainedSketch(name='cuboidSketch', sheetSize=2 * max(width, depth))
    cuboid_sketch.rectangle(point1=(0, 0), point2=(width, depth))
    # Créer la pièce cuboïde
    cuboid_part = model.Part(name='Cuboid', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    cuboid_part.BaseSolidExtrude(sketch=cuboid_sketch, depth=height)
    return cuboid_part



def create_cone(model, base_radius, top_radius, height, cone_name):
    
    # Créer un nouveau croquis pour le profil du cône
    cone_sketch = model.ConstrainedSketch(name='coneSketch', sheetSize=500.0)
    

    cone_sketch.ConstructionLine(point1=(0, 0), point2=(0, height))
    cone_sketch.Line(point1=(0, height), point2=(top_radius, height))
    cone_sketch.Line(point1=(top_radius, height), point2=(base_radius, 0))  
    cone_sketch.Line(point1=(0, height), point2=(0, 0)) 
    cone_sketch.Line(point1=(base_radius, 0), point2=(0, 0))
    
 
    cone_part = model.Part(name=cone_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    cone_part.BaseSolidRevolve(sketch=cone_sketch, angle=360.0)
    
    return cone_part


def create_cone_pattern(model, cone_part, base_radius, spacing, num_x, num_z, start_x, start_z, cuboid_height):
    for i in range(num_x):
        for j in range(num_z):
            # Calculer les positions x et z pour chaque instance du cône
            x = start_x + i * spacing
            z = start_z + j * spacing
            instance_name = 'ConeInst_{}_{}'.format(i, j)
            
            # Créer l'instance du cône
            model.rootAssembly.Instance(name=instance_name, part=cone_part, dependent=ON)
            
            # Positionner l'instance du cône directement sur la surface latérale du cuboïde
            # en tenant compte du pivotement du cuboïde, la hauteur est maintenant alignée le long de y
            model.rootAssembly.translate(instanceList=(instance_name,), vector=(x, 0, z))
          

def clear_assembly(assembly):
  
    instance_keys = assembly.instances.keys()

    for key in instance_keys:
        del assembly.instances[key]

        

# Accéder au modèle courant
myModel = mdb.models['Model-1']

# Paramètres pour le cuboïde et le cercle
cuboid_width = 56
cuboid_depth = 46
cuboid_height = 2


# Remplacer par la nouvelle fonction
cuboid_part = create_cuboid(myModel, cuboid_width, cuboid_depth, cuboid_height)


# Ajouter le cuboïde à l'assemblée et le positionner
cuboid_instance = myModel.rootAssembly.Instance(name='CuboidInst', part=cuboid_part, dependent=ON)
# Rotation du cuboïde pour aligner l'extrusion le long de l'axe y
myModel.rootAssembly.rotate(instanceList=('CuboidInst',), axisPoint=(0, 0, 0), 
                            axisDirection=(1, 0, 0), angle=90)


# Dimensions et création du cône
cone_base_radius = 0.2 # en mm 
cone_top_radius = 0.05 # en mm
cone_height = 10.0 # en mm

cone_part = create_cone(myModel, cone_base_radius, cone_top_radius, cone_height, 'Cone')

# Translate le cône pour qu'il soit placé sur la surface supérieure du cuboïde
myModel.rootAssembly.translate(instanceList=('ConeInst',), vector=(0, 0, cuboid_height))

# Espacement des cônes et création de la grille
num_x = 50     # Nombre de cônes en x
num_y = 50    # Nombre de cônes en y


# Ajouter un espacement pour pouvoir ajouter les pas de vis 

start_x = 8.4 # en mm 
start_y = 3.4 # en mm
spacing = 0.8 # rayon de la base + espacement de base en base # en mm

# Création de la grille de cônes
create_cone_pattern(myModel, cone_part, cone_base_radius, spacing, num_x, num_y, start_x, start_y, cuboid_height)


all_instances = [instance_name for instance_name in myModel.rootAssembly.instances.keys()]

# Tourner toutes les instances de l'assemblage autour de l'axe X de 90 degrés
myModel.rootAssembly.rotate(instanceList=tuple(all_instances), axisPoint=(0, 0, 0), 
                            axisDirection=(1, 0, 0), angle=90.0)


myModel.rootAssembly.regenerate()















