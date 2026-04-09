Dungeon RPG - Documentação do Backend
=====================================

Resumo
------
Este arquivo descreve o funcionamento do backend do projeto "Dungeon RPG". Ele detalha as bibliotecas utilizadas, a arquitetura entre os módulos Python e explica função por função as mecânicas e interações. O arquivo cobre todos os módulos exceto o `main.py` (UI / startup), conforme solicitado.

Requisitos / Bibliotecas
------------------------
- Python 3.8+ (recomendado).  
- Módulos usados (padrão / opcionais):
  - `tkinter` (GUI) — presente no `main.py`.  
  - `random` (padrão) — usado para sorteios e probabilidades em vários módulos.  
  - `Pillow` (opcional) — `PIL` (importado em `main.py`) para redimensionar/carregar imagens se disponível.  
  - `pygame` (opcional) — usado no `main.py` para som se instalado; caso contrário há fallback `winsound` (Windows).  

Observação: Para empacotamento em Windows use `PyInstaller` (opcional) — inclua a pasta `assets` com `--add-data "assets;assets"` e use a função `resource_path()` (já adicionada em `main.py`) para localizar recursos quando empacotado.

Visão geral dos arquivos backend (não inclui `main.py`)
-----------------------------------------------------
- `entities.py` — definição de `Character` (jogador/inimigo) e `create_enemy()` (fábrica de inimigos).
- `actions.py` — lógica de ataque básico, ataques especiais e funções utilitárias (XP, drop de runas).
- `combat.py` — classe `Combat` que coordena o loop de turno, aplica efeitos e produz logs para a UI.
- `dungeon.py` — gerenciador de salas (geração de tipo de sala, loot, loja, bosses, progressão de sala).
- `shop.py` — definição da `Shop` com opções e lógica de compra.

Dependências e importações entre arquivos
----------------------------------------
- `entities.py` importa internamente funções de `actions.py` quando necessário (por import local dentro de métodos) — e `entities.create_enemy()` é importado por `dungeon.py`.
- `combat.py` chama métodos de `Character` (do `entities.py`) e depende que `Character.attack_target()` utilize `actions.attack()`.
- `dungeon.py` importa `create_enemy` de `entities` e `calculate_xp` de `actions`.
- `shop.py` opera diretamente sobre a instância `player` (um `Character`) e altera atributos como `gold`, `weapon_bonus`, `has_shield`, etc.

Descrição por arquivo (detalhada)
--------------------------------

`actions.py`
~~~~~~~~~~~~~
- Funções principais:
  - `attack(attacker, defender)`
    - Parâmetros: `attacker` e `defender` são instâncias de `Character`.
    - Comportamento: calcula `base_damage` = `attacker.attack + attacker.weapon_bonus`. Determina dano aleatório entre 1 e `base_damage`. Antes de aplicar dano, verifica efeitos como bloqueio de escudo (20% se `defender.has_shield`), crítico (se `attacker.rune_type == 'crit'`, chance base 10% + 5% por `rune_power`), sangramento (aplica `defender.bleed_turns += rune_power`) e stun (dependendo de `rune_power`). Aplica `defender.take_damage(damage)` e retorna `(damage, messages)`.
  - `special_attack_basic(attacker, defender)`
    - Dano maior, define `attacker.special_cooldown = 2`. Retorna `(damage, messages)`.
  - `special_attack_fury(attacker)`
    - Buff que seta `attacker.fury_turns = 4` e cooldown. Retorna mensagens.
  - `special_attack_stun(attacker, defender)`
    - Dano alto e aplica `defender.stunned = True`, define `attacker.special_cooldown = 4`.
  - `calculate_xp(enemy)` — retorna XP base dado o `enemy.level`.
  - `drop_rune()` — escolhe aleatoriamente uma runa (tipo e valor) — usado por loot/baús (ainda que `dungeon.py` tenha uma implementação própria de escolha de runa também).

Mecânicas importantes em `actions.py`:
- Runas: afetam crítico, sangramento e stun. São verificadas no `attack()` e podem provocar efeitos adicionais (dobrar dano, aplicar `bleed_turns`, atordoar).
- Especial: cada especial consome energia (tratada no `Character.use_special`) e aplica cooldowns.


`combat.py`
~~~~~~~~~~~~
- Classe `Combat`:
  - `__init__(self, player, enemy)` — armazena referências, flags `finished`, `victory` e `log`.
  - `get_actions()` — lista de ações válidas (strings) que a UI apresenta.
  - `execute_action(self, action)` — função central que executa um turno completo:
    1. Limpa `self.log` e adiciona linha de cabeçalho.  
    2. Aplica efeitos contínuos (sangramento) chamando `apply_bleed()` dos `Character`s e registrando no log.  
    3. Resolve a ação do jogador: `ATACAR` → chama `self.player.attack_target(self.enemy)`; `ESPECIAL` → busca `self.player.get_special_options()` e chama `use_special`; poções e granadas chamam os métodos respectivos do `Character`; `FUGIR` tem 50% de sucesso.  
    4. Verifica morte do inimigo.  
    5. Reduz efeitos de turnos (`reduce_turn_effects`).  
    6. Turno do inimigo: se `stunned` ou `stun_turns > 0` perde turno; caso contrário chama `self.enemy.attack_target(self.player)` e registra dano/mensagens.  
    7. No fim, reduz efeitos novamente e verifica morte do jogador.  

  - `get_player_status()` / `get_enemy_status()` — retornam dicionários usados pela UI para mostrar barras, valores e ícones.

Mecânica: `Combat` é o coordenador do fluxo turn-based. Ele mantém `self.log` com mensagens que a interface (`main.py`) mostra ao jogador.


`dungeon.py`
~~~~~~~~~~~~~
- Constantes:
  - `ROOM_WEIGHTS` — pesos relativos para geração de tipos de sala (INIMIGO, ITEM, ARMADILHA, SANTUARIO).
  - `RELICS` — lista de relíquias possíveis com efeitos simples (vida, dano, ouro).

- `Dungeon` (classe): gerencia a progressão de salas e loot.
  - `__init__(self, player)` — guarda `player` (`Character`) e inicia estado.
  - `generate_room()` / `generate_two_rooms()` — usa `random.choices` com `ROOM_WEIGHTS` para decidir tipos de sala.
  - `next_room()` — incrementa `room_count`, decide se é `BOSS` (a cada 10 salas) ou `SHOP` (a cada 5) ou cria duas portas normais e retorna `ROOM_CHOICE`.
  - `choose_room(option)` — valida escolha 1/2, escreve no `log` e chama `resolve_room` com o tipo selecionado.
  - `resolve_room(room_type)` — lida com cada tipo:
    - `INIMIGO`: define `self.state = 'COMBAT'` e retorna `COMBAT` (a UI cria `Combat` e chama `start_combat`).
    - `ITEM`: chance de relíquia (15%) com `player.add_relic()`; chama `handle_loot()` que aplica uma das recompensas (ouro, poções, granadas, runas, etc.).
    - `ARMADILHA`: causa dano aleatório e possivelmente aplica sangramento.
    - `SANTUARIO`: cura vida e energia.
  - `handle_loot()` — distribuição de itens por probabilidades (ouro, poções, granadas, runas, upgrades). Aplica direto no `player`.
  - `handle_enemy_drop()` — lógica parecida com `handle_loot()` mas com chances menores (30% de drop) ao derrotar inimigos.

Interações: `Dungeon` depende de `entities.create_enemy` para criar inimigos (quando o fluxo chegar em `COMBAT`) e usa `actions.calculate_xp` para calcular XP quando necessário.


`entities.py`
~~~~~~~~~~~~~~
- `Character` (classe): representa jogador e inimigos. Contém atributos de estado (vida, ataque, energia), itens e efeitos temporários.

Campos notáveis:
  - `max_life`, `life`, `attack`, `weapon_bonus`, `block_chance`  
  - `level`, `xp`, `xp_to_next_level`  
  - inventário: `potions`, `energy_potions`, `gold`  
  - granadas: `explosive_grenades`, `smoke_grenades`, `flash_grenades`  
  - energia: `max_energy`, `energy`  
  - especiais: `special_cooldown`, `fury_turns`  
  - runas: `rune_type`, `rune_power`  
  - efeitos: `bleed_turns`, `bleed_damage`, `stunned`, `stun_turns`, `smoke_turns`  
  - equipáveis: `has_shield`, `has_bow`, `weapon`, `weapon_attack`, `relics`  

Métodos principais:
  - `attack_target(self, target)`
    - Importa `attack` de `actions` localmente. Implementa a mecânica de `fury_turns` (chance de ataque duplo) e delega o cálculo para `actions.attack`. Retorna `(total_damage, messages)`.

  - `get_special_options(self)`
    - Retorna um dicionário com os especiais disponíveis de acordo com o nível (BASIC, FURY, STUN) e o custo de energia.

  - `use_special(self, special_type, target)`
    - Valida cooldown/energia, decrementa energia e chama as funções em `actions.py` correspondentes: `special_attack_basic`, `special_attack_fury`, `special_attack_stun`.

  - `take_damage(self, damage)`
    - Aplica chance de esquiva se `smoke_turns>0` (30%). Caso contrário considera `block_chance` (reduz dano pela metade) e decrementa `life`. Retorna dano aplicado.

  - `apply_bleed(self)` — reduz `life` pelo `bleed_damage` e decrementa `bleed_turns`.

  - Poções: `use_potion()` e `use_energy_potion()` — restauram vida/energia e atualizam contadores.

  - Granadas: `use_explosive_grenade(target)`, `use_smoke_grenade()`, `use_flash_grenade(target)` — aplicam efeitos conforme descrito no nome (dano grande, 3 turnos de esquiva, atordoamento no alvo por 3 turnos), atualizam contadores.

  - Turnos e efeitos: `reduce_turn_effects()` — decrementa cooldowns e turnos de efeitos (fury, smoke, stun, etc.).

  - Progressão: `gain_xp(amount)` e `level_up()` — adiciona XP, sobe níveis, aplica bônus automáticos (vida e ataque), e prepara texto para UI pedir escolha de bônus adicional. `apply_level_bonus(choice)` aplica o bônus escolhido pelo jogador.

  - Runas e relíquias: `equip_rune(rune_type, value)`, `apply_upgrade_rune()` (aprimora arma permanentemente), `add_relic(relic)` (aplica efeitos imediatos de relíquia: vida/dano/ouro).

  - `is_alive()` — utilitário booleano.

Fábrica de inimigos:
  - `create_enemy(player_level, room_count=0, boss=False)` — cria instâncias `Character` com stats escalonados por `player_level` e `room_count`. Se `boss=True` aplica multiplicadores e configura temas (tirano, executor, corrompido, sentinela) com modificadores específicos.


`shop.py`
~~~~~~~~~
- `Shop` (classe): gerencia opções de compra e aplica efeitos na instância `player`.
  - `get_options()` — retorna um dicionário com chaves (ex: `POTION_LIFE`, `WEAPON_1`, `SHIELD`, `BOW`, `EXIT`) e dados do item (`name`, `cost`, `damage`, `sockets`).
  - `execute(self, option_key, confirm=False)` — lógica principal:
    - Valida `option_key`.  
    - Se `EXIT` marca `finished = True`.  
    - Poções: checa ouro e incrementa o contador correspondente.  
    - Armas: se o jogador não tiver ouro suficiente solicita confirmação (`confirm=False` faz apenas a prévia mostrando os detalhes); se confirmado aplica `player.weapon_bonus = damage`, remove runas atuais (`player.rune_type = None`, `player.rune_power = 0`) e define `player.max_rune_slots`. Deduz ouro.  
    - `SHIELD` e `BOW` atualizam `player.has_shield` e `player.has_bow` e deduzem ouro.

Observações: `execute()` devolve mensagens em `self.log` e depende fortemente dos atributos do `player` para aplicar efeitos.


Fluxo de chamadas resumido (exemplo de combate)
--------------------------------------------
1. `main.py` (UI) chama `Dungeon.next_room()`.  
2. Se for `COMBAT`, `main.py` cria `Combat(player, enemy)` onde `enemy` vem de `create_enemy()` do `entities.py`.  
3. Quando o jogador escolhe `ATACAR`, a UI chama `Combat.execute_action('ATACAR')`.  
4. `Combat.execute_action` chama `player.attack_target(enemy)` (método em `entities.py`).  
5. `attack_target` importa e usa `actions.attack(attacker, defender)` (lógica de dano e runas).  
6. `actions.attack` chama `defender.take_damage(damage)` (método em `entities.py`) para aplicar o dano.  
7. Eventos como drop/loot/back to dungeon usam `Dungeon.handle_enemy_drop()` e `actions.calculate_xp()` para calcular XP e `player.gain_xp()` para progressão.


Extensões e como modificar o backend
-----------------------------------
- Adicionar uma nova arma:  
  - Atualize `shop.get_options()` em `shop.py` adicionando nova `WEAPON_X` com `damage`, `sockets` e `cost`.  
  - A lógica de compra já ajusta `player.weapon_bonus` e `max_rune_slots`.

- Adicionar nova runa/efeito:  
  - Em `actions.py`, expanda `attack()` para reconhecer novo `rune_type` e aplicar efeitos correspondentes (ex.: veneno de longo prazo).  
  - Ajuste UI / textos no `main.py` para exibir descrições se desejar.

- Ajustar balanceamento: 
  - Modifique `ROOM_WEIGHTS` e `RELICS` em `dungeon.py` para alterar frequências e tipos de relíquias.  
  - Ajuste valores base em `entities.create_enemy()` (vida/ataque) para mudar curva de dificuldade.


Dicas para empacotamento (Windows)
---------------------------------
- Recomendado: criar um ambiente virtual e instalar `pyinstaller`:  
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate
  pip install pyinstaller
  ```
- Comando sugerido para gerar `.exe` único e incluir `assets`:
  ```powershell
  pyinstaller --onefile --noconsole --add-data "assets;assets" main.py
  ```
- Certifique-se de que `main.py` use `resource_path()` para acessar arquivos em `assets` quando empacotado (já está adicionado).


Notas finais
-----------
- O backend foi projetado com classes e funções pequenas e fáceis de estender. A separação entre: (i) lógica de combate/ataque (`actions.py`), (ii) entidade/jogador/inimigo (`entities.py`), (iii) fluxo de combate (`combat.py`) e (iv) gerência de dungeon/loots (`dungeon.py`) permite alterações localizadas sem tocar a UI (`main.py`).
- Se quiser, posso também gerar uma versão `README.md` em Markdown, adicionar diagramas de chamadas, ou documentar linha-a-linha funções específicas com exemplos de entrada/saída.

Arquivo gerado: `readme.txt`
