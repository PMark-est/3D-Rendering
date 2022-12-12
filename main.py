"""
Liikuda saab nuppudega W, A, S, D,
SPACE, LSHIFT ning rakenduse saab
sulgeda ESCAPE nupuga

Enne programmi käivitamist peab installeerima järgmised teegid:
numpy
pygame
PyGLM

"""
from blackbox import *
import pygame as pg
import numpy as np
import glm
import os
import sys
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from PIL import ImageTk


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
                create_models_gui(False)
                pg.mouse.get_rel()
                pg.event.set_grab(True)
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


def cube(vaos, shader_program, pos, texture, size=(1, 1, 1), name="kast"):
    m_model = glm.mat4()
    m_model = glm.translate(m_model, pos)
    m_model = glm.scale(m_model, size)
    return vaos['cube'], cube_model(shader_program, pos, size, vaos, texture), m_model, name


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


def end_pause():
    """Funktsioon, mis paneb "paus" ekraani kinni ja viib tagasi põhivaatesse"""
    global objects_pause, Ia, Id, Is
    for obj in objects_pause:
        obj[1][0]['light.Ia'].write(Ia)  # Viib valgus tasemed tagasi algseisu
        obj[1][0]['light.Id'].write(Id)
        obj[1][0]['light.Is'].write(Is)
    pg.mouse.get_rel()  # on selleks, et pärast ei jamaks see hiire asukoha muutusega kui paus kinni panna, funktsioon ise ei kasuta seda
    pg.event.set_grab(True)
    pg.mouse.set_visible(False)  # peidab hiire
    return


def create_models(vaos, shader, *objects, name):
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
        objs.append(obj[0](vaos, shader, pos, texture, size, name))
    return objs


def create_models_gui(start):
    """Esimene ekraan mis tuleb ette kui vajutad f tähte"""
    global window

    # Teeb hiire vabaks
    pg.event.set_grab(False)
    pg.mouse.set_visible(True)
    pg.mouse.set_pos(WIN_SIZE[0] / 2, WIN_SIZE[1] / 2)

    # Tkinteri initsialiseerimine
    window = tk.Tk()
    window.title("Muuda stseeni")
    window.resizable(width=False, height=False)
    window.geometry("300x300")

    # Pildi variandina väga halvasti kirjutatud tekst
    img = Image.open("textures/valitegevus.jpg")
    img = img.resize((230, 70), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(window, image=img)
    panel.pack()

    img2 = Image.open("textures/hetkelobjekteekraanil.jpg")
    img2 = img2.resize((250, 60), Image.Resampling.LANCZOS)
    img2 = ImageTk.PhotoImage(img2)
    panel2 = tk.Label(window, image=img2)
    panel2.pack()

    # Teksti variandina sama jutt
    # label = tk.Label(window, text="Vali tegevus",
    #                 font=10, width=25, height=5)
    # count = tk.Label(window, text=f"{len(objects)}",
    #                 width=25, height=2)

    # Halvasti kirjutatud arvud piltidena
    number = []
    panel3 = []
    for i in range(len(str(len(objects)))):
        a = str(len(objects))[i]
        number.append(Image.open(
            f"textures/numbrid/{a}.jpg").resize((20, 30), Image.Resampling.LANCZOS))
        number[i] = ImageTk.PhotoImage(number[i])
        panel3.append(tk.Label(window, image=number[i]))
        panel3[i].photo = number[i]
       #panel3[i].grid(row=1, column=i)
        panel3[i].pack()

    # Nupud
    button1 = tk.Button(window, text="Lisa objekte",
                        width=25, command=lambda: add_stuff(start))
    if start == True:
        button2 = tk.Button(
            window, text="Alusta", width=25, command=lambda: close_gui(1))
    else:
        button2 = tk.Button(
            window, text="Muuda/eemalda objekte", width=25, command=change_stuff)
        button4 = tk.Button(
            window, text="Muuda valguse asukohta", width=25, command=change_light)
        button5 = tk.Button(
            window, text="Muuda tausta värvi", width=25, command=change_scene)

    # Teeb kõik elemendid kuvatavaks vist
   # label.pack()
    # count.pack()

    button1.pack()
    button2.pack()
    if start == False:
        button4.pack()
        button5.pack()

    # Põhitsükkel tööle, ehk kuvab tekitatud akna
    window.mainloop()


def close_gui(a):
    """Funktsioon tkinteri akende sulgemiseks, et ei peaks iga funktsiooni lõpus seda olema"""
    global window, window2
    if a == 2:
        # Sülgeb mõlemad aknad korraga
        window2.destroy()
        window.destroy()
    elif a == 1:
        # Sulgeb ainult ühe akna, sest ainult üks on ees
        window.destroy()
    elif a == "x":
        # Sulgeb pealmise akna
        window2.destroy()
    pg.mouse.get_rel()
    pg.event.set_grab(True)
    pg.mouse.set_visible(False)


def add_stuff(start):
    """Teine ekraan mis tuleb ette kui vajutad esimesel nuppu "Lisa objekte" """
    global window2

    # Uus aken uue muutuja nimega
    window2 = tk.Toplevel()
    window2.title("Lisa objekte")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    # Tekst
    label_info = tk.Label(window2, text="Sisesta koordinaadid")

    # Sisestuskastid
    x = tk.StringVar()
    label_x = tk.Label(window2, text="X")
    x_entry = ttk.Entry(window2, textvariable=x)
    x_entry.focus()

    y = tk.StringVar()
    label_y = tk.Label(window2, text="Y")
    y_entry = ttk.Entry(window2, textvariable=y)

    z = tk.StringVar()
    label_z = tk.Label(window2, text="Z")
    z_entry = ttk.Entry(window2, textvariable=z)

    name = tk.StringVar()
    label_name = tk.Label(window2, text="Nimi objektile")
    name_entry = ttk.Entry(window2, textvariable=name)

    # Nupud
    button = tk.Button(
        window2, text="Edasi värvi valima", command=lambda: create(x, y, z, name, "color", "add", start))
    button2 = tk.Button(
        window2, text="Või vali oma pilt", command=lambda: create(x, y, z, name, "image", "add", start))

    label_info2 = tk.Label(
        window2, text="Töökindel .jpg failidega, teiste tüüpidega vastutad ise")

    # Kõik elemendid kuvatavaks vist
    label_info.pack()

    label_x.pack()
    x_entry.pack()

    label_y.pack()
    y_entry.pack()

    label_z.pack()
    z_entry.pack()

    label_name.pack()
    name_entry.pack()

    button.pack()
    button2.pack()
    label_info2.pack()

    # Akna põhitsükkel
    window2.mainloop()


def create(x, y, z, name, choice, action, count="", start=False):
    """Funktsioon, mis võtab eelnevast funktsioonist x-y-z koordinaadid, küsib värvi ja loob neist objekti"""
    if action == "add":
        # Teeb eelnevalt kasti sisestatud koordinaadid arvudeks
        try:
            x = float(x.get())
            y = float(y.get())
            z = float(z.get())
            name = str(name.get())
        except:
            raise Exception("Sisestatud koordinaadid ei ole arvud")

    if choice == "color":
        # Windowsi basic color picker
        color = colorchooser.askcolor(title="Vali värv")
        color = color[0]

    elif choice == "image":
        # Laseb kasutajal ise valida pildi objektile
        color = filedialog.askopenfilename(title='Vali pilt')

    # Lisab need objektide nimekirja
    object = create_models(vaos, shader_programs['default'],
                           (cube, (x, y, z), texture((color))), name=name)
    objects.append(object[0])

    # Kui on alles programm käima pandud, siis ei taha, et see automaatselt kõik kinni paneks
    # pärast esimese objekti lisamist
    if start == True:
        close_gui("x")
        # Uuendab teksti
        count.config(text=f"Hetkel objekte ekraanil: {len(objects)}")
    else:
        close_gui(2)


def change_stuff():
    """Aken objektide nimekirjaga, kus saab valida kas muuta värvi või eemaldada"""
    global objects, window2
    window2 = tk.Toplevel()
    window2.title("Muuda objekte")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    valik = []
    coords = []
    # Lisab kõikide olevate objektide koordinaadid järjendisse
    for obj in objects:
        # Nimekiri, mida kasutaja näeb
        valik.append(f"{obj[3]}: {obj[2].to_tuple()[3][0:3]}")
        # Koordinaadid lähevad eraldi veel järjendisse, et neid oleks lihtsam otsida
        coords.append(obj[2].to_tuple()[3][0:3])
    list_items = tk.Variable(value=valik)

    # Kast, kus saab valida ühte rida
    listbox = tk.Listbox(
        window2, listvariable=list_items, selectmode=tk.SINGLE)

    # Nupud
    button1 = tk.Button(window2, text="Muuda värvi",
                        command=lambda: change(listbox, coords, True, "color"))
    button2 = tk.Button(window2, text="Muuda pilti",
                        command=lambda: change(listbox, coords, True, "image"))
    button3 = tk.Button(window2, text="Eemalda",
                        command=lambda: change(listbox, coords, False))

    listbox.pack()
    button1.pack()
    button2.pack()
    button3.pack()

    window2.mainloop()


def change(listbox, coords, replace, choice=""):
    """Funktsioon objekti värvi muutmiseks"""
    global objects

    # Leiab nimekirjast valitud rea numbri ja koordinaatide nimekirjast vastavad koordinaadid
    i = listbox.curselection()
    coord = coords[i[0]]

    # Leiab muudetava objekti koordinaadid ehk eelnevast nimekirjast otsib need
    x, y, z = float(coord[0]), float(coord[1]), float(coord[2])
    # Võtab objekti nime korraks hoiule, et see pärast edasi anda
    name = objects[i[0]][3]
    # Eemaldab vastava numbriga rea objektide nimekirjast
    # (i[0], sest listbox.curselection tagastab tuple formaadis indeksi)
    objects.pop(i[0])

    # Kui on valitud nupp "Muuda värvi"
    if replace == True:
        create(x, y, z, name, choice, "replace")

    close_gui(2)


def change_light():
    """Aken valguse "lambi" asukoha väärtuste sisestamiseks"""
    global window2
    # Uus aken
    window2 = tk.Toplevel()
    window2.title("Muuda valgust")
    window2.resizable(width=False, height=False)
    window2.geometry("300x300")

    # Teksti kastid
    label_info1 = tk.Label(window2, text="Hetkel valguse asukoht:")
    label_info2 = tk.Label(
        window2, text=f"{VALGUS_X}, {VALGUS_Y}, {VALGUS_Z}")
    label_info3 = tk.Label(window2, text="Sisesta koordinaadid")

    # Sisestuskastid
    x = tk.StringVar()
    label_x = tk.Label(window2, text="X")
    x_entry = ttk.Entry(window2, textvariable=x)
    x_entry.focus()

    y = tk.StringVar()
    label_y = tk.Label(window2, text="Y")
    y_entry = ttk.Entry(window2, textvariable=y)

    z = tk.StringVar()
    label_z = tk.Label(window2, text="Z")
    z_entry = ttk.Entry(window2, textvariable=z)

    # Nupp
    button = tk.Button(
        window2, text="Muuda valguse asukoht", command=lambda: move_light(x, y, z))

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

    # Akna põhitsükkel
    window2.mainloop()


def move_light(x, y, z):
    """Funktsioon valguse "lambi" asukoha muutmiseks"""
    global position_v, m_view_light, objects, VALGUS_X, VALGUS_Y, VALGUS_Z
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


def change_scene():
    """Muudab tausta värvi"""
    global RED, GREEN, BLUE
    color = colorchooser.askcolor(title="Vali värv")

    # Teeb valitud 0-255 väärtused 0-1 vahemikku
    RED, GREEN, BLUE = color[0][0]/255, color[0][1]/255, color[0][2]/255
    close_gui(1)


def main():
    global objects, vaos, shader_programs
    shader_programs = {}
    vbos = {}
    vaos = {}
    objects = []

    shader_programs = shaders(shader_programs)
    vbos = create_vbos(vbos)
    vaos = create_vaos(vaos, vbos['cube'], shader_programs)
    create_models_gui(True)
    # Kui ei ole lisatud ühtegi kasti
    if objects == []:
        objects = create_models(vaos, shader_programs['default'],
                                (cube, (5, 0, 0), texture((0, 0, 255))), name="Tavaline kast"
                                )

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
