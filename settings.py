import moderngl as mgl
import pygame as pg
import glm

WIN_SIZE = (1280, 720)
# Tausta värvid
RED = 0.08  # 0.32
GREEN = 0.16  # 0.34
BLUE = 0.18  # 0.48

# Kuubi värvid
KUUBI_RED = 1
KUUBI_GREEN = 0
KUUBI_BLUE = 0
kuubi_värv = glm.vec3(KUUBI_RED, KUUBI_GREEN, KUUBI_BLUE)

# Kaamera parameetrid
FOV = 75
NEAR = 0.1
FAR = 100
SPEED = 10
SENSITIVITY = 0.05

# Valguse asukoht
VALGUS_X, VALGUS_Y, VALGUS_Z = 20, 20, 20
# Valgus
position_v = glm.vec3(VALGUS_X, VALGUS_Y, VALGUS_Z)
color = glm.vec3(1, 1, 1)


# Kordajad valguse peegeldumiseks, "intensiivsus"
Ia = 0.1 * color  # Üldine valgustugevus
Id = 0.8 * color  # Punktist tulnud valguse hajuvus pinnalt
Is = 1.0 * color  # Otsene peegeldus valgusel pinnalt


# Pygame'i initsialiseerimine koos openGL-iga
pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(
    pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
pg.display.set_mode(WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
pg.event.set_grab(True)
pg.mouse.set_visible(False)
ctx = mgl.create_context()
ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
clock = pg.time.Clock()


# Kaamera
aspect_ratio = WIN_SIZE[0]/WIN_SIZE[1]
# Kaamera algne asukoht (PAREM/VASAK,ÜLES/ALLA, ETTE/TAHA)
position = glm.vec3(0, 0, 0)
# Defineerib, mis poole on ette, üles ja paremale
right = glm.vec3(1, 0, 0)
up = glm.vec3(0, 1, 0)
forward = glm.vec3(0, 0, -1)
# Kaamera keeramise muutujad
yaw = -90
pitch = 0
# tagastab, kuhu vaatame maatrikskujul
m_view = glm.lookAt(position, glm.vec3(0, 0, 0), up)
# tagastab varjude loomiseks vajaliku vaatepunkti
m_view_light = glm.lookAt(position_v, glm.vec3(0, 0, 0), up)
# tagastab objektide projektsiooni maatrikskujul.
m_proj = glm.perspective(glm.radians(FOV), aspect_ratio, NEAR, FAR)




# Varjude tekstuurid
textures = {}
textures['depth_texture'] = ctx.depth_texture(WIN_SIZE)
textures['depth_texture'].repeat_x = False
textures['depth_texture'].repeat_y = False

depth_texture = textures['depth_texture']
depth_fbo = ctx.framebuffer(depth_attachment=depth_texture)