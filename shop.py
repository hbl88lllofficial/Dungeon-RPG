class Shop:
    def __init__(self, player):
        self.player = player
        self.finished = False
        self.log = []

    # ==========================
    # OPÇÕES DISPONÍVEIS
    # ==========================
    def get_options(self):
        return {
            "POTION_LIFE": {"name": "Poção de Vida", "cost": 10},
            "POTION_ENERGY": {"name": "Poção de Energia", "cost": 10},
            "SHIELD": {"name": "Escudo", "cost": 40},
            "BOW": {"name": "Arco e Flecha", "cost": 60},
            "WEAPON_1": {
                "name": "Espada Reforçada",
                "damage": 2,
                "sockets": 1,
                "cost": 30
            },
            "WEAPON_2": {
                "name": "Espada de Aço",
                "damage": 4,
                "sockets": 2,
                "cost": 60
            },
            "WEAPON_3": {
                "name": "Espada Lendária",
                "damage": 6,
                "sockets": 3,
                "cost": 100
            },
            "EXIT": {"name": "Sair"}
        }

    # ==========================
    # EXECUTAR COMPRA
    # ==========================
    def execute(self, option_key, confirm=False):
        self.log.clear()

        options = self.get_options()

        if option_key not in options:
            self.log.append("❌ Opção inválida.")
            return

        if option_key == "EXIT":
            self.finished = True
            self.log.append("🚪 Você saiu da loja.")
            return

        item = options[option_key]

        # ==========================
        # POÇÕES
        # ==========================
        if option_key == "POTION_LIFE":
            if self.player.gold >= item["cost"]:
                self.player.potions += 1
                self.player.gold -= item["cost"]
                self.log.append("🧪 Poção de vida comprada!")
            else:
                self.log.append("❌ Ouro insuficiente.")
            return

        if option_key == "POTION_ENERGY":
            if self.player.gold >= item["cost"]:
                self.player.energy_potions += 1
                self.player.gold -= item["cost"]
                self.log.append("⚡ Poção de energia comprada!")
            else:
                self.log.append("❌ Ouro insuficiente.")
            return

        # ==========================
        # ARMAS
        # ==========================
        if option_key.startswith("WEAPON"):
            if self.player.gold < item["cost"]:
                self.log.append("❌ Ouro insuficiente.")
                return

            if not confirm:
                self.log.append(f"⚔️ Comprar {item['name']}?")
                self.log.append(f"Dano: +{item['damage']}")
                self.log.append(f"Sockets: {item['sockets']}")
                self.log.append("Confirme a compra.")
                return

            # Confirmado
            self.player.weapon_bonus = item["damage"]
            self.player.rune_type = None
            self.player.rune_power = 0
            self.player.max_rune_slots = item["sockets"]

            self.player.gold -= item["cost"]

            self.log.append(f"✅ Você equipou {item['name']}!")
            self.log.append("🔮 Runas anteriores foram removidas.")
            return

        if option_key == "SHIELD":
            if self.player.gold >= item["cost"]:
                self.player.has_shield = True
                self.player.gold -= item["cost"]
                self.log.append("🛡️ Você comprou o Escudo! 20% de chance de bloquear ataque inimigo.")
            else:
                self.log.append("❌ Ouro insuficiente.")
            return

        if option_key == "BOW":
            if self.player.gold >= item["cost"]:
                self.player.has_bow = True
                self.player.gold -= item["cost"]
                self.log.append("🏹 Você comprou o Arco e Flecha! Bônus: golpe extra no 1º round do combate.")
            else:
                self.log.append("❌ Ouro insuficiente.")
            return
