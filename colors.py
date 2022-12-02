from settings import *
import pygame as pg
from PIL import Image
import numpy as np



def texture(texture):
    if type(texture) == tuple: # Kui argument on antud RGB tuple-na, loob uue 1-pikslise pildi, millest teeb tekstuuri
        image_RGB = np.array([[[texture[0], texture[1], texture[2]]]])
        image = Image.fromarray(image_RGB.astype('uint8')).convert('RGB')
        image.save('textures/image.jpg')
        texture = pg.image.load('textures/image.jpg').convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

    else: # Muidu laeb tekstuuri pildi failist
        texture = pg.image.load(texture).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))
        
    return texture

