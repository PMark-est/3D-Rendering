import moderngl as mgl
import pygame as pg
import numpy as np
import glm

# Tausta värvid
RED = 0.08 #0.32
GREEN = 0.16 #0.34
BLUE = 0.18 #0.48

# Parema käe koordinaadistik
WIN_SIZE = (1280, 720)
# Kaamera parameetrid
FOV = 50
NEAR = 0.1
FAR = 100
SPEED = 10
SENSITIVITY = 0.05

# Valgus
position_v = glm.vec3(2, 3, 3)
color = glm.vec3(1, 1, 1)
Ia = 0.1 * color # ambient
Id = 0.8 * color # diffuse
Is = 1.0 * color # specular

pg.init()
pg.event.set_grab(True)
pg.mouse.set_visible(False)

pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(
    pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

pg.display.set_mode(WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
ctx = mgl.create_context()
ctx.enable(flags=mgl.DEPTH_TEST)
clock = pg.time.Clock()
# Kaamera
aspect_ratio = WIN_SIZE[0]/WIN_SIZE[1]
position = glm.vec3(2, 3, 3)
# Defineerib, mis poole on ette, üles ja paremale
right = glm.vec3(1, 0, 0)
up = glm.vec3(0, 1, 0)
forward = glm.vec3(0, 0, -1)
# Kaamera keeramise muutujad
yaw = -90
pitch = 0
# tagastab, kuhu vaatame maatrikskujul
m_view = glm.lookAt(position, glm.vec3(0), up)
# tagastab objektide projektsiooni maatrikskujul.
m_proj = glm.perspective(glm.radians(FOV), aspect_ratio, NEAR, FAR)


def check_events(scene):
    move_camera()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            destroy(scene)
            pg.quit()
            exit()


def load_shader(shader_name):
    with open(f"shaders/{shader_name}.vert") as file:
        vertex_shader = file.read()
    with open(f"shaders/{shader_name}.frag") as file:
        fragment_shader = file.read()
    program = ctx.program(vertex_shader=vertex_shader,
                          fragment_shader=fragment_shader)
    return program


def create(vertex_data):
    vbo = ctx.buffer(vertex_data)
    shader_program = load_shader('default')
    m_model = glm.mat4()

    shader_program['light.position_v'].write(position_v)
    shader_program['light.Ia'].write(Ia)
    shader_program['light.Id'].write(Id)
    shader_program['light.Is'].write(Is)

    shader_program['m_proj'].write(m_proj)
    shader_program['m_view'].write(m_view)
    shader_program['m_model'].write(m_model)
    shader_program['camPos'].write(position)
    vao = ctx.vertex_array(shader_program, [(vbo, '3f 3f', 'in_normal', 'in_position')])
    return (vao, vbo, shader_program, m_model)


def render(scene):
    # vao.render()
    scene[0].render()
    m_model = glm.rotate(scene[3], pg.time.get_ticks()
                         * 0.001, glm.vec3(0, 1, 0))
    scene[2]['m_model'].write(m_model)
    scene[2]['m_view'].write(m_view)


def destroy(scene):
    # Garbage collection. See on selleks, et mälust kustutatakse ära asjad, mida ei kasutata enam
    # vbo.release()
    scene[1].release()
    # shader_program.release()
    scene[2].release()
    # vao.release()
    scene[0].release()


def triangle(k=0):
    # Defineerime tipud
    # Siis lastakse nad läbi shaderi, mis töötleb igat tippu
    # Luuakse jooned tippude asukohtade põhjal
    # Rasteratsioon
    # Värvi shader
    vertices = [
        (-0.6, -0.8, 0.0),
        (0.6, -0.8, 0.0),
        (-0.6, 0.8, 0.0)
    ]
    vertex_data = np.array(vertices, dtype='f4')
    return create(vertex_data)


def cube():
    #      4------7
    #     /|     /|
    #    / |    / |
    #   3--|---2  |
    #   |  5---|--6
    #   | /    | /
    #   |/     |/
    #   0------1
    vertices = [
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),  # 0, 1, 2, 3
        (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)  # 4, 5, 6, 7
    ]

    # Kolmnurgad, millest kuup koosneb. Avaldatatud kuupide tippudena vastupäeva järjekorras. Iga paar on kuubi üks tahk
    indices = [
        (0, 1, 2), (0, 2, 3),
        (1, 6, 7), (1, 7, 2),
        (6, 5, 4), (6, 4, 7),
        (5, 0, 3), (5, 3, 4),
        (0, 6, 1), (0, 5, 6),
        (3, 2, 7), (3, 7, 4)
    ]

    # Kuubi pinna normaalid, nagu tasanditel
    normals = [
        (0, 0, 1) * 6, 
        (1, 0, 0) * 6, 
        (0, 0, -1) * 6, 
        (-1, 0, 0) * 6, 
        (0, 1, 0) * 6, 
        (0, -1, 0) * 6
    ]
    normals = np.array(normals, dtype='f4').reshape(36, 3)

    data = [vertices[ind] for triangle in indices for ind in triangle]
    vertex_data = np.array(data, dtype='f4')
    vertex_data = np.hstack([normals, vertex_data])
    return create(vertex_data)


def move_camera():
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
    if keys[pg.K_q]:
        position += up * vel
    if keys[pg.K_e]:
        position -= up * vel
    m_view = glm.lookAt(position, position + forward, up)


"""def rotate_camera():
    global yaw, pitch, forward, right, up
    rel_x, rel_y = pg.mouse.get_rel()
    yaw = rel_x * SENSITIVITY
    pitch = rel_y * SENSITIVITY
    pitch = max(-89, min(89, pitch))

    yaw, pitch = glm.radians(yaw), glm.radians(pitch)
    forward.x = glm.cos(yaw) * glm.cos(pitch)
    forward.y = glm.sin(pitch)
    forward.z = glm.sin(yaw) * glm.cos(pitch)

    forward = glm.normalize(forward)
    right = glm.normalize(glm.cross(forward, glm.vec3(0, 1, 0)))
    up = glm.normalize(glm.cross(right, forward))"""


def main():
    scene = cube()
    while 1:
        check_events(scene)
        # Uuendab ekranni
        ctx.clear(color=(RED, GREEN, BLUE))
        render(scene)
        pg.display.flip()
        # FPS
        clock.tick(60)


main()
