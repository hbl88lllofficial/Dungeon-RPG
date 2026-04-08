import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

from entities import Character, create_enemy
from combat import Combat
from dungeon import Dungeon
from shop import Shop
import tkinter.font as tkFont


# ===== Renderizador e Som (simples) =====
class SoundManager:
    def __init__(self, assets_dir):
        self.assets_dir = assets_dir
        self.backend = None
        try:
            import pygame
            pygame.mixer.init()
            self.pygame = pygame
            self.backend = 'pygame'
        except Exception:
            self.pygame = None
            self.backend = 'winsound' if os.name == 'nt' else None

    def play(self, name):
        # tenta arquivo wav/mp3 em assets
        candidates = [f"{name}.wav", f"{name}.mp3"]
        for c in candidates:
            path = os.path.join(self.assets_dir, c)
            if os.path.exists(path):
                try:
                    if self.backend == 'pygame' and self.pygame:
                        sound = self.pygame.mixer.Sound(path)
                        sound.play()
                        return
                except Exception:
                    pass

        # fallback simples: beep (Windows)
        if os.name == 'nt':
            try:
                import winsound
                winsound.Beep(800, 120)
            except Exception:
                pass


class Render:
    def __init__(self, canvas, assets_dir):
        self.canvas = canvas
        self.assets_dir = assets_dir
        self.images = {}

        # tenta carregar imagens padrões se existirem
        self._load_image('player', 'player.png', (160, 160))
        self._load_image('enemy', 'enemy.png', (160, 160))
        self._load_image('room', 'room.png', (520, 520))

    def _load_image(self, key, filename, target_size=None):
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            try:
                if PIL_AVAILABLE:
                    img = Image.open(path)
                    if target_size:
                        img = img.resize(target_size, Image.ANTIALIAS)
                    self.images[key] = ImageTk.PhotoImage(img)
                else:
                    self.images[key] = tk.PhotoImage(file=path)
            except Exception:
                self.images[key] = None
        else:
            self.images[key] = None

    def draw_room(self, dungeon):
        self.canvas.delete('room')
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        if self.images.get('room'):
            self.canvas.create_image(w//2, h//2, image=self.images['room'], tags='room')
        else:
            # Fundo escuro da dungeon
            self.canvas.create_rectangle(0, 0, w, h, fill='#0d0d0d', tags='room')

            # Paredes laterais com tijolos
            brick_height = 25
            brick_width = 40
            for side in [0, w-60]:  # Parede esquerda e direita
                for y in range(0, int(h*0.55), brick_height):
                    for x_offset in range(0, 60, brick_width):
                        x0 = side + x_offset
                        x1 = min(side + x_offset + brick_width, side + 60)
                        y0 = y
                        y1 = min(y + brick_height, int(h*0.55))
                        shade = 30 + ((x_offset // brick_width + y // brick_height) % 2) * 15
                        self.canvas.create_rectangle(x0, y0, x1, y1, fill=f'#{shade:02x}{shade:02x}{shade:02x}', outline='#222', width=1, tags='room')

            # Parede do fundo com tijolos maiores
            for y in range(0, int(h*0.55), brick_height):
                for x in range(60, w-60, brick_width):
                    shade = 25 + ((x // brick_width + y // brick_height) % 2) * 10
                    self.canvas.create_rectangle(x, y, x + brick_width, y + brick_height, fill=f'#{shade:02x}{shade:02x}{shade:02x}', outline='#333', width=1, tags='room')

            # Pilares nas esquinas
            pillar_width = 30
            pillar_height = int(h*0.55)
            for px in [30, w-60]:
                self.canvas.create_rectangle(px, 0, px + pillar_width, pillar_height, fill='#1a1a1a', outline='#444', width=2, tags='room')
                # Detalhes do pilar
                for py in range(0, pillar_height, 20):
                    self.canvas.create_line(px, py, px + pillar_width, py, fill='#666', width=1, tags='room')

            # Chão com lajes de pedra
            floor_y = int(h*0.55)
            slab_width = 50
            slab_height = 25
            for row in range(0, h - floor_y, slab_height):
                for col in range(0, w, slab_width):
                    shade = 40 + ((row // slab_height + col // slab_width) % 2) * 20
                    self.canvas.create_rectangle(col, floor_y + row, col + slab_width, floor_y + row + slab_height, fill=f'#{shade:02x}{shade:02x}{shade:02x}', outline='#555', width=1, tags='room')

            # Porta grande no centro
            door_x0 = 200
            door_x1 = 320
            door_y0 = 50
            door_y1 = 250
            self.canvas.create_rectangle(door_x0, door_y0, door_x1, door_y1, fill='#000', outline='#666', width=6, tags='room')
            # Arco da porta
            self.canvas.create_arc(door_x0 - 20, door_y0 - 50, door_x1 + 20, door_y1 - 150, start=0, extent=180, style='arc', outline='#888', width=4, tags='room')

            # Texto DUNGEON
            self.canvas.create_text(w*0.5, 80, text='DUNGEON', fill='#aaa', font=('Consolas', 24, 'bold'), tags='room')

            # Tochas nas paredes
            torch_positions = [
                (80, 100), (w-80, 100),  # Paredes laterais
                (150, 150), (w-150, 150),  # Mais tochas
                (door_x0 - 30, door_y1 - 50), (door_x1 + 30, door_y1 - 50)  # Perto da porta
            ]
            for tx, ty in torch_positions:
                # Suporte da tocha
                self.canvas.create_rectangle(tx-3, ty-20, tx+3, ty+10, fill='#8b4513', outline='#654321', tags='room')
                # Chama
                flame_colors = ['#ff4500', '#ffa500', '#ffff00']
                for i, color in enumerate(flame_colors):
                    self.canvas.create_oval(tx-5+i, ty-25+i*3, tx+5-i, ty-15+i*3, fill=color, outline='', tags='room')

            # Sombras no chão
            self.canvas.create_oval(100, floor_y + 50, 200, floor_y + 100, fill='#000', stipple='gray50', tags='room')
            self.canvas.create_oval(w-200, floor_y + 50, w-100, floor_y + 100, fill='#000', stipple='gray50', tags='room')

            # Detalhes decorativos: correntes nas paredes
            for chain_y in [120, 180]:
                for chain_x in [70, w-70]:
                    for i in range(5):
                        self.canvas.create_oval(chain_x-2, chain_y + i*15, chain_x+2, chain_y + 4 + i*15, fill='#666', outline='#444', tags='room')

    def draw_combat(self, player, enemy):
        self.canvas.delete('chars')
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        if self.images.get('player'):
            self.canvas.create_image(w*0.25, h*0.6, image=self.images['player'], tags='chars')
        else:
            self._draw_player_sprite(w*0.25, h*0.6)
        if self.images.get('enemy'):
            self.canvas.create_image(w*0.75, h*0.4, image=self.images['enemy'], tags='chars')
        else:
            self._draw_enemy_sprite(w*0.75, h*0.45)

    def _draw_player_sprite(self, cx, cy):
        # Cavaleiro: armadura prateada, elmo, escudo, espada
        # Elmo
        self.canvas.create_oval(cx-20, cy-70, cx+20, cy-30, fill='#c0c0c0', outline='#808080', width=2, tags='chars')
        # Visor do elmo
        self.canvas.create_rectangle(cx-15, cy-55, cx+15, cy-35, fill='#2a2a2a', outline='#000', tags='chars')
        # Corpo com armadura
        self.canvas.create_rectangle(cx-25, cy-30, cx+25, cy+20, fill='#a0a0a0', outline='#606060', width=3, tags='chars')
        # Cintura
        self.canvas.create_rectangle(cx-20, cy+20, cx+20, cy+35, fill='#808080', outline='#404040', width=2, tags='chars')
        # Pernas
        self.canvas.create_rectangle(cx-15, cy+35, cx-5, cy+70, fill='#606060', outline='#303030', width=2, tags='chars')
        self.canvas.create_rectangle(cx+5, cy+35, cx+15, cy+70, fill='#606060', outline='#303030', width=2, tags='chars')
        # Braço esquerdo com escudo
        self.canvas.create_rectangle(cx-45, cy-25, cx-25, cy+15, fill='#8b4513', outline='#654321', width=2, tags='chars')
        # Escudo
        self.canvas.create_oval(cx-50, cy-30, cx-20, cy+20, fill='#ffd700', outline='#daa520', width=3, tags='chars')
        # Braço direito com espada
        self.canvas.create_rectangle(cx+25, cy-20, cx+35, cy+10, fill='#c0c0c0', outline='#808080', width=2, tags='chars')
        # Espada
        self.canvas.create_rectangle(cx+30, cy-40, cx+40, cy+20, fill='#c0c0c0', outline='#808080', width=1, tags='chars')
        self.canvas.create_polygon(cx+35, cy-45, cx+45, cy-35, cx+35, cy-25, fill='#ffd700', outline='#daa520', tags='chars')
        # Detalhes da armadura
        self.canvas.create_line(cx-20, cy-25, cx-15, cy-20, fill='#fff', width=2, tags='chars')
        self.canvas.create_line(cx+15, cy-25, cx+20, cy-20, fill='#fff', width=2, tags='chars')

    def _draw_enemy_sprite(self, cx, cy):
        # Orc: pele verde, presas, brutamontes
        # Cabeça
        self.canvas.create_oval(cx-28, cy-72, cx+28, cy-24, fill='#228b22', outline='#006400', width=3, tags='chars')
        # Olhos amarelos
        self.canvas.create_oval(cx-18, cy-52, cx-10, cy-44, fill='#ffff00', outline='#000', tags='chars')
        self.canvas.create_oval(cx+10, cy-52, cx+18, cy-44, fill='#ffff00', outline='#000', tags='chars')
        # Pupilas
        self.canvas.create_oval(cx-16, cy-50, cx-12, cy-46, fill='#000', tags='chars')
        self.canvas.create_oval(cx+12, cy-50, cx+16, cy-46, fill='#000', tags='chars')
        # Boca
        self.canvas.create_arc(cx-15, cy-35, cx+15, cy-25, start=0, extent=-180, fill='#8b0000', outline='#000', tags='chars')
        # Presas
        self.canvas.create_polygon(cx-10, cy-35, cx-6, cy-25, cx-2, cy-35, fill='#fff', outline='#000', tags='chars')
        self.canvas.create_polygon(cx+2, cy-35, cx+6, cy-25, cx+10, cy-35, fill='#fff', outline='#000', tags='chars')
        # Corpo musculoso
        self.canvas.create_rectangle(cx-32, cy-24, cx+32, cy+30, fill='#32cd32', outline='#228b22', width=3, tags='chars')
        # Braços grossos
        self.canvas.create_oval(cx-50, cy-20, cx-20, cy+10, fill='#228b22', outline='#006400', width=2, tags='chars')
        self.canvas.create_oval(cx+20, cy-20, cx+50, cy+10, fill='#228b22', outline='#006400', width=2, tags='chars')
        # Mãos grandes
        self.canvas.create_oval(cx-55, cy+5, cx-45, cy+15, fill='#daa520', outline='#8b4513', tags='chars')
        self.canvas.create_oval(cx+45, cy+5, cx+55, cy+15, fill='#daa520', outline='#8b4513', tags='chars')
        # Cinto
        self.canvas.create_rectangle(cx-25, cy+25, cx+25, cy+35, fill='#8b4513', outline='#654321', width=2, tags='chars')
        # Pernas
        self.canvas.create_rectangle(cx-20, cy+30, cx-10, cy+70, fill='#228b22', outline='#006400', width=2, tags='chars')
        self.canvas.create_rectangle(cx+10, cy+30, cx+20, cy+70, fill='#228b22', outline='#006400', width=2, tags='chars')
        # Pés
        self.canvas.create_oval(cx-25, cy+65, cx-5, cy+75, fill='#8b4513', outline='#654321', tags='chars')
        self.canvas.create_oval(cx+5, cy+65, cx+25, cy+75, fill='#8b4513', outline='#654321', tags='chars')
        # Clava
        self.canvas.create_line(cx+40, cy-10, cx+70, cy-30, fill='#8b4513', width=8, tags='chars')
        self.canvas.create_oval(cx+65, cy-35, cx+75, cy-25, fill='#654321', outline='#000', tags='chars')

    def draw_background_gradient(self):
        # desenha um gradiente simples vertical
        self.canvas.delete('bg')
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        steps = 40
        for i in range(steps):
            color_val = int(20 + (i / steps) * 60)
            color = f"#{color_val:02x}{color_val:02x}{color_val+20:02x}"
            y0 = int(i * h / steps)
            y1 = int((i+1) * h / steps)
            self.canvas.create_rectangle(0, y0, w, y1, fill=color, width=0, tags='bg')

    def draw_hud(self, player, enemy=None):
        # desenha barras simples no topo do canvas
        self.canvas.delete('hud')
        w = int(self.canvas['width'])
        # player
        p_pct = max(0, player.life / player.max_life)
        self.canvas.create_rectangle(20, 20, 20 + int((w-40)*p_pct), 30, fill='#4caf50', tags='hud')
        self.canvas.create_text(20, 15, text=f"{player.name} {player.life}/{player.max_life}", anchor='nw', fill='#fff', tags='hud')
        if enemy:
            e_pct = max(0, enemy.life / enemy.max_life)
            self.canvas.create_rectangle(20, 40, 20 + int((w-40)*e_pct), 50, fill='#f44336', tags='hud')
            self.canvas.create_text(20, 35, text=f"{enemy.name} {enemy.life}/{enemy.max_life}", anchor='nw', fill='#fff', tags='hud')

    def attack_effect(self, enemy):
        # simples flash vermelho onde o inimigo está
        self._flash_overlay('#a00', 120)
        self.shake_screen(duration=300, intensity=8)

    def explosion_effect(self, enemy):
        self._flash_overlay('#ff8c00', 220)
        self.shake_screen(duration=400, intensity=12)

    def special_effect(self, player):
        self._flash_overlay('#ff0', 180)
        self.shake_screen(duration=350, intensity=10)

    def shake_screen(self, duration=300, intensity=8):
        """Efeito de tremor de tela para impacto visual"""
        step_time = 30
        steps = max(1, duration // step_time)
        current_offset = [0, 0]

        def do_shake(step=0):
            if step > 0:
                self.canvas.move('all', -current_offset[0], -current_offset[1])
                current_offset[0] = 0
                current_offset[1] = 0

            if step < steps:
                import random
                dx = random.randint(-intensity, intensity)
                dy = random.randint(-intensity, intensity)
                current_offset[0] = dx
                current_offset[1] = dy
                self.canvas.move('all', dx, dy)
                self.canvas.after(step_time, lambda: do_shake(step + 1))
            else:
                # garante retorno à posição original
                if current_offset[0] or current_offset[1]:
                    self.canvas.move('all', -current_offset[0], -current_offset[1])
                    current_offset[0] = 0
                    current_offset[1] = 0

        do_shake()

    def flash(self, color='#fff', duration=150):
        self._flash_overlay(color, duration)

    def _flash_overlay(self, color, duration):
        # cria retângulo sem preencher completamente e remove após tempo
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        rect = self.canvas.create_rectangle(0, 0, w, h, fill=color, stipple='gray25', tags='fx')
        self.canvas.after(duration, lambda: self.canvas.delete(rect))

    def _spawn_particles(self, color, count=8):
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        particles = []
        for i in range(count):
            x = int(w * (0.4 + 0.2 * (i / max(1, count))))
            y = int(h * (0.4 - 0.2 * (i % 3) / 3))
            r = self.canvas.create_oval(x, y, x+6, y+6, fill=color, tags='p')
            particles.append(r)

        def animate(step=0):
            for p in particles:
                try:
                    self.canvas.move(p, 0, -4 - (step % 3))
                    self.canvas.after(50, lambda: None)
                except Exception:
                    pass
            if step < 8:
                self.canvas.after(60, lambda: animate(step+1))
            else:
                for p in particles:
                    try:
                        self.canvas.delete(p)
                    except Exception:
                        pass

        animate()



class Game:

    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Game")
        self.root.geometry("950x650")

        # caminho dos assets (imagens/sons)
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")

        self.player = Character("Herói", 30, 5)
        self.dungeon = Dungeon(self.player)

        self.combat = None
        self.shop = None

        # Render e som
        self.canvas = None
        self.renderer = None
        self.sound = None

        self.create_ui()
        
        # inicializa renderizador e sistema de som
        self.init_render_and_sound()

        # Painel lateral de informações
        self.info_frame = tk.Frame(root)
        self.info_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.info_label = tk.Label(
            self.info_frame,
            text="",
            justify="left",
            font=("Consolas", 11),
            anchor="nw"
        )

        self.info_label.pack(fill="both", expand=True)

    # só depois iniciar dungeon
        self.start_next_room()

    def update_info_panel(self):

        base_attack = self.player.attack
        weapon_bonus = getattr(self.player, "weapon_attack", 0)
        total_attack = base_attack + weapon_bonus

        weapon = getattr(self.player, "weapon", "Arma básica")
        rune = getattr(self.player, "rune", "Nenhuma")

        rune = getattr(self.player, "rune", "Nenhuma")
        weapon = getattr(self.player, "weapon", "Arma básica")

        base_attack = self.player.attack
        weapon_bonus = getattr(self.player, "weapon_attack", 0)
        total_attack = base_attack + weapon_bonus

        # ===== INIMIGO =====
        if self.combat and self.combat.enemy:
            enemy_name = self.combat.enemy.name
            enemy_level = self.combat.enemy.level
            enemy_life = self.combat.enemy.life
            enemy_max = self.combat.enemy.max_life
            enemy_attack = self.combat.enemy.attack
        else:
            enemy_name = "-"
            enemy_level = "-"
            enemy_life = "-"
            enemy_max = "-"
            enemy_attack = "-"

        # ===== TEXTO =====
        text = f"""===== JOGADOR =====
        Nível: {self.player.level}
        XP: {self.player.xp} / {self.player.xp_to_next_level}

        Vida: {self.player.life}/{self.player.max_life}
        Energia: {self.player.energy}/{self.player.max_energy}

        Ataque base: {base_attack}
        Arma: {weapon} (+{weapon_bonus})
        Ataque total: {total_attack}

        Runa: {rune}
        Escudo: {'Sim' if self.player.has_shield else 'Não'}
        Arco: {'Sim' if self.player.has_bow else 'Não'}
        Ouro: {self.player.gold}

        ===== INIMIGO =====
        Nome: {enemy_name}
        Nível: {enemy_level}

        Vida: {enemy_life}/{enemy_max}
        Ataque: {enemy_attack}

        ===== DUNGEON =====
        Sala atual: {self.dungeon.room_count}
        """

        self.info_label.config(text=text)

    # =====================================
    # UI
    # =====================================

    def create_ui(self):

        # Layout: canvas à esquerda, UI à direita
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Canvas para renderização do jogo
        self.canvas = tk.Canvas(main_frame, width=520, height=520, bg="#111")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Frame de UI (direita)
        ui_frame = tk.Frame(main_frame)
        ui_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

        # ===== STATUS FRAME =====
        self.status_frame = tk.Frame(ui_frame)
        self.status_frame.pack(pady=5)

        self.player_info = tk.Label(self.status_frame, font=("Arial", 11))
        self.player_info.grid(row=0, column=0, padx=40)

        self.enemy_info = tk.Label(self.status_frame, font=("Arial", 11))
        self.enemy_info.grid(row=0, column=1, padx=40)

        # Barras de vida
        self.player_hp = ttk.Progressbar(ui_frame, length=300)
        self.player_hp.pack(pady=3)

        self.enemy_hp = ttk.Progressbar(ui_frame, length=300)
        self.enemy_hp.pack(pady=3)

        # ===== BOTÕES =====
        self.button_frame = tk.Frame(ui_frame)
        self.button_frame.pack(pady=15)

        self.buttons = []
        for i in range(5):
            btn = tk.Button(self.button_frame, width=20, height=2)
            self._place_button(btn, i)
            self.buttons.append(btn)

        # ===== LOG =====
        self.log_text = tk.Text(ui_frame, height=15, width=60, state="disabled", bg="#0f0f0f", fg="#ddd")
        self.log_text.pack(pady=10)

        # indicações rápidas em cima do canvas (opcional)
        self.canvas_text = self.canvas.create_text(260, 10, text="", fill="#fff", anchor="n", font=("Consolas", 12))

        # Estiliza botões e header
        self._style_ui(ui_frame)

        # Painel lateral de informações (moved into ui_frame)
        self.info_frame = tk.Frame(ui_frame)
        self.info_frame.pack(side=tk.BOTTOM, fill='x')

        self.info_label = tk.Label(
            self.info_frame,
            text="",
            justify="left",
            font=("Consolas", 10),
            anchor="nw",
            bg="#0b0b0b",
            fg="#eee",
            bd=1,
            relief='sunken'
        )

        self.info_label.pack(fill="both", expand=True)

    def init_render_and_sound(self):
        try:
            self.renderer = Render(self.canvas, self.assets_dir)
        except Exception:
            self.renderer = None

        try:
            self.sound = SoundManager(self.assets_dir)
        except Exception:
            self.sound = None
        # desenha background inicial
        if self.renderer:
            try:
                self.renderer.draw_background_gradient()
            except Exception:
                pass

    def _style_ui(self, ui_frame):
        # Fonte e cores
        try:
            title_font = tkFont.Font(family="Georgia", size=16, weight="bold")
        except Exception:
            title_font = ("Georgia", 16, "bold")

        # Cabeçalho
        header = tk.Label(ui_frame, text="Dungeon RPG", font=title_font, bg="#0b0b0b", fg="#ffd700")
        header.pack(side=tk.TOP, fill='x', pady=(0,6))

        # Cores do frame
        try:
            ui_frame.config(bg="#0b0b0b")
        except Exception:
            pass

        # Estilo para progressbars
        try:
            style = ttk.Style()
            style.theme_use('default')
            style.configure('Green.Horizontal.TProgressbar', troughcolor='#222', background='#4caf50')
            style.configure('Red.Horizontal.TProgressbar', troughcolor='#222', background='#f44336')
            self.player_hp.config(style='Green.Horizontal.TProgressbar')
            self.enemy_hp.config(style='Red.Horizontal.TProgressbar')
        except Exception:
            pass

        # Estiliza botões e labels
        btn_font = ("Helvetica", 10, "bold")
        for btn in self.buttons:
            try:
                btn.config(font=btn_font, bg="#1f1f1f", fg="#fff", activebackground="#333", activeforeground="#fff", bd=0)
            except Exception:
                pass

        try:
            self.player_info.config(bg="#0b0b0b", fg="#fff")
            self.enemy_info.config(bg="#0b0b0b", fg="#fff")
            self.button_frame.config(bg="#0b0b0b")
        except Exception:
            pass

    def _place_button(self, btn, index):
        # coloca botão em grid com wrap a cada 5 colunas
        row = index // 5
        col = index % 5
        try:
            btn.grid(row=row, column=col, padx=5, pady=3)
        except Exception:
            # fallback caso grid não funcione
            btn.grid(row=0, column=col, padx=5, pady=3)

    # =====================================
    # UTILIDADES
    # =====================================

    def _disable_buttons_temporarily(self, duration=1000):
        """Desabilita todos os botões por um período para evitar multi-clique"""
        for btn in self.buttons:
            try:
                btn.config(state="disabled")
            except Exception:
                pass
        
        # Reabilita após o tempo
        def re_enable():
            for btn in self.buttons:
                try:
                    if btn.cget('text') != '':
                        btn.config(state="normal")
                except Exception:
                    pass
        
        self.root.after(duration, re_enable)

    def update_status(self, enemy=None):

        self.player_info.config(
            text=(
                f"👤 {self.player.name} | "
                f"Nv: {self.player.level} | "
                f"XP: {self.player.xp}/{self.player.xp_to_next_level}\n"
                f"Vida: {self.player.life}/{self.player.max_life} | "
                f"Energia: {self.player.energy}/{self.player.max_energy}\n"
                f"Ouro: {self.player.gold} | "
                f"Poções: {self.player.potions} | "
                f"E.Poções: {self.player.energy_potions}\n"
                f"Granadas: E{self.player.explosive_grenades} F{self.player.smoke_grenades} L{self.player.flash_grenades} | "
                f"Cooldown: {self.player.special_cooldown}"
            )
        )

        self.player_hp["maximum"] = self.player.max_life
        self.player_hp["value"] = self.player.life

        if enemy:
            self.enemy_info.config(
                text=f"👾 {enemy.name}\nVida: {enemy.life}/{enemy.max_life}"
            )
            self.enemy_hp["maximum"] = enemy.max_life
            self.enemy_hp["value"] = enemy.life
        else:
            self.enemy_info.config(text="")
            self.enemy_hp["value"] = 0

        self.update_info_panel()

        # desenho do background
        if self.renderer:
            try:
                self.renderer.draw_background_gradient()
            except Exception:
                pass

    def add_log(self, messages):
        self.log_text.config(state="normal")
        for msg in messages:
            self.log_text.insert(tk.END, msg + "\n")
        self.log_text.insert(tk.END, "-" * 60 + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def clear_buttons(self):
        for btn in self.buttons:
            btn.config(text="", command=lambda: None, state="disabled")

    # =====================================
    # DUNGEON
    # =====================================

    def start_next_room(self):
        self.clear_buttons()

        state = self.dungeon.next_room()
        self.add_log(self.dungeon.log)
        if self.combat:
            self.update_status(self.combat.enemy)
        else:
            self.update_status()

        if state == "ROOM_CHOICE":
            self.show_room_choice()
        elif state == "SHOP":
            self.open_shop()
        elif state == "BOSS":
            self.start_combat(boss=True)

        # renderiza sala e toca som ambiente
        if self.renderer:
            try:
                self.renderer.draw_room(self.dungeon)
            except Exception:
                pass
        if self.sound:
            try:
                self.sound.play('room')
            except Exception:
                pass

    def show_room_choice(self):
        self.buttons[0].config(text="🚪 Porta 1",
                               state="normal",
                               command=lambda: self.enter_room(1))
        self.buttons[1].config(text="🚪 Porta 2",
                               state="normal",
                               command=lambda: self.enter_room(2))

    def enter_room(self, option):
        # Desabilita botões temporariamente
        self._disable_buttons_temporarily(duration=1200)
        
        result = self.dungeon.choose_room(option)
        self.add_log(self.dungeon.log)
        self.update_status()

        if self.renderer:
            try:
                self.renderer.flash(color="#222", duration=200)
            except Exception:
                pass
        if self.sound:
            try:
                self.sound.play('door')
            except Exception:
                pass

        if result == "COMBAT":
            self.start_combat()
        elif result == "ROOM_RESOLVED":
            self.root.after(1500, self.start_next_room)

    # =====================================
    # COMBATE
    # =====================================

    def start_combat(self, boss=False):
        enemy = create_enemy(self.player.level,
                             self.dungeon.room_count,
                             boss=boss)

        self.combat = Combat(self.player, enemy)
        self.update_status(enemy)

        # Efeito de arco e flecha: ataque extra no primeiro round
        if self.player.has_bow:
            damage, messages = self.player.attack_target(enemy)
            self.add_log([f"🏹 Arco: ataque extra inicial causa {damage} de dano!"])
            self.add_log(messages)

            if not enemy.is_alive():
                self.add_log(["🏆 Inimigo derrotado no ataque extra do arco!"])
                self.player.gold += 20
                xp = __import__('actions').calculate_xp(enemy)
                xp_messages = self.player.gain_xp(xp)
                self.add_log(xp_messages)
                self.add_log([f"💰 Você ganhou 20 de ouro."])
                self.root.after(1000, self.start_next_room)
                return

        self.setup_combat_buttons()

        # desenha combate e toca som
        if self.renderer:
            try:
                self.renderer.draw_combat(self.player, enemy)
            except Exception:
                pass
        if self.sound:
            try:
                self.sound.play('combat_start')
            except Exception:
                pass

    def setup_combat_buttons(self):
        self.buttons[0].config(text="⚔ ATACAR",
                               state="normal",
                               command=lambda: self.do_combat("ATACAR"))
        self.buttons[1].config(text="✨ ESPECIAL",
                               state="normal",
                               command=lambda: self.do_combat("ESPECIAL"))
        self.buttons[2].config(text="🧪 ITENS",
                               state="normal",
                               command=self.show_items_menu)
        self.buttons[3].config(text="🏃 FUGIR",
                               state="normal",
                               command=lambda: self.do_combat("FUGIR"))
        self.buttons[4].config(text="", state="disabled")  # Botão extra desabilitado

    def show_items_menu(self):
        self.buttons[0].config(text="❤️ VIDA",
                               state="normal",
                               command=lambda: self.do_combat("POÇÃO_VIDA"))
        self.buttons[1].config(text="⚡ ENERGIA",
                               state="normal",
                               command=lambda: self.do_combat("POÇÃO_ENERGIA"))
        self.buttons[2].config(text="💥 GRANADA EXPLOSIVA",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_EXPLOSIVA"))
        self.buttons[3].config(text="💨 GRANADA FUMAÇA",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_FUMAÇA"))

        if len(self.buttons) < 5:
            btn = tk.Button(self.button_frame, width=20, height=2)
            self._place_button(btn, len(self.buttons))
            self.buttons.append(btn)

        self.buttons[4].config(text="⚡ GRANADA FLASH",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_FLASH"))

        # Também adicionar um botão para voltar
        if len(self.buttons) < 6:
            btn = tk.Button(self.button_frame, width=20, height=2)
            self._place_button(btn, len(self.buttons))
            self.buttons.append(btn)

        self.buttons[5].config(text="⬅ VOLTAR",
                               state="normal",
                               command=self.start_combat)  # Voltar para o menu principal

    def show_items_menu(self):
        self.buttons[0].config(text="❤️ VIDA",
                               state="normal",
                               command=lambda: self.do_combat("POÇÃO_VIDA"))
        self.buttons[1].config(text="⚡ ENERGIA",
                               state="normal",
                               command=lambda: self.do_combat("POÇÃO_ENERGIA"))
        self.buttons[2].config(text="💥 GRANADA EXPLOSIVA",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_EXPLOSIVA"))
        self.buttons[3].config(text="💨 GRANADA FUMAÇA",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_FUMAÇA"))
        self.buttons[4].config(text="⚡ GRANADA FLASH",
                               state="normal",
                               command=lambda: self.do_combat("GRANADA_FLASH")) 

    def do_combat(self, action):
        # Desabilita botões para evitar multi-clique
        self._disable_buttons_temporarily(duration=1000)
        
        self.combat.execute_action(action)
        self.add_log(self.combat.log)
        self.update_status(self.combat.enemy)

        # Redesenha os personagens após atualizar status
        if self.renderer and self.combat:
            try:
                self.renderer.draw_combat(self.player, self.combat.enemy)
            except Exception:
                pass

        # efeitos visuais e sonoros
        try:
            if self.renderer:
                if action == "ATACAR":
                    self.renderer.attack_effect(self.combat.enemy)
                elif action == "GRANADA_EXPLOSIVA":
                    self.renderer.explosion_effect(self.combat.enemy)
                elif action == "ESPECIAL":
                    self.renderer.special_effect(self.player)
        except Exception:
            pass

        try:
            if self.sound:
                if action == "ATACAR":
                    self.sound.play('attack')
                elif action == "GRANADA_EXPLOSIVA":
                    self.sound.play('explosion')
                elif action == "ESPECIAL":
                    self.sound.play('special')
        except Exception:
            pass

        # Se foi uma ação de item, voltar para o menu principal
        if action in ["POÇÃO_VIDA", "POÇÃO_ENERGIA", "GRANADA_EXPLOSIVA", "GRANADA_FUMAÇA", "GRANADA_FLASH"]:
            self.root.after(600, self.setup_combat_buttons)

        if self.combat.finished:
            if self.combat.victory:
                from actions import calculate_xp

                # Ouro
                self.player.gold += 20

                # XP
                xp = calculate_xp(self.combat.enemy)
                xp_messages = self.player.gain_xp(xp)
                self.add_log(xp_messages)

                # Drop do inimigo
                self.dungeon.log.clear()
                self.dungeon.handle_enemy_drop()
                if self.dungeon.log:
                    self.add_log(self.dungeon.log)

                # Se subiu de nível, mostrar escolha
                if any("subiu para o nível" in msg for msg in xp_messages):
                    self.show_level_up_choice()
                    return

                self.add_log([f"💰 Você ganhou 20 de ouro."])
                self.add_log(xp_messages)

                messagebox.showinfo("Vitória", "Inimigo derrotado!")

                if self.sound:
                    try:
                        self.sound.play('victory')
                    except Exception:
                        pass
                self.root.after(1000, self.start_next_room)

            else:
                messagebox.showinfo("Game Over", "Você morreu.")
                if self.sound:
                    try:
                        self.sound.play('defeat')
                    except Exception:
                        pass
                self.root.destroy()

    def show_level_up_choice(self):
            self.clear_buttons()

            self.buttons[0].config(
                text="❤️ +5 Vida",
                state="normal",
                command=lambda: self.apply_level_upgrade("VIDA")
            )

            self.buttons[1].config(
                text="⚡ +5 Energia",
                state="normal",
                command=lambda: self.apply_level_upgrade("ENERGIA")
            )

            self.buttons[2].config(
                text="⚔ +2 Ataque",
                state="normal",
                command=lambda: self.apply_level_upgrade("ATAQUE")
            )
    
    def apply_level_upgrade(self, choice):
        messages = self.player.apply_level_bonus(choice)

        self.add_log(messages)
        self.update_status()

        # Limpa botões de upgrade
        self.clear_buttons()

        # Continua dungeon após pequena pausa
        self.root.after(800, self.start_next_room)

    # =====================================
    # LOJA
    # =====================================

    def open_shop(self):
        self.shop = Shop(self.player)
        self.update_status()

        options = self.shop.get_options()
        keys = [k for k in options.keys() if k != "EXIT"]

        # Cria botões suficientes para exibir todas as opções (mais botão de sair)
        while len(self.buttons) < len(keys) + 1:
            btn = tk.Button(self.button_frame, width=20, height=2)
            self._place_button(btn, len(self.buttons))
            self.buttons.append(btn)

        for i, key in enumerate(keys):
            item = options[key]
            cost = item.get("cost", "")
            text = f"{item['name']} ({cost})" if cost else item['name']

            self.buttons[i].config(
                text=text,
                state="normal",
                command=lambda k=key: self.buy_item(k)
            )

        # Botão sair ao final
        exit_idx = len(keys)
        self.buttons[exit_idx].config(
            text="🚪 Sair da Loja",
            state="normal",
            command=lambda: self.buy_item("EXIT")
        )

        # Desativa botões extras além dos usados
        for i in range(exit_idx + 1, len(self.buttons)):
            self.buttons[i].config(text="", state="disabled", command=lambda: None)

    def buy_item(self, key):
        self.shop.execute(key, confirm=True)
        self.add_log(self.shop.log)
        self.update_status()

        if self.shop.finished:
            self.root.after(1000, self.start_next_room)


# =====================================
# INICIAR
# =====================================

root = tk.Tk()
game = Game(root)
root.mainloop()
