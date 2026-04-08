import random
from entities import create_enemy
from actions import calculate_xp


# ==============================
# CONFIGURAÇÃO
# ==============================

ROOM_WEIGHTS = {
    "INIMIGO": 40,
    "ITEM": 25,
    "ARMADILHA": 20,
    "SANTUARIO": 15
}

RELICS = [
    {"name": "🗿 Amuleto da Vitalidade", "type": "vida", "value": 10},
    {"name": "⚔ Talismã de Guerra", "type": "dano", "value": 1},
    {"name": "🪙 Moeda Antiga", "type": "ouro", "value": 0.1},
]


# ==============================
# DUNGEON MANAGER
# ==============================

class Dungeon:

    def __init__(self, player):
        self.player = player
        self.room_count = 0
        self.current_rooms = None
        self.log = []
        self.state = "ROOM_CHOICE"  # ROOM_CHOICE / COMBAT / SHOP / FINISHED

    # ==========================
    # GERAR SALA
    # ==========================

    def generate_room(self):
        rooms = list(ROOM_WEIGHTS.keys())
        weights = list(ROOM_WEIGHTS.values())
        return random.choices(rooms, weights=weights, k=1)[0]

    def generate_two_rooms(self):
        return self.generate_room(), self.generate_room()

    # ==========================
    # AVANÇAR SALA
    # ==========================

    def next_room(self):
        self.log.clear()
        self.room_count += 1

        self.log.append(f"🏰 SALA {self.room_count}")

        # 👑 BOSS
        if self.room_count % 10 == 0:
            self.log.append("👑 UM BOSS APARECEU!")
            self.state = "BOSS"
            return "BOSS"

        # 🛒 LOJA
        if self.room_count % 5 == 0:
            self.log.append("🛒 Você encontrou uma loja.")
            self.state = "SHOP"
            return "SHOP"

        # 🎲 SALAS NORMAIS
        self.current_rooms = self.generate_two_rooms()
        self.log.append("🚪 Duas portas aparecem diante de você.")
        self.log.append("Escolha 1 ou 2.")

        self.state = "ROOM_CHOICE"
        return "ROOM_CHOICE"

    # ==========================
    # ESCOLHER SALA
    # ==========================

    def choose_room(self, option):
        if self.state != "ROOM_CHOICE":
            return None

        self.log.clear()

        if option == 1:
            room_type = self.current_rooms[0]
        elif option == 2:
            room_type = self.current_rooms[1]
        else:
            self.log.append("❌ Opção inválida.")
            return None

        self.log.append(f"🚪 Você entrou em: {room_type}")
        return self.resolve_room(room_type)

    # ==========================
    # RESOLVER SALA
    # ==========================

    def resolve_room(self, room_type):

        if room_type == "INIMIGO":
            self.state = "COMBAT"
            return "COMBAT"

        elif room_type == "ITEM":
            self.log.append("🎁 Você encontrou um baú!")

            if random.random() < 0.15:
                relic = random.choice(RELICS)
                self.player.add_relic(relic)
                self.log.append(f"✨ Relíquia adquirida: {relic['name']}")
            
            # Baús sempre fazem drop de itens, além de possível relíquia
            self.handle_loot()

        elif room_type == "ARMADILHA":
            damage = random.randint(5, 12)
            self.player.take_damage(damage)
            self.log.append(f"☠ Armadilha! Você sofreu {damage} de dano!")

            if random.random() < 0.3:
                self.player.bleed_turns = 2
                self.log.append("🩸 Você começou a sangrar!")

        elif room_type == "SANTUARIO":
            heal = random.randint(10, 25)
            energy = random.randint(5, 15)

            self.player.life = min(self.player.max_life, self.player.life + heal)
            self.player.energy = min(self.player.max_energy, self.player.energy + energy)

            self.log.append(
                f"⛩ Santuário restaurou {heal} vida e {energy} energia!"
            )

        return "ROOM_RESOLVED"

    # ==========================
    # LOOT
    # ==========================

    def handle_loot(self):
        roll = random.random()

        if roll < 0.40:
            gold = random.randint(10, 30)
            self.player.gold += gold
            self.log.append(f"💰 Você encontrou {gold} de ouro.")

        elif roll < 0.60:
            self.player.potions += 1
            self.log.append("🧪 Você encontrou uma poção de vida.")

        elif roll < 0.75:
            self.player.energy_potions += 1
            self.log.append("⚡ Você encontrou uma poção de energia.")

        elif roll < 0.80:
            self.player.explosive_grenades += 1
            self.log.append("💥 Você encontrou uma granada explosiva.")

        elif roll < 0.85:
            self.player.smoke_grenades += 1
            self.log.append("💨 Você encontrou uma granada de fumaça.")

        elif roll < 0.85:
            self.player.flash_grenades += 1
            self.log.append("⚡ Você encontrou uma granada flash.")

        elif roll < 0.90:
            self.player.apply_upgrade_rune()
            self.log.append("🔮 Runa de aprimoramento aplicada!")

        else:
            rune_type, rune_value = random.choice([
                ("crit", 5),
                ("bleed", 2),
                ("stun", 5)
            ])

            self.player.equip_rune(rune_type, rune_value)
            self.log.append(
                f"✨ Runa equipada: {rune_type.upper()} (+{rune_value})"
            )

    def handle_enemy_drop(self):
        """
        Inimigos fazem drop de itens com 30% de probabilidade
        Probabilidade menor que os baús (100%), baseado nos mesmos itens disponíveis
        """
        # 30% de chance de fazer drop
        if random.random() < 0.30:
            roll = random.random()

            if roll < 0.40:
                gold = random.randint(5, 15)
                self.player.gold += gold
                self.log.append(f"💰 Inimigo deixou cair {gold} de ouro.")

            elif roll < 0.60:
                self.player.potions += 1
                self.log.append("🧪 Inimigo deixou cair uma poção de vida.")

            elif roll < 0.75:
                self.player.energy_potions += 1
                self.log.append("⚡ Inimigo deixou cair uma poção de energia.")

            elif roll < 0.80:
                self.player.explosive_grenades += 1
                self.log.append("💥 Inimigo deixou cair uma granada explosiva.")

            elif roll < 0.85:
                self.player.smoke_grenades += 1
                self.log.append("💨 Inimigo deixou cair uma granada de fumaça.")

            elif roll < 0.90:
                self.player.flash_grenades += 1
                self.log.append("⚡ Inimigo deixou cair uma granada flash.")

            elif roll < 0.95:
                self.player.apply_upgrade_rune()
                self.log.append("🔮 Runa de aprimoramento obtida do inimigo!")

            else:
                rune_type, rune_value = random.choice([
                    ("crit", 5),
                    ("bleed", 2),
                    ("stun", 5)
                ])

                self.player.equip_rune(rune_type, rune_value)
                self.log.append(
                    f"✨ Runa do inimigo equipada: {rune_type.upper()} (+{rune_value})"
                )
