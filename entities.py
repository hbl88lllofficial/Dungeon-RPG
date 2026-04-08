import random


class Character:
    def __init__(self, name, life, attack):
        self.name = name

        # VIDA
        self.max_life = life
        self.life = life

        # ATAQUE
        self.attack = attack
        self.weapon_bonus = 0

        # DEFESA
        self.block_chance = 0.1

        # PROGRESSÃO
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 25

        # ITENS
        self.potions = 1
        self.energy_potions = 0
        self.gold = 0

        # GRANADAS
        self.explosive_grenades = 0
        self.smoke_grenades = 0
        self.flash_grenades = 0

        # ENERGIA
        self.max_energy = 10
        self.energy = 10

        # ESPECIAIS
        self.special_cooldown = 0
        self.fury_turns = 0

        # RUNAS
        self.rune_type = None
        self.rune_power = 0

        # ESTADOS
        self.bleed_turns = 0
        self.bleed_damage = 2
        self.stunned = False

        self.crit_bonus = 0
        self.gold_bonus = 0

        self.relics = []

        # EFEITOS DE GRANADAS
        self.smoke_turns = 0
        self.stun_turns = 0

        self.rune = "Nenhuma"
        self.weapon = "Arma básica"
        self.weapon_attack = 0

        # ITENS EQUIPÁVEIS
        self.has_shield = False
        self.has_bow = False

    # ==================================================
    # ATAQUE
    # ==================================================
    def attack_target(self, target):
        from actions import attack

        messages = []
        total_damage = 0

        if self.fury_turns > 0 and random.random() < 0.6:
            messages.append("🔥 Ataque duplo!")

            damage1, msg1 = attack(self, target)
            damage2, msg2 = attack(self, target)

            total_damage = damage1 + damage2
            messages.extend(msg1)
            messages.extend(msg2)
        else:
            total_damage, msg = attack(self, target)
            messages.extend(msg)

        return total_damage, messages


    # ==================================================
    # ESPECIAIS
    # ==================================================
    def get_special_options(self):
        options = {}

        if self.level >= 2:
            options["BASIC"] = 5

        if self.level >= 6:
            options["FURY"] = 4

        if self.level >= 9:
            options["STUN"] = 6

        return options

    def use_special(self, special_type, target):
        from actions import (
            special_attack_basic,
            special_attack_fury,
            special_attack_stun
        )

        messages = []

        if self.special_cooldown > 0:
            return [f"⏳ Habilidade em recarga ({self.special_cooldown} turno(s))."]

        options = self.get_special_options()

        if special_type not in options:
            return ["❌ Especial inválido."]

        cost = options[special_type]

        if self.energy < cost:
            return ["❌ Energia insuficiente!"]

        self.energy -= cost

        if special_type == "BASIC":
            damage, msg = special_attack_basic(self, target)
            messages.extend(msg)

        elif special_type == "FURY":
            damage, msg = special_attack_fury(self)
            messages.extend(msg)

        elif special_type == "STUN":
            damage, msg = special_attack_stun(self, target)
            messages.extend(msg)

        return messages


    # ==================================================
    # DANO
    # ==================================================
    def take_damage(self, damage):
        dodge_chance = 0.3 if self.smoke_turns > 0 else 0
        if random.random() < dodge_chance:
            return 0  # Esquivou
        if random.random() < self.block_chance:
            damage //= 2
        self.life = max(0, self.life - damage)
        return damage

    def apply_bleed(self):
        if self.bleed_turns > 0:
            self.life -= self.bleed_damage
            self.bleed_turns -= 1

    # ==================================================
    # POÇÕES
    # ==================================================
    def use_potion(self):
        if self.potions > 0:
            self.life = self.max_life
            self.potions -= 1
            return ["🧪 Poção de vida usada!"]
        return ["❌ Sem poções."]

    def use_energy_potion(self):
        if self.energy_potions > 0:
            self.energy = min(self.max_energy, self.energy + 5)
            self.energy_potions -= 1
            return ["⚡ Poção de energia usada!"]
        return ["❌ Sem poções."]

    # ==================================================
    # GRANADAS
    # ==================================================
    def use_explosive_grenade(self, target):
        if self.explosive_grenades > 0:
            damage = random.randint(20, 40)
            target.take_damage(damage)
            self.explosive_grenades -= 1
            return [f"💥 Granada explosiva usada! Causou {damage} de dano!"]
        return ["❌ Sem granadas explosivas."]

    def use_smoke_grenade(self):
        if self.smoke_grenades > 0:
            self.smoke_turns = 3  # 3 turnos de esquiva
            self.smoke_grenades -= 1
            return ["💨 Granada de fumaça usada! 30% de chance de esquiva por 3 turnos!"]
        return ["❌ Sem granadas de fumaça."]

    def use_flash_grenade(self, target):
        if self.flash_grenades > 0:
            target.stun_turns = 3
            self.flash_grenades -= 1
            return ["⚡ Granada flash usada! Inimigo atordoado por 3 turnos!"]
        return ["❌ Sem granadas flash."]

    # ==================================================
    # TURNOS
    # ==================================================
    def reduce_turn_effects(self):
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        if self.fury_turns > 0:
            self.fury_turns -= 1
        if self.smoke_turns > 0:
            self.smoke_turns -= 1
        if self.stun_turns > 0:
            self.stun_turns -= 1

    # ==================================================
    # PROGRESSÃO
    # ==================================================
    def gain_xp(self, amount):
        self.xp += amount
        messages = [f"✨ Você ganhou {amount} XP!"]

        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            lvl_msg = self.level_up()
            messages.extend(lvl_msg)

        return messages

    def level_up(self):
        self.level += 1

        # ===== BÔNUS AUTOMÁTICO =====
        self.max_life += 3
        self.attack += 2

        self.life = self.max_life
        self.energy = self.max_energy

        self.xp_to_next_level += 25

        return [
            f"⬆️ {self.name} subiu para o nível {self.level}!",
            "✨ Bônus automático aplicado!",
            "Escolha um bônus adicional!"    
    ]
    def apply_level_bonus(self, choice):
        if choice == "VIDA":
            self.max_life += 5
            self.life += 5
            return ["❤️ Vida máxima aumentada em +5!"]

        elif choice == "ENERGIA":
            self.max_energy += 5
            self.energy += 5
            return ["⚡ Energia máxima aumentada em +5!"]

        elif choice == "ATAQUE":
            self.attack += 2
            return ["⚔ Ataque aumentado em +2!"]

        return ["❌ Escolha inválida."]

    # ==================================================
    # RUNAS
    # ==================================================
    def equip_rune(self, rune_type, value):
        if self.rune_type == rune_type:
            self.rune_power += value
            return [f"🔮 Runa aprimorada! Poder atual: {self.rune_power}"]

        self.rune_type = rune_type
        self.rune_power = value
        return [f"✨ Nova runa equipada: {rune_type.upper()}"]

    def apply_upgrade_rune(self):
        self.weapon_bonus += 1
        return ["🔧 Arma aprimorada permanentemente (+1 dano)"]

    # ==================================================
    # RELÍQUIAS
    # ==================================================
    def add_relic(self, relic):
        self.relics.append(relic)

        if relic["type"] == "vida":
            self.max_life += relic["value"]
            self.life += relic["value"]

        elif relic["type"] == "dano":
            self.attack += relic["value"]

        elif relic["type"] == "ouro":
            self.gold_bonus += relic["value"]

        return [f"✨ Relíquia adquirida: {relic['name']}"]

    # ==================================================
    # ESTADO
    # ==================================================
    def is_alive(self):
        return self.life > 0


# ==================================================
# CRIAÇÃO DE INIMIGOS
# ==================================================
def create_enemy(player_level, room_count=0, boss=False):

    enemy_type = "normal"
    boss_theme = None

    if boss:
        boss_theme = random.choice([
            "tirano",
            "executor",
            "corrompido",
            "sentinela"
        ])
        name = f"👑 Boss da Dungeon"
        life = 20 + player_level * 10
        attack = 3 + player_level * 2
    else:
        name = f"Inimigo Nível {player_level}"
        life = 20 + player_level * 5
        attack = 3 + player_level

    if room_count >= 16:
        enemy_type = random.choice([
            "berserker",
            "assassino",
            "corrompido",
            "guardiao"
        ])


    enemy = Character(name, life, attack)
    enemy.level = player_level

    # ===== BOSS =====
    if boss:
        enemy.life = int(enemy.life * 1.6)
        enemy.max_life = enemy.life
        enemy.attack += 2

        if boss_theme == "tirano":
            enemy.attack += 2
            enemy.name = "👑 Tirano da Dungeon"

        elif boss_theme == "executor":
            enemy.crit_bonus = 0.15
            enemy.name = "⚔ Executor Ancestral"

        elif boss_theme == "corrompido":
            enemy.bleed_damage = 2
            enemy.name = "☠ Senhor Corrompido"

        elif boss_theme == "sentinela":
            enemy.block_chance += 0.2
            enemy.name = "🛡 Sentinela Imortal"

    # ===== INIMIGOS TEMÁTICOS =====
    elif enemy_type == "berserker":
        enemy.attack += 2
        enemy.name = "🔴 Berserker da Dungeon"

    elif enemy_type == "assassino":
        enemy.crit_bonus = 0.1
        enemy.name = "🗡 Assassino das Sombras"

    elif enemy_type == "corrompido":
        enemy.bleed_damage = 2
        enemy.name = "☠ Criatura Corrompida"

    elif enemy_type == "guardiao":
        enemy.max_life += 10
        enemy.life += 10
        enemy.block_chance += 0.1
        enemy.name = "🛡 Guardião Antigo"

    return enemy

