import random

class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.finished = False
        self.victory = None
        self.log = []

    # =========================
    # AÇÕES DISPONÍVEIS
    # =========================
    def get_actions(self):
        actions = [
            "ATACAR",
            "ESPECIAL",
            "POÇÃO_VIDA",
            "POÇÃO_ENERGIA",
            "GRANADA_EXPLOSIVA",
            "GRANADA_FUMAÇA",
            "GRANADA_FLASH",
            "FUGIR"
        ]
        return actions

    # =========================
    # EXECUTA UMA AÇÃO
    # =========================
    def execute_action(self, action):
        if self.finished:
            return

        self.log.clear()

        self.log.append(f"⚔️ Combate: {self.player.name} vs {self.enemy.name}")

        # =========================
        # EFEITOS CONTÍNUOS
        # =========================
        if self.player.bleed_turns > 0:
            self.player.apply_bleed()
            self.log.append("🩸 Você sofre sangramento.")

        if self.enemy.bleed_turns > 0:
            self.enemy.apply_bleed()
            self.log.append("🩸 O inimigo sofre sangramento.")

        # =========================
        # TURNO DO JOGADOR
        # =========================
        if action == "ATACAR":
            damage, messages = self.player.attack_target(self.enemy)
            self.log.append(f"🗡 Você causou {damage} de dano!")
            self.log.extend(messages)

        elif action == "ESPECIAL":

            options = self.player.get_special_options()

            if not options:
                self.log = ["❌ Nenhum especial disponível."]
                return

            special_type = list(options.keys())[0]

            messages = self.player.use_special(special_type, self.enemy)
            self.log = messages

        elif action == "POÇÃO_VIDA":
            self.player.use_potion()

        elif action == "POÇÃO_ENERGIA":
            self.player.use_energy_potion()

        elif action == "GRANADA_EXPLOSIVA":
            messages = self.player.use_explosive_grenade(self.enemy)
            self.log.extend(messages)

        elif action == "GRANADA_FUMAÇA":
            messages = self.player.use_smoke_grenade()
            self.log.extend(messages)

        elif action == "GRANADA_FLASH":
            messages = self.player.use_flash_grenade(self.enemy)
            self.log.extend(messages)

        elif action == "FUGIR":
            if random.random() < 0.5:
                self.log.append("🏃 Você fugiu com sucesso!")
                self.finished = True
                self.victory = False
                return
            else:
                self.log.append("❌ Falha ao fugir!")

        else:
            self.log.append("❌ Ação inválida!")

        # =========================
        # VERIFICA MORTE DO INIMIGO
        # =========================
        if not self.enemy.is_alive():
            self.finished = True
            self.victory = True
            self.log.append(f"🏆 Você derrotou {self.enemy.name}!")
            return

        # =========================
        # REDUZ EFEITOS DE TURNO
        # =========================
        self.player.reduce_turn_effects()
        self.enemy.reduce_turn_effects()

        # =========================
        # TURNO DO INIMIGO
        # =========================
        if self.enemy.stunned or self.enemy.stun_turns > 0:
            self.log.append(f"⚡ {self.enemy.name} está atordoado e perde o turno!")
            if self.enemy.stunned:
                self.enemy.stunned = False
            if self.enemy.stun_turns > 0:
                self.enemy.stun_turns -= 1
        else:
            enemy_damage, enemy_messages = self.enemy.attack_target(self.player)
            self.log.append(f"👾 {self.enemy.name} causou {enemy_damage} de dano!")
            self.log.extend(enemy_messages)

        # =========================
        # FIM DO TURNO
        # =========================
        self.player.reduce_turn_effects()
        self.enemy.reduce_turn_effects()

        # =========================
        # VERIFICA MORTE DO JOGADOR
        # =========================
        if not self.player.is_alive():
            self.finished = True
            self.victory = False
            self.log.append("💀 Você foi derrotado...")

    # =========================
    # STATUS (PARA UI)
    # =========================
    def get_player_status(self):
        return {
            "vida": f"{self.player.life}/{self.player.max_life}",
            "energia": f"{self.player.energy}/{self.player.max_energy}",
            "ataque": f"{self.player.attack} (+{self.player.weapon_bonus})",
            "bloqueio": int(self.player.block_chance * 100),
            "potions": self.player.potions,
            "energy_potions": self.player.energy_potions,
            "ouro": self.player.gold,
            "especial_cd": self.player.special_cooldown,
            "furia": self.player.fury_turns,
            "runa": self.player.rune_type,
            "reliquias": [r["name"] for r in self.player.relics]
        }

    def get_enemy_status(self):
        return {
            "nome": self.enemy.name,
            "vida": f"{self.enemy.life}/{self.enemy.max_life}"
        }
