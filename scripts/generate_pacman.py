
from pathlib import Path

svg = r'''<svg width="1200" height="260" viewBox="0 0 1200 260" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="260" rx="24" fill="#0D1117"/>

  <!-- Título pequeno estilo terminal -->
  <text x="60" y="52" fill="#58A6FF" font-family="monospace" font-size="22">github profile</text>
  <text x="60" y="84" fill="#8B949E" font-family="monospace" font-size="16">minimal mode // pacman theme</text>

  <!-- Linha do jogo -->
  <line x1="90" y1="150" x2="1110" y2="150" stroke="#30363D" stroke-width="4" stroke-dasharray="8 12"/>

  <!-- Pontos -->
  <circle cx="170" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="250" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="330" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="410" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="490" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="570" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="650" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="730" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="810" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="890" cy="150" r="7" fill="#F2CC60"/>
  <circle cx="970" cy="150" r="7" fill="#F2CC60"/>

  <!-- Pac-Man -->
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0; 780 0; 0 0" dur="9s" repeatCount="indefinite"/>
    <path d="M130 150L95 130A40 40 0 1 0 95 170L130 150Z" fill="#FFD43B">
      <animate attributeName="d"
        dur="0.35s"
        repeatCount="indefinite"
        values="
        M130 150L95 130A40 40 0 1 0 95 170L130 150Z;
        M130 150L90 145A40 40 0 1 0 90 155L130 150Z;
        M130 150L95 130A40 40 0 1 0 95 170L130 150Z" />
    </path>
    <circle cx="108" cy="136" r="4" fill="#0D1117"/>
  </g>

  <!-- Fantasma 1 -->
  <g transform="translate(920 0)">
    <animateTransform attributeName="transform" type="translate" values="0 0; -680 0; 0 0" dur="9s" repeatCount="indefinite"/>
    <path d="M0 0" fill="none"/>
    <path d="M0 150
             C0 120 20 105 45 105
             C70 105 90 120 90 150
             L90 185
             L78 175
             L66 185
             L54 175
             L42 185
             L30 175
             L18 185
             L6 175
             L0 185 Z"
          fill="#FF5C8A"/>
    <circle cx="30" cy="138" r="8" fill="white"/>
    <circle cx="60" cy="138" r="8" fill="white"/>
    <circle cx="32" cy="140" r="3.5" fill="#0D1117"/>
    <circle cx="62" cy="140" r="3.5" fill="#0D1117"/>
  </g>

  <!-- Fantasma 2 -->
  <g transform="translate(1030 0)">
    <animateTransform attributeName="transform" type="translate" values="0 0; -680 0; 0 0" dur="9s" repeatCount="indefinite"/>
    <path d="M0 150
             C0 120 20 105 45 105
             C70 105 90 120 90 150
             L90 185
             L78 175
             L66 185
             L54 175
             L42 185
             L30 175
             L18 185
             L6 175
             L0 185 Z"
          fill="#58A6FF"/>
    <circle cx="30" cy="138" r="8" fill="white"/>
    <circle cx="60" cy="138" r="8" fill="white"/>
    <circle cx="32" cy="140" r="3.5" fill="#0D1117"/>
    <circle cx="62" cy="140" r="3.5" fill="#0D1117"/>
  </g>

  <!-- Rodapé discreto -->
  <text x="60" y="225" fill="#8B949E" font-family="monospace" font-size="15">tech stack</text>
  <text x="160" y="225" fill="#F78166" font-family="monospace" font-size="15">javascript</text>
  <text x="300" y="225" fill="#58A6FF" font-family="monospace" font-size="15">html</text>
  <text x="380" y="225" fill="#A371F7" font-family="monospace" font-size="15">css</text>
  <text x="450" y="225" fill="#3FB950" font-family="monospace" font-size="15">python</text>
  <text x="560" y="225" fill="#C9D1D9" font-family="monospace" font-size="15">git</text>
  <text x="610" y="225" fill="#C9D1D9" font-family="monospace" font-size="15">github</text>
</svg>
'''

Path("assets").mkdir(exist_ok=True)
Path("assets/pacman.svg").write_text(svg, encoding="utf-8")
print("assets/pacman.svg generated successfully.")
