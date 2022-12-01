from settings import *
import pygame as pg


def load_texture(texture_path):
    texture = pg.image.load(texture_path).convert()
    texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
    texture = ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))
    return texture

texture = {}
texture['paus_pilt'] = load_texture("textures/paus_pilt.jpg")
texture['red'] = load_texture("textures/red.jpg")
texture['blue'] = load_texture("textures/blue.jpg")
texture['green'] = load_texture("textures/green.jpg")
texture['white'] = load_texture("textures/white.jpg")