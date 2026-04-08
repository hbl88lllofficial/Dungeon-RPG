Adicionar imagens e sons para a parte visual do jogo

Como usar esta pasta:

- Coloque imagens PNG/GIF com os nomes opcionais abaixo para que o jogo carregue automaticamente:
  - `player.png`  — sprite/imagem do jogador (recomendado 160x160)
  - `enemy.png`   — sprite/imagem do inimigo (recomendado 160x160)
  - `room.png`    — imagem de fundo da sala (opcional)

- Coloque efeitos sonoros em formato WAV ou MP3 com os nomes sugeridos:
  - `attack.wav` / `attack.mp3`        — som de ataque
  - `explosion.wav` / `explosion.mp3`  — som de granada/explosão
  - `special.wav` / `special.mp3`      — som de habilidade especial
  - `combat_start.wav`                  — início de combate
  - `room.wav`                          — som ambiente de sala
  - `door.wav`                          — som de porta
  - `victory.wav`                       — vitória
  - `defeat.wav`                        — derrota

Dependências opcionais (para som):
- Recomenda-se instalar `pygame` para reprodução de sons e melhor controle de áudio.
  - Instalar: `pip install pygame`
  - Se `pygame` não estiver disponível, o jogo tentará usar um beep simples no Windows como fallback.

Observações:
- Se nenhuma imagem estiver presente, o jogo desenhará formas básicas (círculos/retângulos) na tela.
- Para melhores resultados, use PNGs com fundo transparente.
- Se desejar adicionar sprites animados, você pode estender a classe `Render` em `main.py`.

Exemplo de uso:
- Coloque `player.png` e `enemy.png` nesta pasta.
- Coloque `attack.wav` e `explosion.wav` para efeitos sonoros.
- Execute o jogo normalmente: `python main.py`

Gerador automático de placeholders:
- Existe um script `generate_placeholders.py` nesta pasta que cria imagens simples e arquivos WAV.
- Executar:

```bash
python assets/generate_placeholders.py
```

Isso facilita testar a interface/sons sem arquivos externos.