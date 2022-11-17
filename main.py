"""
Liikuda saab nuppudega W, A, S, D,
SPACE, LSHIFT ning rakenduse saab
sulgeda ESCAPE nupuga
"""
from blackbox import *
import pygame as pg
import numpy as np
import glm


def check_events(vaos, vbos, shader_programs):
    move_camera()
    rotate_camera()
    for event in pg.event.get():
        # Kontrollib sulgemist
        if event.type == pg.QUIT:
            destroy(vaos, vbos, shader_programs)
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                destroy(vaos, vbos, shader_programs)
                pg.quit()
                exit()


def shaders(shader_programs):
    shader_programs['default'] = load_shader('default')
    return shader_programs


def create_vbos(vbos):
    vbos['cube'] = cube_vbo()
    return vbos


def create_vaos(vaos, vbo, shader_program):
    vaos['cube'] = get_vao(shader_program, vbo)
    return vaos


def cube(vaos, shader_program, pos):
    return vaos['cube'], cube_model(shader_program, pos), glm.translate(glm.mat4(), pos)


def cube_vbo():
    _format = "3f 3f"
    _attribs = ["in_normal", "in_position"]
    #      4------7
    #     /|     /|
    #    / |    / |
    #   3--|---2  |
    #   |  5---|--6
    #   | /    | /
    #   |/     |/
    #   0------1

    # Tipud
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

    # Kuubi pinna normaalid, nagu tasandi normaalid KM tundides (risti tahuga)
    normals = [
        (0, 0, 1) * 6,
        (1, 0, 0) * 6,
        (0, 0, -1) * 6,
        (-1, 0, 0) * 6,
        (0, 1, 0) * 6,
        (0, -1, 0) * 6
    ]
    normals = np.array(normals, dtype='f4').reshape(36, 3)

    data = get_data(vertices, indices)
    vertex_data = np.array(data, dtype='f4')
    vertex_data = np.hstack([normals, vertex_data])
    return get_vbo(vertex_data), _format, _attribs


def cube_model(shader_program, pos):
    shader_program['light.position_v'].write(position_v)
    shader_program['light.Ia'].write(Ia)
    shader_program['light.Id'].write(Id)
    shader_program['light.Is'].write(Is)

    m_model = glm.translate(glm.mat4(), pos)
    shader_program['m_proj'].write(m_proj)
    shader_program['m_view'].write(m_view)
    shader_program['m_model'].write(m_model)
    return shader_program


def create_model():
    return


def main():
    shader_programs = {}
    vbos = {}
    vaos = {}
    objects = []

    shader_programs = shaders(shader_programs)
    vbos = create_vbos(vbos)
    vaos = create_vaos(vaos, vbos['cube'], shader_programs['default'])

    objects.append(cube(vaos, shader_programs['default'], (0, 0, -5)))
    objects.append(cube(vaos, shader_programs['default'], (3, 0, -5)))
    objects.append(cube(vaos, shader_programs['default'], (-3, 0, -5)))
    while 1:
        check_events(vaos, vbos, shader_programs)
        # Uuendab ekranni
        ctx.clear(color=(RED, GREEN, BLUE))
        render_scene(objects)
        pg.display.flip()
        # FPS
        clock.tick(60)


main()
