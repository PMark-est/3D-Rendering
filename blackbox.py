from settings import *
from PIL import Image
import pygame as pg
import numpy as np
import glm


def load_shader(shader_name):
    """Loeb shaders kaustast vastavalt tippude ja värvi varjutajad"""
    with open(f"shaders/{shader_name}.vert") as file:
        vertex_shader = file.read()
    with open(f"shaders/{shader_name}.frag") as file:
        fragment_shader = file.read()
    program = ctx.program(vertex_shader=vertex_shader,
                          fragment_shader=fragment_shader)
    return program

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

def get_data(vertices, indices):
    data = [vertices[ind] for triangle in indices for ind in triangle]
    return np.array(data, dtype='f4')


def get_vbo(vertex_data):
    return ctx.buffer(vertex_data)


def get_vao(shader_program, vbo):
    return ctx.vertex_array(shader_program, [(vbo[0], vbo[1], *vbo[2])], skip_errors=True)


def render_scene(objects):
    """Paneb objekti ekraanile"""
    ctx.screen.use()
    for obj in objects:
        obj[0].render()
        obj[1][0]["m_model"].write(obj[2])
        obj[1][0]["m_view"].write(m_view)
        obj[1][0]["camPos"].write(position)
        obj[1][3].use(location=0) # renderdab iga objekti jaoks oma tekstuuri/värvi

def render_shadow(objects):
    """Teeb kindlaks, milline pind on eespool ja milline tagapool ehk loob aluse varjude tegemiseks"""
    depth_fbo.clear()
    depth_fbo.use()
    for obj in objects:
        obj[1][1]['m_model'].write(obj[2])
        obj[1][2].render()                   # renderdab "shadow_vao"

def destroy(vaos, vbos, shader_programs):
    """Garbage collection. See on selleks, et mälust kustutatakse ära asjad, mida ei kasutata enam"""
    for vao in vaos.values():
        vao.release()
    for vbo in vbos.values():
        vbo[0].release
    for shader in shader_programs.values():
        shader.release()
    depth_fbo.release()
    pg.quit()
    exit()



def move_camera():
    """Laseb kaameral liikuda üles, alla, paremale, vasakule, edasi ja tagasi.
    Vastavad nupud on W, S, D, A, SPACE ja LSHIFT"""
    global m_view, position
    vel = SPEED * 0.016  # 0.016 on delta_time e. aeg, mis kulub ühe framei joonistamiseks
    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        position += forward * vel
    if keys[pg.K_a]:
        position -= right * vel
    if keys[pg.K_s]:
        position -= forward * vel
    if keys[pg.K_d]:
        position += right * vel
    if keys[pg.K_SPACE]:
        position += up * vel
    if keys[pg.K_LSHIFT]:
        position -= up * vel


def rotate_camera():
    """Laseb kaamerat hiirega liikutada"""
    global yaw, pitch, forward, right, up, m_view
    rel_x, rel_y = pg.mouse.get_rel()
    yaw += rel_x * SENSITIVITY
    pitch -= rel_y * SENSITIVITY
    pitch = max(-89, min(89, pitch))

    yaw2, pitch2 = glm.radians(yaw), glm.radians(pitch)
    forward.x = glm.cos(yaw2) * glm.cos(pitch2)
    forward.y = glm.sin(pitch2)
    forward.z = glm.sin(yaw2) * glm.cos(pitch2)

    forward = glm.normalize(forward)
    right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
    up = glm.normalize(glm.cross(right, forward))
    m_view = glm.lookAt(position, position + forward, up)

def rotate_camera_pause():
    """Suunab kaamera kindlasse punkti, et teostada paus-menüü. Põhimõtteliselt sama funktsioon, mis eelnev, aga muutujad on ette antud"""
    global yaw, pitch, forward, right, up, m_view
    forward.x = -0.017452405765652657  # Need arvud on võetud kaamera alla keeramisega ja sealt 'forward' muutujate väärtuste võtmisega, ei ole "täpsed" alla suuna väärtused
    forward.y = -0.9998477101325989
    forward.z = -2.436815520923119e-06

    forward = glm.normalize(forward)
    right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
    up = glm.normalize(glm.cross(right, forward))
    m_view = glm.lookAt(glm.vec3(0, 11, 0), glm.vec3(0, 11, 0) + forward, up)