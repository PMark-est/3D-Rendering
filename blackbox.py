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
    if type(texture) == tuple:  # Kui argument on antud RGB tuple-na, loob uue 1-pikslise pildi, millest teeb tekstuuri
        image_RGB = np.array([[[texture[0], texture[1], texture[2]]]])
        image = Image.fromarray(image_RGB.astype('uint8')).convert('RGB')
        image.save('textures/image.jpg')
        texture = pg.image.load('textures/image.jpg').convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = ctx.texture(size=texture.get_size(
        ), components=3, data=pg.image.tostring(texture, 'RGB'))

    else:  # Muidu laeb tekstuuri pildi failist
        texture = pg.image.load(texture).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = ctx.texture(size=texture.get_size(
        ), components=3, data=pg.image.tostring(texture, 'RGB'))

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
        # renderdab iga objekti jaoks oma tekstuuri/värvi
        obj[1][3].use(location=0)


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
    yaw = yaw % 360
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
    # Need arvud on võetud kaamera alla keeramisega ja sealt 'forward' muutujate väärtuste võtmisega, ei ole "täpsed" alla suuna väärtused
    forward.x = -0.017452405765652657
    forward.y = -0.9998477101325989
    forward.z = -2.436815520923119e-06

    forward = glm.normalize(forward)
    right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
    up = glm.normalize(glm.cross(right, forward))
    m_view = glm.lookAt(glm.vec3(0, 11, 0), glm.vec3(0, 11, 0) + forward, up)


def normalize(ray, dst, cur_pos):
    x = ray[0]
    y = ray[1]
    z = ray[2]
    length = np.sqrt(x*x + y*y + z*z)
    return dst * glm.vec3(x/length, y/length, z/length) + (glm.vec3(cur_pos))


def intersection_test(objects, dst):
    # Leiab, mis nurga all maailmasse vaatame
    x = np.cos(np.radians(yaw))
    y = np.sin(np.radians(pitch))
    z = np.cos(np.radians(90-yaw))
    ray_end = normalize((x, y, z), dst, position)
    intersecting_objects = []
    for obj in objects:
        matrix = obj[2]
        size_x = matrix[0][0]
        size_y = matrix[1][1]
        size_z = matrix[2][2]
        coordinates = obj[2][3]
        obj_x = coordinates[0]
        obj_y = coordinates[1]
        obj_z = coordinates[2]

        start_x = position[0]
        start_y = position[1]
        start_z = position[2]
        end_x = ray_end[0]
        end_y = ray_end[1]
        end_z = ray_end[2]

        # Kaamera on objekti sees
        x_in = start_x > obj_x - size_x and start_x < obj_x + size_x
        z_in = start_z < obj_z + size_z and start_z > obj_z - size_z
        y_in = start_y > obj_y - size_y and start_y < obj_y + size_y
        if x_in and z_in and y_in:
            continue

        # Kas kaamera vaatab üldse objekti suunas/ kas kaamera on õiges positsioonis, et näha
        # objekti
        if reach_test(start_y, end_y, obj_y, size_y):
            continue
        if reach_test(start_x, end_x, obj_x, size_x):
            continue
        if reach_test(start_z, end_z, obj_z, size_z):
            continue

        if find_side(start_x, obj_x, size_x):
            if start_z <= obj_z - size_z:
                angle_l = np.rad2deg(np.arctan((obj_x+size_x-start_x)/(obj_z-size_z-start_z)))
                angle_r = np.rad2deg(np.arctan((start_x-obj_x+size_x)/(obj_z-size_z-start_z)))
                if 90 - angle_l > yaw > 0:
                    continue
                if 180 > yaw > 90 + angle_r:
                    continue
                intersecting_objects.append(obj)
            elif start_z >= obj_z + size_z:
                angle_l = np.rad2deg(np.arctan((start_x-obj_x+size_x)/(start_z-obj_z-size_z)))
                angle_r = np.rad2deg(np.arctan((obj_x+size_x-start_x)/(start_z-obj_z-size_z)))
                if 270 - angle_l > yaw > 180:
                    continue
                if 270 + angle_r < yaw < 360:
                    continue
                intersecting_objects.append(obj)
            continue
        elif find_side(start_z, obj_z, size_z):
            if start_x <= obj_x - size_x:
                angle_l = np.rad2deg(np.arctan(start_z-obj_z+size_z) /
                                     (obj_x-size_x-start_x))
                angle_r = np.rad2deg(np.arctan(obj_z+size_z-start_z) /
                                     (obj_x-size_x-start_x))
                if 270 < yaw < 360 - angle_l:
                    continue
                elif 90 > yaw > angle_r:
                    continue
                intersecting_objects.append(obj)
            elif start_x >= obj_x + size_x:
                angle_l = np.rad2deg(np.arctan(obj_z+size_z-start_z) /
                                     (start_x-obj_x-size_x))
                angle_r = np.rad2deg(np.arctan(start_z-obj_z+size_z) /
                                     (start_x-obj_x-size_x))
                if 90 < yaw < 180-angle_l:
                    continue
                elif 270 > yaw > 180+angle_r:
                    continue
                intersecting_objects.append(obj)
            continue
        else:
            continue
    return intersecting_objects


def reach_test(start, end, pos, size):
    if start < pos - size and end < pos - size:
        return True
    if start > pos + size and end > pos + size:
        return True


def find_side(start, pos, size):
    if start >= pos - size and start <= pos + size:
        return True


def view_angle(x, y, z):
    print(np.degrees(np.arccos(x)), np.degrees(
        np.arcsin(y)), np.degrees(np.arccos(z)))
