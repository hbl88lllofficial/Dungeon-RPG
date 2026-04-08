import random

# ==================================================
# ATAQUE NORMAL
# ==================================================

def attack(attacker, defender):
    """
    Ataque básico do personagem
    Aplica runas, arma, sangramento, crítico e stun
    """

    messages = []

    base_damage = attacker.attack + attacker.weapon_bonus
    damage = random.randint(1, max(1, base_damage))

    # ==========================
    # RUNAS (arma)
    # ==========================

    # BLOQUEIO DE ESCUDO
    if getattr(defender, 'has_shield', False) and random.random() < 0.20:
        messages.append("🛡️ Seu escudo bloqueou o ataque!")
        return 0, messages

    # CRÍTICO
    if attacker.rune_type == "crit":
        crit_chance = 0.1 + (0.05 * attacker.rune_power)
        if random.random() < crit_chance:
            damage *= 2
            messages.append("💥 CRÍTICO!")

    # SANGRAMENTO
    if attacker.rune_type == "bleed":
        defender.bleed_turns += attacker.rune_power
        messages.append("🩸 Sangramento aplicado!")

    # STUN
    if attacker.rune_type == "stun":
        stun_chance = 0.1 * attacker.rune_power
        if random.random() < stun_chance:
            defender.stunned = True
            messages.append("⚡ Inimigo atordoado!")

    defender.take_damage(damage)

    return damage, messages


# ==================================================
# ATAQUES ESPECIAIS
# ==================================================

def special_attack_basic(attacker, defender):
    """
    Especial Nível 3
    Dano alto simples
    Energia: 3
    Cooldown: 2
    """

    messages = []

    damage = random.randint(
        attacker.attack + attacker.weapon_bonus + 2,
        attacker.attack + attacker.weapon_bonus + 5
    )

    defender.take_damage(damage)
    attacker.special_cooldown = 2

    messages.append(f"✨ Golpe Especial causa {damage} de dano!")

    return damage, messages


def special_attack_fury(attacker):
    """
    Especial Nível 6
    Buff de fúria
    40% de chance de ataque duplo por 4 turnos
    Energia: 4
    Cooldown: 3
    """

    attacker.fury_turns = 4
    attacker.special_cooldown = 3

    return 0, ["🔥 FÚRIA ATIVADA! Chance de ataque duplo por 4 turnos."]


def special_attack_stun(attacker, defender):
    """
    Especial Nível 9
    Dano alto + stun garantido
    Energia: 6
    Cooldown: 4
    """

    messages = []

    damage = random.randint(
        attacker.attack + attacker.weapon_bonus + 6,
        attacker.attack + attacker.weapon_bonus + 10
    )

    defender.take_damage(damage)
    defender.stunned = True
    attacker.special_cooldown = 4

    messages.append(f"💥 Golpe Devastador causa {damage} de dano!")
    messages.append(f"⚡ {defender.name} ficou atordoado!")

    return damage, messages


# ==================================================
# PROGRESSÃO
# ==================================================

def calculate_xp(enemy):
    """
    XP ganho ao derrotar inimigos
    """
    return 10 + enemy.level * 3


def drop_rune():
    runes = [
        ("critico", 5),
        ("sangramento", 2),
        ("stun", 5)
    ]
    return random.choice(runes)
