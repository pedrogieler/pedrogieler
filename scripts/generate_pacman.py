from pathlib import Path

WIDTH = 1200
HEIGHT = 470

PACMAN_TIME = 20


def pellet(x, y, delay=0):
    return f"""
    <circle cx="{x}" cy="{y}" r="3.3" fill="#ffe8a3">
        <animate
            attributeName="opacity"
            values="1;1;0;0;1"
            keyTimes="0;{delay:.3f};{min(delay + 0.015, 0.94):.3f};0.97;1"
            dur="{PACMAN_TIME}s"
            repeatCount="indefinite"
        />
    </circle>
    """


def static_pellet(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.3" fill="#ffe8a3"/>'


def power_pellet(x, y):
    return f"""
    <circle cx="{x}" cy="{y}" r="9" fill="#fff2c7">
        <animate
            attributeName="opacity"
            values="1;0.45;1"
            dur="0.7s"
            repeatCount="indefinite"
        />
        <animate
            attributeName="r"
            values="8;10;8"
            dur="0.7s"
            repeatCount="indefinite"
        />
    </circle>
    """


def ghost(color, path, duration, begin):
    return f"""
    <g>
        <animateMotion
            dur="{duration}s"
            begin="{begin}s"
            repeatCount="indefinite"
            rotate="auto"
            path="{path}"
        />

        <g transform="translate(-16,-16)">
            <path
                d="
                M2 31
                V16
                C2 7 8 2 16 2
                C24 2 30 7 30 16
                V31
                L26 27
                L22 31
                L17 27
                L12 31
                L7 27
                L2 31 Z
                "
                fill="{color}"
            />

            <ellipse cx="11" cy="14" rx="4.5" ry="5.5" fill="white"/>
            <ellipse cx="22" cy="14" rx="4.5" ry="5.5" fill="white"/>

            <circle cx="13" cy="15" r="2.2" fill="#164cc9"/>
            <circle cx="24" cy="15" r="2.2" fill="#164cc9"/>
        </g>
    </g>
    """


# ==========================================================
# LABIRINTO
# ==========================================================

maze = r"""
<g
    fill="none"
    stroke="#0878ff"
    stroke-width="7"
    stroke-linecap="round"
    stroke-linejoin="round"
>

    <!-- BORDA EXTERNA -->
    <rect x="45" y="90" width="1110" height="330" rx="16"/>

    <!-- TOPO ESQUERDO -->
    <path d="
        M115 130 H300
        V175
        H115
        Z
    "/>

    <!-- TOPO CENTRO ESQUERDO -->
    <path d="
        M380 130 H535
        V175
        H380
        Z
    "/>

    <!-- TOPO CENTRO DIREITO -->
    <path d="
        M665 130 H820
        V175
        H665
        Z
    "/>

    <!-- TOPO DIREITO -->
    <path d="
        M900 130 H1085
        V175
        H900
        Z
    "/>

    <!-- BLOCO MEIO ESQUERDO -->
    <path d="
        M115 230 H300
        V275
        H115
        Z
    "/>

    <!-- BLOCO MEIO DIREITO -->
    <path d="
        M900 230 H1085
        V275
        H900
        Z
    "/>

    <!-- VERTICAL ESQUERDA -->
    <path d="
        M340 205
        V305
        H385
        V205
    "/>

    <!-- VERTICAL DIREITA -->
    <path d="
        M815 205
        V305
        H860
        V205
    "/>

    <!-- CENTRO SUPERIOR -->
    <path d="
        M455 205
        H535
        V225
    "/>

    <path d="
        M665 205
        H745
        V225
    "/>

    <!-- CASA DOS FANTASMAS -->
    <path d="
        M505 310
        V250
        Q505 235 520 235
        H560
    "/>

    <path d="
        M640 235
        H680
        Q695 235 695 250
        V310
    "/>

    <path d="
        M505 310
        H695
    "/>

    <!-- INFERIOR ESQUERDO -->
    <path d="
        M115 330
        H300
        V375
        H115
        Z
    "/>

    <!-- INFERIOR CENTRAL ESQUERDO -->
    <path d="
        M385 340
        H520
        V375
        H385
        Z
    "/>

    <!-- INFERIOR CENTRAL DIREITO -->
    <path d="
        M680 340
        H815
        V375
        H680
        Z
    "/>

    <!-- INFERIOR DIREITO -->
    <path d="
        M900 330
        H1085
        V375
        H900
        Z
    "/>

</g>

<!-- PORTA ROSA DA CASA -->
<line
    x1="560"
    y1="235"
    x2="640"
    y2="235"
    stroke="#ff76d9"
    stroke-width="7"
    stroke-linecap="round"
/>
"""


# ==========================================================
# PELLETS
# ==========================================================

route_points = [
    (75, 195),
    (115, 195),
    (155, 195),
    (195, 195),
    (235, 195),
    (275, 195),
    (315, 195),
    (355, 195),
    (395, 195),
    (435, 195),
    (475, 195),
    (515, 195),
    (555, 195),
    (595, 195),
    (635, 195),
    (675, 195),
    (715, 195),
    (755, 195),
    (795, 195),
    (835, 195),
    (875, 195),
    (915, 195),
    (955, 195),
    (995, 195),
    (1035, 195),
    (1075, 195),
    (1125, 195),

    (1125, 235),
    (1125, 275),
    (1125, 315),
    (1125, 355),
    (1125, 395),

    (1085, 395),
    (1045, 395),
    (1005, 395),
    (965, 395),
    (925, 395),
    (885, 395),
    (845, 395),
    (805, 395),
    (765, 395),
    (725, 395),
    (685, 395),
    (645, 395),
    (605, 395),
    (565, 395),
    (525, 395),
    (485, 395),
    (445, 395),
    (405, 395),
    (365, 395),
    (325, 395),
    (285, 395),
    (245, 395),
    (205, 395),
    (165, 395),
    (125, 395),
    (75, 395),

    (75, 355),
    (75, 315),
    (75, 275),
    (75, 235),
]

pellets = []

total = len(route_points)

for i, (x, y) in enumerate(route_points):
    delay = 0.05 + (i / total) * 0.82
    pellets.append(
        pellet(x, y, delay)
    )


static_points = [
    (75, 115),
    (75, 150),

    (1125, 115),
    (1125, 150),

    (325, 115),
    (350, 115),

    (850, 115),
    (875, 115),

    (325, 320),
    (350, 320),

    (850, 320),
    (875, 320),

    (405, 215),
    (440, 215),
    (475, 215),

    (725, 215),
    (760, 215),
    (795, 215),

    (405, 300),
    (445, 300),
    (485, 300),

    (715, 300),
    (755, 300),
    (795, 300),
]

for x, y in static_points:
    pellets.append(
        static_pellet(x, y)
    )


powers = [
    power_pellet(75, 110),
    power_pellet(1125, 110),
    power_pellet(75, 400),
    power_pellet(1125, 400),
]


# ==========================================================
# ROTAS
# ==========================================================

pacman_path = (
    "M75 195 "
    "H435 "
    "V300 "
    "H485 "
    "V395 "
    "H815 "
    "V300 "
    "H865 "
    "V195 "
    "H1125 "
    "V395 "
    "H815 "
    "V320 "
    "H385 "
    "V395 "
    "H75 "
    "V195"
)

red_path = (
    "M600 270 "
    "H865 "
    "V195 "
    "H1125 "
    "V395 "
    "H815 "
    "V320 "
    "H600 "
    "V300 "
    "H385 "
    "V195 "
    "H75 "
    "V395 "
    "H385 "
    "V270 "
    "H600"
)

pink_path = (
    "M600 270 "
    "H385 "
    "V195 "
    "H75 "
    "V395 "
    "H385 "
    "V320 "
    "H600 "
    "V395 "
    "H815 "
    "V300 "
    "H1125 "
    "V195 "
    "H865 "
    "V270 "
    "H600"
)

cyan_path = (
    "M570 270 "
    "H385 "
    "V300 "
    "H75 "
    "V195 "
    "H385 "
    "V270 "
    "H570 "
    "V395 "
    "H815 "
    "V300 "
    "H1125 "
    "V195 "
    "H865 "
    "V270 "
    "H570"
)

orange_path = (
    "M630 270 "
    "H865 "
    "V300 "
    "H1125 "
    "V195 "
    "H865 "
    "V270 "
    "H630 "
    "V395 "
    "H385 "
    "V300 "
    "H75 "
    "V195 "
    "H385 "
    "V270 "
    "H630"
)


# ==========================================================
# SVG
# ==========================================================

svg = f"""
<svg
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    xmlns="http://www.w3.org/2000/svg"
>

    <defs>

        <filter
            id="blueGlow"
            x="-20%"
            y="-20%"
            width="140%"
            height="140%"
        >
            <feGaussianBlur
                stdDeviation="1.8"
                result="blur"
            />
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <filter
            id="yellowGlow"
            x="-30%"
            y="-30%"
            width="160%"
            height="160%"
        >
            <feGaussianBlur
                stdDeviation="2.2"
                result="blur"
            />
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

    </defs>


    <!-- FUNDO -->
    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        rx="18"
        fill="#05070c"
    />


    <!-- SCORE -->
    <text
        x="55"
        y="55"
        fill="#ffffff"
        font-family="Courier New, monospace"
        font-size="23"
        font-weight="700"
    >
        SCORE
    </text>

    <text
        x="145"
        y="55"
        fill="#ffe500"
        font-family="Courier New, monospace"
        font-size="23"
        font-weight="700"
    >
        007950
    </text>


    <!-- HIGH SCORE -->
    <text
        x="465"
        y="55"
        fill="#ffffff"
        font-family="Courier New, monospace"
        font-size="19"
        font-weight="700"
    >
        HIGH SCORE
    </text>

    <text
        x="610"
        y="55"
        fill="#ffe500"
        font-family="Courier New, monospace"
        font-size="19"
        font-weight="700"
    >
        012340
    </text>


    <!-- LIVES -->
    <text
        x="940"
        y="55"
        fill="#ffffff"
        font-family="Courier New, monospace"
        font-size="22"
        font-weight="700"
    >
        LIVES
    </text>


    <!-- 3 VIDAS -->
    <g fill="#ffe329">

        <path
            d="
            M1045 49
            L1030 39
            A17 17 0 1 0 1030 59
            Z
            "
        />

        <path
            d="
            M1082 49
            L1067 39
            A17 17 0 1 0 1067 59
            Z
            "
        />

        <path
            d="
            M1119 49
            L1104 39
            A17 17 0 1 0 1104 59
            Z
            "
        />

    </g>


    <!-- LABIRINTO -->
    <g filter="url(#blueGlow)">
        {maze}
    </g>


    <!-- PONTOS -->
    <g>
        {''.join(pellets)}
        {''.join(powers)}
    </g>


    <!-- READY -->
    <text
        x="558"
        y="220"
        fill="#ffe500"
        font-family="Courier New, monospace"
        font-size="18"
        font-weight="700"
    >
        READY!

        <animate
            attributeName="opacity"
            values="1;1;0;0"
            keyTimes="0;0.05;0.12;1"
            dur="{PACMAN_TIME}s"
            repeatCount="indefinite"
        />
    </text>


    <!-- FANTASMAS -->
    {ghost("#ff3131", red_path, 15.4, 0)}
    {ghost("#ff83dc", pink_path, 17.1, -4)}
    {ghost("#28d9ff", cyan_path, 18.7, -8)}
    {ghost("#ff9d2e", orange_path, 16.2, -11)}


    <!-- PAC-MAN -->
    <g filter="url(#yellowGlow)">

        <animateMotion
            dur="{PACMAN_TIME}s"
            repeatCount="indefinite"
            rotate="auto"
            path="{pacman_path}"
        />

        <g>

            <path
                fill="#ffe329"
                d="
                M0 0
                L16 -12
                A20 20 0 1 0 16 12
                Z
                "
            >

                <animate
                    attributeName="d"
                    values="
                    M0 0 L16 -12 A20 20 0 1 0 16 12 Z;
                    M0 0 L19.9 -2 A20 20 0 1 0 19.9 2 Z;
                    M0 0 L16 -12 A20 20 0 1 0 16 12 Z
                    "
                    dur="0.22s"
                    repeatCount="indefinite"
                />

            </path>

            <circle
                cx="4"
                cy="-9"
                r="2.5"
                fill="#05070c"
            />

        </g>

    </g>

</svg>
"""


# ==========================================================
# SALVAR
# ==========================================================

Path("assets").mkdir(
    parents=True,
    exist_ok=True
)

Path(
    "assets/pacman.svg"
).write_text(
    svg,
    encoding="utf-8"
)

print("Pac-Man profile generated successfully.")
