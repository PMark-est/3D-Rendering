"""
Liikuda saab nuppudega W, A, S, D,
SPACE, LSHIFT ning rakenduse saab
sulgeda ESCAPE nupuga
"""
from blackbox import *
import pygame as pg
import numpy as np
import glm
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser


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
            if event.key == pg.K_f:
                # toob hiire nähtavale ja laseb vabaks
                pg.event.set_grab(False)
                pg.mouse.set_visible(True)
                pg.mouse.set_pos(WIN_SIZE[0] / 2, WIN_SIZE[1] / 2)
                create_models_gui()
                pg.mouse.get_rel()
                pg.event.set_grab(True)  # vastupidi
                pg.mouse.set_visible(False)


def check_events_pause(vaos, vbos, shader_programs):
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            x, y = pg.mouse.get_pos()  # Hangib hiire koordinaadid kliki ajal
            # Kui hiir klikiti antud koordinaatide vahemikus (ehk peaaegu täpselt kastide sees)
            if x in range(414, 865):

                if y in range(94, 199):  # "Sulge rakendus" nupp
                    destroy(vaos, vbos, shader_programs)

                elif y in range(314, 420):  # "Alusta uuesti" nupp
                    sys.stdout.flush()
                    # Sulgeb hetkel käiva rakenduse ja avab uuesti, teeb "restardi"
                    os.execl(sys.executable, 'python', __file__, *sys.argv[1:])

                elif y in range(540, 648):  # "Tagasi" nupp
                    end_pause()
                    return True

        # Kontrollib muid tegevusi
        if event.type == pg.QUIT:  # Kui aken on ristist suletud
            destroy(vaos, vbos, shader_programs)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # Kui esc nuppu vajutatud, viib ka tagasi nagu "Tagasi" nupp ekraanil
                end_pause()
                return True


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

    # luues erinevaid uusi objekte, peaks selle argumendi muudetavaks tegema ('shadow_' + vao nimi)
    shadow_vao = vaos['shadow_cube']
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


def pause(vaos, vbos, shader_programs):
    global objects_pause
    objects_pause = []  # eraldi järjend, kuhu tekitatakse kast vastava küljepildiga
    objects_pause.append(cube(vaos, shader_programs['default'], (0, 0, 0), texture(
        'textures/paus_pilt.jpg'), (9, 0.1, 16)))  # Tekstuuri faili teekond

    pg.event.set_grab(False)  # toob hiire nähtavale ja laseb vabaks
    pg.mouse.set_visible(True)
    # liigubtab hiire ekraani keskele, et oleks ilusam
    pg.mouse.set_pos(WIN_SIZE[0] / 2, WIN_SIZE[1] / 2)

    for obj in objects_pause:
        # See eemaldab kõik valguse peegeldumised ning jätab alles puhta RGB valguse
        obj[1][0]['light.Ia'].write(0.8 * glm.vec3(1, 1, 1))
        obj[1][0]['light.Id'].write(0 * glm.vec3(1, 1, 1))
        obj[1][0]['light.Is'].write(0 * glm.vec3(1, 1, 1))

    while 1:
        pg.mouse.get_rel()  # on selleks, et pärast ei jamaks see hiire asukoha muutusega kui paus kinni panna, funktsioon ise ei kasuta seda
        rotate_camera_pause()  # funktsioon kaamera vaate alla suunamiseks
        # siin ei ole funktsiooni kaamera liigutamiseks, kuna seda ei tohi siin liigutada

        ctx.clear(color=(RED, GREEN, BLUE))
        render_shadow(objects_pause)
        # renderdab eraldi järjendis oleva(d) objekti(d)
        render_scene(objects_pause)
        pg.display.flip()

        # kui antud frunktsioon tagastab True
        if check_events_pause(vaos, vbos, shader_programs):
            return

        clock.tick(60)

    return


def end_pause():  # Funktsioon, mis paneb "paus" ekraani kinni ja viib tagasi põhivaatesse
    global objects_pause, Ia, Id, Is
    for obj in objects_pause:
        obj[1][0]['light.Ia'].write(Ia)  # Viib valgus tasemed tagasi algseisu
        obj[1][0]['light.Id'].write(Id)
        obj[1][0]['light.Is'].write(Is)
    pg.event.set_grab(True)
    pg.mouse.set_visible(False)  # peidab hiire
    return


def create_models(vaos, shader, *objects):
    objs = []
    for obj in objects:
        if len(obj) == 2:
            pos = (0, 0, 0)
            size = (1, 1, 1)
        elif len(obj) == 3:
            size = (1, 1, 1)
            texture = obj[2]
        else:
            size = obj[3]
            texture = obj[2]
        pos = obj[1]
        objs.append(obj[0](vaos, shader, pos, texture, size))
    return objs


def create_models_gui():
    """Esimene ekraan mis tuleb ette kui vajutad f tähte"""
    global window

    # Tkinteri initsialiseerimine
    window = tk.Tk()
    window.title("Muuda stseeni")
    window.resizable(width=False, height=False)
    window.geometry("300x300")

    # Raam, mille sisse tulevad elemendid
    frame_a = tk.Frame(master=window)

    # Tekst
    label = tk.Label(master=frame_a, text="Vali tegevus",
                     font=10, width=25, height=10)

    # Nupud
    button1 = tk.Button(master=frame_a, text="Lisa objekte",
                        width=25, command=add_stuff)
    button2 = tk.Button(
        master=frame_a, text="Muuda/eemalda objekte", width=25, command=change_stuff)
    button4 = tk.Button(
        master=frame_a, text="Muuda valguse asukohta", width=25, command=change_light)
    button5 = tk.Button(
        master=frame_a, text="Muuda tausta värvi", width=25, command=change_scene)

    # Teeb kõik elemendid kuvatavaks vist
    label.pack()

    button1.pack()
    button2.pack()
    button4.pack()
    button5.pack()

    frame_a.pack()

    # Põhitsükkel tööle, ehk kuvab tekitatud akna
    window.mainloop()


def close_gui(a):
    """Funktsioon tkinteri akende sulgemiseks, et ei peaks iga funktsiooni lõpus seda olema"""
    global window, window2
    # Kui on edastatud aknate arv kahena (ühe tehtava funktsiooni korral on see 1 ehk teist akent ei looda)
    if a == 2:
        window2.destroy()
    window.destroy()


def add_stuff():
    """Teine ekraan mis tuleb ette kui vajutad esimesel nuppu "Lisa objekte" """
    global window2, color, objects, vaos, shader_programs, x, y, z

    # Uus aken uue muutuja nimega
    window2 = tk.Toplevel()
    window2.title("Lisa objekte")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    # Raam
    frame_c = tk.Frame(master=window2, width=30)

    # Tekst
    label_info = tk.Label(master=frame_c, text="Sisesta koordinaadid")

    # Sisestuskastid
    x = tk.StringVar()
    label_x = tk.Label(master=frame_c, text="X")
    x_entry = ttk.Entry(master=frame_c, textvariable=x)
    x_entry.focus()

    y = tk.StringVar()
    label_y = tk.Label(master=frame_c, text="Y")
    y_entry = ttk.Entry(master=frame_c, textvariable=y)

    z = tk.StringVar()
    label_z = tk.Label(master=frame_c, text="Z")
    z_entry = ttk.Entry(master=frame_c, textvariable=z)

    # Nupp
    button = tk.Button(
        master=frame_c, text="Edasi värvi valima", command=color_chooser)

    # Kõik elemendid kuvatavaks vist
    label_info.pack()

    label_x.pack()
    x_entry.pack()

    label_y.pack()
    y_entry.pack()

    label_z.pack()
    z_entry.pack()

    button.pack()

    frame_c.pack()

    # Akna põhitsükkel
    window2.mainloop()


def color_chooser():
    """Funktsioon, mis võtab eelnevast funktsioonist x-y-z koordinaadid, küsib värvi ja loob neist objekti"""
    global color, x, y, z

    # Windowsi basic color picker
    color = colorchooser.askcolor(title="Vali värv")

    # Teeb eelnevalt kasti sisestatud koordinaadid arvudeks
    try:
        x = float(x.get())
        y = float(y.get())
        z = float(z.get())
    except:
        raise Exception("Sisestatud koordinaadid ei ole arvud")

    # Lisab need objektide nimekirja
    object = create_models(vaos, shader_programs['default'],
                           (cube, (x, y, z), texture((color[0]))))
    objects.append(object[0])

    close_gui(2)
    return


def change_stuff():
    """Aken objektide nimekirjaga, kus saab valida kas muuta värvi või eemaldada"""
    global objects, listbox, window2
    window2 = tk.Toplevel()
    window2.title("Muuda objekte")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    frame_b = tk.Frame(master=window2, width=30)

    valik = []
    # Lisab kõikide olevate objektide koordinaadid järjendisse
    for obj in objects:
        valik.append(obj[2].to_tuple()[3][0:3])
    list_items = tk.Variable(value=valik)

    # Kast, kus saab valida ühte rida
    listbox = tk.Listbox(
        master=frame_b, listvariable=list_items, selectmode=tk.SINGLE)

    # Nupud
    button1 = tk.Button(master=frame_b, text="Muuda värvi", command=change)
    button2 = tk.Button(master=frame_b, text="Eemalda", command=remove)

    listbox.pack()
    button1.pack()
    button2.pack()
    frame_b.pack()

    window2.mainloop()


def change():
    """Funktsioon objekti värvi muutmiseks"""
    global listbox, objects
    i = listbox.curselection()
    coord = listbox.get(i)
    # Leiab muudetava objekti koordinaadid ehk eelnevast nimekirjast otsib need
    x, y, z = float(coord[0]), float(coord[1]), float(coord[2])
    # Eemaldab valitud objekti
    objects.pop(i[0])

    color = colorchooser.askcolor(title="Vali värv")
    # Koostab uue objekti samade koordinaatide peale
    object = create_models(vaos, shader_programs['default'],
                           (cube, (x, y, z), texture((color[0]))))
    objects.append(object[0])

    close_gui(2)
    return


def remove():
    """Funktsioon objekti eemaldamiseks"""
    global listbox, objects
    # Leiab nimekirjast valitud rea numbri
    i = listbox.curselection()
    # Eemaldab vastava numbriga rea objektide nimekirjast
    # (i[0], sest eelnev funktsioon tagastab tuple formaadis indeksi)
    objects.pop(i[0])

    close_gui(2)
    return


def change_light():
    """Aken valguse "lambi" asukoha väärtuste sisestamiseks"""
    global window2, x, y, z, VALGUS_X, VALGUS_Y, VALGUS_Z
    # Uus aken
    window2 = tk.Toplevel()
    window2.title("Muuda valgust")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    frame_b = tk.Frame(master=window2, width=30)
    # Teksti kastid
    label_info1 = tk.Label(master=frame_b, text="Hetkel valguse asukoht:")
    label_info2 = tk.Label(
        master=frame_b, text=f"{VALGUS_X}, {VALGUS_Y}, {VALGUS_Z}")
    label_info3 = tk.Label(master=frame_b, text="Sisesta koordinaadid")

    # Sisestuskastid
    x = tk.StringVar()
    label_x = tk.Label(master=frame_b, text="X")
    x_entry = ttk.Entry(master=frame_b, textvariable=x)
    x_entry.focus()

    y = tk.StringVar()
    label_y = tk.Label(master=frame_b, text="Y")
    y_entry = ttk.Entry(master=frame_b, textvariable=y)

    z = tk.StringVar()
    label_z = tk.Label(master=frame_b, text="Z")
    z_entry = ttk.Entry(master=frame_b, textvariable=z)

    # Nupp
    button = tk.Button(
        master=frame_b, text="Muuda valguse asukoht", command=move_light)

    # Kõik elemendid kuvatavaks vist
    label_info1.pack()
    label_info2.pack()
    label_info3.pack()

    label_x.pack()
    x_entry.pack()

    label_y.pack()
    y_entry.pack()

    label_z.pack()
    z_entry.pack()

    button.pack()

    frame_b.pack()

    # Akna põhitsükkel
    window2.mainloop()


def move_light():
    """Funktsioon valguse "lambi" asukoha muutmiseks"""
    global x, y, z, position_v, up, m_view_light, objects, VALGUS_X, VALGUS_Y, VALGUS_Z
    try:
        x = float(x.get())
        y = float(y.get())
        z = float(z.get())
    except:
        raise Exception("Sisestatud koordinaadid ei ole arvud")

    # Muudab antud muutujad ära, et hiljem uuesti kasutades sellele eelnevat funktsiooni, oleks näidatavad arvud õiged
    VALGUS_X, VALGUS_Y, VALGUS_Z = x, y, z
    position_v = glm.vec3(x, y, z)

    m_view_light = glm.lookAt(position_v, glm.vec3(0, 0, 0), up)

    # Lükkab uued valguse/varju väärtused renderisse
    for obj in objects:
        obj[1][0]['light.position_v'].write(position_v)
        obj[1][0]['m_view_light'].write(m_view_light)

    close_gui(2)
    return


def change_scene():
    global RED, GREEN, BLUE
    color = colorchooser.askcolor(title="Vali värv")

    # Teeb valitud 0-255 väärtused 0-1 vahemikku
    RED, GREEN, BLUE = color[0][0]/255, color[0][1]/255, color[0][2]/255
    close_gui(1)
    return


def main():
    global objects, vaos, shader_programs
    shader_programs = {}
    vbos = {}
    vaos = {}
    objects = []

    shader_programs = shaders(shader_programs)
    vbos = create_vbos(vbos)
    vaos = create_vaos(vaos, vbos['cube'], shader_programs)
    objects = create_models(vaos, shader_programs['default'],
                            (cube, (5, 0, 0), texture((0, 0, 255)))
                            )

    while 1:
        print()
        check_events(vaos, vbos, shader_programs)
        # Uuendab ekranni
        ctx.clear(color=(RED, GREEN, BLUE))
        # ennem varjud
        render_shadow(objects)
        # siis põhipilt
        render_scene(objects)
        intersection_test(objects, 4)
        pg.display.flip()
        # FPS
        clock.tick(60)


main()
