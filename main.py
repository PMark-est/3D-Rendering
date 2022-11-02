import moderngl as mgl
import pygame as pg
import numpy as np
import glm

# Parema käe koordinaadistik
WIN_SIZE = (1280, 720)
BLACK = (0.0, 0.0, 0.0)
FOV = 50
NEAR = 0.1
FAR = 100

pg.init()

pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

pg.display.set_mode(WIN_SIZE, flags=pg.OPENGL|pg.DOUBLEBUF)
ctx = mgl.create_context()
clock = pg.time.Clock()
# Kaamera
aspect_ratio = WIN_SIZE[0]/WIN_SIZE[1]
position = glm.vec3(2, 3, 3)
up = glm.vec3(0, 1, 0)
m_view = glm.lookAt(position, glm.vec3(0), up)
m_proj = glm.perspective(glm.radians(FOV), aspect_ratio, NEAR, FAR)

def check_events(scene):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            destroy(scene)
            pg.quit()
            exit()

def load_shader(shader_name):
    with open(f"shaders/{shader_name}.vert") as file:
        vertex_shader = file.read()
    with open(f"shaders/{shader_name}.frag") as file:
        fragment_shader= file.read()
    program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    return program

def create(vertex_data):
    vbo = ctx.buffer(vertex_data)
    shader_program = load_shader('default')
    shader_program['m_proj'].write(m_proj)
    shader_program['m_view'].write(m_view)
    vao = ctx.vertex_array(shader_program, [(vbo, '3f', 'in_position')])
    return (vao, vbo, shader_program)

def render(scene):
    # vao.render()
    scene[0].render()

def destroy(scene):
    # Garbage collection. See on selleks, et mälust kustutatakse ära asjad, mida ei kasutata enam
    # vbo.release()
    scene[1].release()
    # shader_program.release()
    scene[2].release()
    # vao.release()
    scene[0].release()

def triangle(k = 0):
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
    if k==1:
        vertices = [
        (-0.6, -0.8, 0.0),
        (-0.6, 0.8, 0.0),
        (0.6, -0.8, 0.0)
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
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), # 0, 1, 2, 3
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1) # 4, 5, 6, 7
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
    data = [vertices[ind] for triangle in indices for ind in triangle]
    vertex_data = np.array(data, dtype='f4')
    return create(vertex_data)


def main():
    scene = cube()
    while True:
        check_events(scene)
        # Uuendab ekranni
        ctx.clear(color=BLACK)
        render(scene)
        pg.display.flip()
        # FPS
        clock.tick(60)

main()