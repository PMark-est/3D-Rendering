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
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pause(vaos, vbos, shader_programs)


def shaders(shader_programs):
    shader_programs['default'] = load_shader('default')
    shader_programs['shadow_map'] = load_shader('shadow_map')
    return shader_programs


def create_vbos(vbos):
    vbos['cube'] = cube_vbo()
    return vbos


def create_vaos(vaos, vbo, shader_program):
    vaos['cube'] = get_vao(shader_program['default'], vbo)
    vaos['shadow_cube'] = get_vao(shader_program['shadow_map'], vbo)
    return vaos


def cube(vaos, shader_program, pos, texture, size=(1, 1, 1)):
    m_model = glm.mat4()
    m_model = glm.translate(m_model, pos)
    m_model = glm.scale(m_model, size)
    return vaos['cube'], cube_model(shader_program, pos, size, vaos, texture), m_model


def cube_vbo():
    _format = "2f 3f 3f"
    _attribs = ["in_texcoord_0", "in_normal", "in_position"]
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
        (0, -1, 0) * 6,
        (0, 1, 0) * 6
    ]
    normals = np.array(normals, dtype='f4').reshape(36, 3)

    # Tekstuuri pinna jaoks vajalikud kolmnurgad
    tex_coord = [(0, 0), (1, 0), (1, 1), (0, 1)]
    tex_coord_indices = [
        (0, 1, 2), (0, 2, 3), 
        (0, 1, 2), (0, 2, 3), 
        (0, 1, 2), (0, 2, 3), 
        
        (0, 1, 2), (0, 2, 3), 
        (2, 0, 1), (2, 3, 0), 
        (3, 0, 1), (3, 1, 2)
        ]
    
    vertex_data = get_data(vertices, indices)
    vertex_data = np.hstack([normals, vertex_data])

    tex_coord_data = get_data(tex_coord, tex_coord_indices)
    vertex_data = np.hstack([tex_coord_data, vertex_data])

    return get_vbo(vertex_data), _format, _attribs


def cube_model(shader_program, pos, size, vaos, texture):
    m_model = glm.translate(glm.mat4(), pos)
    m_model = glm.scale(m_model, size)
    
    shader_program['u_texture_0'] = 0

    shader_program['u_resolution'].write(glm.vec2(WIN_SIZE))

    depth_texture = textures['depth_texture']
    shader_program['shadowMap'] = 1
    depth_texture.use(location=1)

    shadow_vao = vaos['shadow_cube'] #luues erinevaid uusi objekte, peaks selle argumendi muudetavaks tegema ('shadow_' + vao nimi)
    shadow_shader_program = shadow_vao.program
    shadow_shader_program['m_proj'].write(m_proj)
    shadow_shader_program['m_view_light'].write(m_view_light)
    shadow_shader_program['m_model'].write(m_model)

    shader_program['m_view_light'].write(m_view_light)

    shader_program['light.position_v'].write(position_v)
    shader_program['light.Ia'].write(Ia)
    shader_program['light.Id'].write(Id)
    shader_program['light.Is'].write(Is)

    shader_program['m_proj'].write(m_proj)
    shader_program['m_view'].write(m_view)
    shader_program['m_model'].write(m_model)
    return [shader_program, shadow_shader_program, shadow_vao, texture]



def create_model():
    return

def pause(vaos, vbos, shader_programs):
    objects_pause = []  # eraldi järjend, kuhu tekitatakse kast vastava küljepildiga
    objects_pause.append(cube(vaos, shader_programs['default'], (0, 0, 0), texture('textures/paus_pilt.jpg'), (9, 0.1, 16))) # Tekstuuri faili teekond


    pg.event.set_grab(False) # toob hiire nähtavale ja laseb vabaks
    pg.mouse.set_visible(True)


    while 1:
        pg.mouse.get_rel() #on selleks, et pärast ei jamaks see hiire asukoha muutusega kui paus kinni panna, funktsioon ise ei kasuta seda
        rotate_camera_pause() # funktsioon kaamera vaate alla suunamiseks
        # siin ei ole funktsiooni kaamera liigutamiseks, kuna seda ei tohi siin liigutada

        ctx.clear(color=(RED, GREEN, BLUE))
        render_shadow(objects_pause)
        render_scene(objects_pause) # renderdab eraldi järjendis oleva(d) objekti(d)
        pg.display.flip()
        
        for event in pg.event.get():
        # Kontrollib nupu vajutusi
            if event.type == pg.QUIT:
                destroy(vaos, vbos, shader_programs) # ristist saab kinni panna akna hetkel
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: # esc nupuga viib tagasi põhivaatesse hetkel
                    objects_pause.clear() #tühjendab järjendi, et järgmine kord ei teki probleeme uuesti sama järjendi koostamisel (vist on ebavajalik, kui funktsiooni alguses teeb uue puhta järjendi?)
                    pg.event.set_grab(True) # tõmbab uuesti hiire kasti kinni
                    pg.mouse.set_visible(False)
                    return
        clock.tick(60)
        
        
    return


def main():
    shader_programs = {}
    vbos = {}
    vaos = {}
    objects = []

    shader_programs = shaders(shader_programs)
    vbos = create_vbos(vbos)
    vaos = create_vaos(vaos, vbos['cube'], shader_programs)

    objects.append(
        cube(vaos, shader_programs['default'], (0, -3, -5), texture((50, 255, 200)), (10, 0.1, 10))) # RGB väärtused kasti värvi jaoks(0-255)
    objects.append(cube(vaos, shader_programs['default'], (3, 0, -5), texture((255, 0, 0))))        # Ära unusta sellest teha "tuple"!
    objects.append(cube(vaos, shader_programs['default'], (-3, 0, -5), texture((0, 0, 0))))
    # VALGUSE KAST (kasutatav ainult "CULL_FACE" flag-iga, mis ei renderda kaste seestpoolt)
    objects.append(
        cube(vaos, shader_programs['default'], (VALGUS_X, VALGUS_Y, VALGUS_Z), texture((255, 255, 255)), (0.1, 0.1, 0.1)))
    while 1:
        check_events(vaos, vbos, shader_programs)
        # Uuendab ekranni
        ctx.clear(color=(RED, GREEN, BLUE))
        # ennem varjud
        render_shadow(objects)
        # siis põhipilt
        render_scene(objects)
        pg.display.flip()
        # FPS
        clock.tick(60)


main()
