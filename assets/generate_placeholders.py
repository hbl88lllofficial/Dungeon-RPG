"""
Gera imagens e sons placeholder simples dentro da pasta `assets`.
Requer Pillow para PNGs; se não tiver, criará arquivos GIF simples.
"""
import os
import math
import wave
import struct

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL = True
except Exception:
    PIL = False

HERE = os.path.dirname(__file__)

def _blend(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i]) * t) for i in range(4))


def gen_images():
    sizes = (160, 160)
    p = os.path.join(HERE, 'player.png')
    e = os.path.join(HERE, 'enemy.png')
    r = os.path.join(HERE, 'room.png')
    if PIL:
        # hero sprite (cavaleiro)
        img = Image.new('RGBA', sizes, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # corpo
        d.rectangle((48, 72, 112, 128), fill=(70, 95, 140, 255), outline=(30, 40, 70, 255), width=2)
        d.rectangle((40, 86, 52, 126), fill=(90, 110, 135, 255), outline=(30, 40, 70, 255), width=2)
        d.rectangle((108, 86, 120, 118), fill=(160, 110, 60, 255), outline=(90, 60, 30, 255), width=2)
        # capa
        d.polygon([(48, 72), (36, 140), (60, 140), (72, 96), (88, 96), (100, 140), (124, 140), (112, 72)], fill=(110, 35, 35, 255), outline=(70, 20, 20, 255))
        # cabeça / elmo
        d.ellipse((52, 20, 108, 76), fill=(220, 220, 220, 255), outline=(80, 80, 90, 255), width=3)
        d.rectangle((62, 48, 98, 60), fill=(35, 35, 35, 255))
        d.line((70, 48, 70, 60), fill=(120, 120, 120, 255), width=2)
        d.line((90, 48, 90, 60), fill=(120, 120, 120, 255), width=2)
        d.rectangle((58, 26, 102, 36), fill=(180, 180, 180, 255), outline=(90, 90, 100, 255), width=2)
        # escudo
        d.polygon([(46, 84), (20, 104), (38, 136), (54, 124), (54, 92)], fill=(210, 180, 100, 255), outline=(90, 70, 30, 255), width=2)
        d.line((34, 106, 40, 120), fill=(110, 90, 40, 255), width=3)
        d.ellipse((28, 94, 36, 102), fill=(170, 140, 70, 255))
        # espada
        d.rectangle((104, 50, 118, 104), fill=(190, 190, 190, 255), outline=(80, 80, 90, 255), width=2)
        d.polygon([(110, 44), (108, 50), (114, 50)], fill=(210, 210, 210, 255), outline=(90, 90, 100, 255), width=2)
        d.rectangle((108, 104, 114, 126), fill=(60, 60, 80, 255))
        d.ellipse((88, 28, 96, 36), fill=(40, 40, 40, 255))
        img.save(p)

        # enemy sprite (orc)
        img2 = Image.new('RGBA', sizes, (0, 0, 0, 0))
        d2 = ImageDraw.Draw(img2)
        # corpo
        d2.rectangle((42, 78, 118, 136), fill=(62, 120, 50, 255), outline=(25, 55, 20, 255), width=2)
        d2.rectangle((38, 90, 52, 132), fill=(52, 95, 40, 255), outline=(25, 55, 20, 255), width=2)
        d2.rectangle((108, 94, 124, 126), fill=(90, 70, 40, 255), outline=(40, 30, 20, 255), width=2)
        # cabeça
        d2.ellipse((46, 10, 114, 76), fill=(95, 150, 70, 255), outline=(30, 55, 25, 255), width=3)
        d2.rectangle((58, 40, 102, 58), fill=(28, 28, 28, 255))
        d2.ellipse((58, 26, 72, 36), fill=(255, 255, 255, 255))
        d2.ellipse((88, 26, 102, 36), fill=(255, 255, 255, 255))
        d2.ellipse((64, 32, 70, 38), fill=(20, 20, 20, 255))
        d2.ellipse((90, 32, 96, 38), fill=(20, 20, 20, 255))
        d2.polygon([(58, 56), (70, 70), (70, 74), (62, 78)], fill=(170, 140, 80, 255), outline=(80, 60, 30, 255))
        d2.polygon([(102, 56), (90, 70), (90, 74), (98, 78)], fill=(170, 140, 80, 255), outline=(80, 60, 30, 255))
        d2.line((62, 68, 96, 68), fill=(30, 40, 20, 255), width=4)
        # ombreira
        d2.rectangle((38, 76, 70, 92), fill=(80, 80, 80, 255), outline=(40, 40, 40, 255), width=2)
        d2.rectangle((90, 76, 116, 92), fill=(80, 80, 80, 255), outline=(40, 40, 40, 255), width=2)
        # clava
        d2.rectangle((20, 92, 34, 126), fill=(85, 55, 35, 255), outline=(45, 30, 20, 255), width=2)
        d2.ellipse((14, 86, 40, 106), fill=(115, 95, 70, 255), outline=(55, 42, 23, 255), width=2)
        img2.save(e)

        # dungeon background
        bg = Image.new('RGBA', (520, 520), (24, 24, 28, 255))
        db = ImageDraw.Draw(bg)
        floor_color = (38, 40, 48, 255)
        for row in range(8):
            for col in range(8):
                x0 = col * 65 + 10
                y0 = row * 65 + 250
                x1 = x0 + 60
                y1 = y0 + 60
                shade = 18 + ((row + col) % 2) * 8
                db.rectangle((x0, y0, x1, y1), fill=(floor_color[0] + shade, floor_color[1] + shade, floor_color[2] + shade, 255))
                db.line((x0, y0, x1, y0), fill=(80, 80, 90, 255))
                db.line((x0, y0, x0, y1), fill=(80, 80, 90, 255))
        wall_color = (40, 40, 55, 255)
        db.rectangle((0, 0, 520, 240), fill=wall_color)
        for i in range(6):
            x = 30 + i * 80
            db.rectangle((x, 20, x + 60, 200), outline=(60, 60, 80, 255), width=3)
            for j in range(5):
                y = 22 + j * 36
                db.rectangle((x + 6, y, x + 54, y + 24), outline=(56, 56, 72, 255), width=1)
        db.rectangle((190, 100, 330, 240), fill=(22, 22, 28, 255), outline=(90, 90, 110, 255), width=4)
        db.arc((200, 50, 320, 220), start=0, end=180, fill=(90, 90, 110, 255), width=4)
        for flame in [(250, 86), (292, 104)]:
            fx, fy = flame
            db.ellipse((fx-10, fy-10, fx+10, fy+20), fill=(200, 120, 50, 255))
            db.ellipse((fx-6, fy-4, fx+6, fy+14), fill=(240, 180, 70, 255))
            db.ellipse((fx-3, fy+4, fx+3, fy+12), fill=(255, 230, 120, 255))
        for i in range(5):
            db.line((20 + i * 100, 240, 40 + i * 100, 520), fill=(25, 25, 30, 255), width=8)
        db.text((28, 18), "DUNGEON", fill=(150, 150, 180, 255))
        bg.save(r)
    else:
        open(p, 'wb').close()
        open(e, 'wb').close()
        open(r, 'wb').close()


def gen_wav(name='attack', duration_s=0.2, freq=440.0):
    path = os.path.join(HERE, f'{name}.wav')
    framerate = 44100
    amplitude = 8000
    nframes = int(duration_s * framerate)
    comptype = "NONE"
    compname = "not compressed"
    nchannels = 1
    sampwidth = 2

    wav_file = wave.open(path, 'w')
    wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    for i in range(nframes):
        t = float(i)/framerate
        val = int(amplitude * math.sin(2*math.pi*freq*t) * (1.0 - t/duration_s))
        data = struct.pack('<h', val)
        wav_file.writeframesraw(data)
    wav_file.close()


if __name__ == '__main__':
    gen_images()
    gen_wav('attack', 0.18, 880.0)
    gen_wav('explosion', 0.5, 200.0)
    gen_wav('special', 0.35, 600.0)
    gen_wav('combat_start', 0.4, 330.0)
    gen_wav('room', 1.0, 220.0)
    gen_wav('door', 0.12, 1200.0)
    gen_wav('victory', 0.6, 1000.0)
    gen_wav('defeat', 0.6, 120.0)
    print('Placeholders gerados em', HERE)
