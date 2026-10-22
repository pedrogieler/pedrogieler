from pathlib import Path

WIDTH = 1200
HEIGHT = 470

# Tempo para o Pac-Man completar uma volta no mapa.
PACMAN_DURATION = 16


def wall(x, y, w, h, r=10):
    return f'''
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"
          fill="#05070c" stroke="#1267ff" stroke-width="7"/>

    <rect x="{x + 8}" y="{y + 8}"
          width="{w - 16}" height="{h - 16}"
          rx="{max(r - 4, 4)}"
          fill="none"
          stroke="#001b70"
          stroke-width="2"/>
    '''


def pellet(x, y, index=None):
    if index is None:
        return f'''
        <circle
            cx="{x}"
            cy="{y}"
            r="4"
            fill="#ffe6a3"
        />
        '''

    t = min(
        0.90,
        0.08 + index * 0.025
    )

    return f'''
    <circle
        cx="{x}"
        cy="{y}"
        r="4"
        fill="#ffe6a3">

        <animate
            attributeName="opacity"
            values="1;1;0;0;1"
            keyTimes="0;{t:.3f};{min(t + 0.015, 0.94):.3f};0.96;1"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
        />

    </circle>
    '''


def power_pellet(x, y):
    return f'''
    <circle
        cx="{x}"
        cy="{y}"
        r="9"
        fill="#fff1c4">

        <animate
            attributeName="r"
            values="8;11;8"
            dur="0.7s"
            repeatCount="indefinite"
        />

        <animate
            attributeName="opacity"
            values="1;0.6;1"
            dur="0.7s"
            repeatCount="indefinite"
        />

    </circle>
    '''


def ghost(color, route, duration, begin):
    return f'''
    <g>

        <animateMotion
            dur="{duration}s"
            begin="{begin}s"
            repeatCount="indefinite"
            rotate="auto"
            path="{route}"
        />

        <g transform="translate(-18,-18)">

            <path
                d="
                    M2 34
                    V18

                    C2 8 9 2 18 2
                    C27 2 34 8 34 18

                    V34

                    L29 29
                    L24 34
                    L18 29
                    L12 34
                    L7 29
                    Z
                "
                fill="{color}">

                <animate
                    attributeName="opacity"
                    values="1;1;0.82;1"
                    keyTimes="0;0.48;0.52;1"
                    dur="{duration}s"
                    repeatCount="indefinite"
                />

            </path>

            <!-- Olhos -->

            <ellipse
                cx="13"
                cy="15"
                rx="5"
                ry="6"
                fill="white"
            />

            <ellipse
                cx="25"
                cy="15"
                rx="5"
                ry="6"
                fill="white"
            />

            <circle
                cx="15"
                cy="16"
                r="2.5"
                fill="#183153"
            />

            <circle
                cx="27"
                cy="16"
                r="2.5"
                fill="#183153"
            />

        </g>

    </g>
    '''


# ============================================================
# PAREDES DO LABIRINTO
# ============================================================

walls = [

    # Borda principal
    wall(
        55,
        95,
        1090,
        320,
        14
    ),

    # Parte superior
    wall(
        140,
        120,
        185,
        48
    ),

    wall(
        400,
        120,
        160,
        48
    ),

    wall(
        640,
        120,
        160,
        48
    ),

    wall(
        875,
        120,
        185,
        48
    ),

    # Laterais centrais
    wall(
        140,
        225,
        180,
        50
    ),

    wall(
        880,
        225,
        180,
        50
    ),

    # Paredes verticais
    wall(
        350,
        220,
        45,
        95
    ),

    wall(
        805,
        220,
        45,
        95
    ),

    # Parte inferior
    wall(
        140,
        325,
        190,
        48
    ),

    wall(
        405,
        330,
        150,
        40
    ),

    wall(
        645,
        330,
        150,
        40
    ),

    wall(
        870,
        325,
        190,
        48
    ),
]


# ============================================================
# CASA DOS FANTASMAS
# ============================================================

ghost_house = '''
<path
    d="
        M505 305
        V245

        Q505 230 520 230

        H565

        M635 230

        H680

        Q695 230 695 245

        V305
        Z
    "

    fill="#05070c"
    stroke="#1267ff"
    stroke-width="7"

    stroke-linecap="round"
    stroke-linejoin="round"
/>

<line
    x1="565"
    y1="230"

    x2="635"
    y2="230"

    stroke="#ff70d5"
    stroke-width="7"

    stroke-linecap="round"
/>
'''


# ============================================================
# PONTINHOS
# ============================================================

pellets = []


# Pontinhos que desaparecem conforme o Pac-Man passa.
route_pellets = [

    (95, 190),
    (135, 190),
    (175, 190),
    (215, 190),
    (255, 190),
    (295, 190),
    (335, 190),
    (375, 190),

    (400, 210),
    (400, 245),
    (400, 280),

    (440, 300),
    (470, 300),

    (460, 335),
    (460, 365),

    (500, 385),
    (545, 385),
    (590, 385),
    (635, 385),
    (680, 385),
    (725, 385),

    (740, 350),
    (740, 315),

    (780, 300),
    (820, 300),

    (840, 280),
    (840, 245),
    (840, 210),

    (880, 190),
    (920, 190),
    (960, 190),
    (1000, 190),
    (1040, 190),
    (1080, 190),
]


for index, (x, y) in enumerate(
    route_pellets
):
    pellets.append(
        pellet(
            x,
            y,
            index
        )
    )


# Outros pontinhos espalhados pelo mapa.
static_pellets = [

    (95, 130),
    (95, 160),
    (95, 230),
    (95, 265),
    (95, 300),
    (95, 340),
    (95, 380),

    (1105, 130),
    (1105, 160),
    (1105, 230),
    (1105, 265),
    (1105, 300),
    (1105, 340),
    (1105, 380),

    (350, 130),
    (375, 130),

    (825, 130),
    (850, 130),

    (350, 350),
    (375, 350),

    (825, 350),
    (850, 350),

    (355, 190),
    (465, 190),
    (505, 190),
    (545, 190),

    (655, 190),
    (695, 190),
    (735, 190),
    (845, 190),

    (350, 300),
    (390, 300),

    (810, 300),
    (850, 300),
]


for x, y in static_pellets:
    pellets.append(
        pellet(
            x,
            y
        )
    )


# ============================================================
# POWER PELLETS
# ============================================================

power = [

    power_pellet(
        92,
        112
    ),

    power_pellet(
        1108,
        112
    ),

    power_pellet(
        92,
        398
    ),

    power_pellet(
        1108,
        398
    ),
]


# ============================================================
# ROTA DO PAC-MAN
# ============================================================

pac_route = (

    "M95 190 "

    "H400 "

    "V300 "

    "H460 "

    "V385 "

    "H740 "

    "V300 "

    "H840 "

    "V190 "

    "H1105 "

    "V300 "

    "H840 "

    "V385 "

    "H360 "

    "V300 "

    "H95 "

    "V190"
)


# ============================================================
# ROTAS DOS FANTASMAS
# ============================================================

ghost_red_route = (

    "M600 265 "

    "H840 "

    "V190 "

    "H1105 "

    "V300 "

    "H840 "

    "V385 "

    "H600 "

    "V300 "

    "H400 "

    "V190 "

    "H95 "

    "V300 "

    "H400 "

    "V265 "

    "H600"
)


ghost_pink_route = (

    "M600 265 "

    "H400 "

    "V190 "

    "H95 "

    "V300 "

    "H360 "

    "V385 "

    "H600 "

    "V300 "

    "H840 "

    "V190 "

    "H1105 "

    "V300 "

    "H840 "

    "V265 "

    "H600"
)


ghost_cyan_route = (

    "M575 265 "

    "H400 "

    "V300 "

    "H95 "

    "V190 "

    "H400 "

    "V265 "

    "H575 "

    "V385 "

    "H740 "

    "V300 "

    "H1105 "

    "V190 "

    "H840 "

    "V265 "

    "H575"
)


ghost_orange_route = (

    "M625 265 "

    "H840 "

    "V300 "

    "H1105 "

    "V190 "

    "H840 "

    "V265 "

    "H625 "

    "V385 "

    "H460 "

    "V300 "

    "H95 "

    "V190 "

    "H400 "

    "V265 "

    "H625"
)


# ============================================================
# SVG FINAL
# ============================================================

svg = f'''
<svg
    width="{WIDTH}"
    height="{HEIGHT}"

    viewBox="0 0 {WIDTH} {HEIGHT}"

    xmlns="http://www.w3.org/2000/svg"
>

    <defs>

        <filter
            id="blueGlow"
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

                <feMergeNode
                    in="blur"
                />

                <feMergeNode
                    in="SourceGraphic"
                />

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
                stdDeviation="2.6"
                result="blur"
            />

            <feMerge>

                <feMergeNode
                    in="blur"
                />

                <feMergeNode
                    in="SourceGraphic"
                />

            </feMerge>

        </filter>

    </defs>


    <!-- Fundo -->

    <rect
        width="1200"
        height="470"
        rx="20"

        fill="#05070c"
    />


    <!-- ================================================= -->
    <!-- SCORE -->
    <!-- ================================================= -->

    <text
        x="65"
        y="55"

        fill="#f4f4f4"

        font-family="'Courier New', monospace"
        font-size="24"
        font-weight="700"
    >
        SCORE
    </text>


    <text
        x="165"
        y="55"

        fill="#ffe500"

        font-family="'Courier New', monospace"
        font-size="24"
        font-weight="700"
    >
        007950
    </text>


    <!-- ================================================= -->
    <!-- HIGH SCORE -->
    <!-- ================================================= -->

    <text
        x="475"
        y="55"

        fill="#f4f4f4"

        font-family="'Courier New', monospace"
        font-size="20"
        font-weight="700"
    >
        HIGH SCORE
    </text>


    <text
        x="620"
        y="55"

        fill="#ffe500"

        font-family="'Courier New', monospace"
        font-size="20"
        font-weight="700"
    >
        012340
    </text>


    <!-- ================================================= -->
    <!-- VIDAS -->
    <!-- ================================================= -->

    <text
        x="945"
        y="55"

        fill="#f4f4f4"

        font-family="'Courier New', monospace"
        font-size="24"
        font-weight="700"
    >
        LIVES
    </text>


    <g fill="#ffe329">

        <path
            d="
                M1050 50
                L1035 40

                A18 18 0 1 0 1035 60

                Z
            "
        />

        <path
            d="
                M1090 50
                L1075 40

                A18 18 0 1 0 1075 60

                Z
            "
        />

        <path
            d="
                M1130 50
                L1115 40

                A18 18 0 1 0 1115 60

                Z
            "
        />

    </g>


    <!-- ================================================= -->
    <!-- LABIRINTO -->
    <!-- ================================================= -->

    <g filter="url(#blueGlow)">

        {''.join(walls)}

        {ghost_house}

    </g>


    <!-- ================================================= -->
    <!-- PONTOS -->
    <!-- ================================================= -->

    <g>

        {''.join(pellets)}

        {''.join(power)}

    </g>


    <!-- ================================================= -->
    <!-- FANTASMAS -->
    <!-- ================================================= -->

    {ghost(
        "#ff3131",
        ghost_red_route,
        13.8,
        0
    )}


    {ghost(
        "#ff88dd",
        ghost_pink_route,
        15.3,
        -3.2
    )}


    {ghost(
        "#21d4fd",
        ghost_cyan_route,
        16.7,
        -6.4
    )}


    {ghost(
        "#ff9d2e",
        ghost_orange_route,
        14.9,
        -8.8
    )}


    <!-- ================================================= -->
    <!-- PAC-MAN -->
    <!-- ================================================= -->

    <g filter="url(#yellowGlow)">

        <animateMotion
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
            rotate="auto"
            path="{pac_route}"
        />


        <g>

            <path
                fill="#ffe329"

                d="
                    M18 0
                    L-6 -15

                    A18 18 0 1 0 -6 15

                    Z
                "
            >

                <!-- Boca abrindo e fechando -->

                <animate
                    attributeName="d"

                    values="
                        M18 0 L-6 -15 A18 18 0 1 0 -6 15 Z;
                        M18 0 L-14 -4 A18 18 0 1 0 -14 4 Z;
                        M18 0 L-6 -15 A18 18 0 1 0 -6 15 Z
                    "

                    dur="0.24s"

                    repeatCount="indefinite"
                />

            </path>


            <!-- Olho -->

            <circle
                cx="3"
                cy="-8"

                r="2.2"

                fill="#111827"
            />

        </g>

    </g>


    <!-- ================================================= -->
    <!-- READY -->
    <!-- ================================================= -->

    <text
        x="555"
        y="215"

        fill="#ffe500"

        font-family="'Courier New', monospace"

        font-size="20"

        font-weight="700"
    >

        READY!

        <animate
            attributeName="opacity"

            values="1;1;0;0"

            keyTimes="0;0.05;0.10;1"

            dur="{PACMAN_DURATION}s"

            repeatCount="indefinite"
        />

    </text>

</svg>
'''


# ============================================================
# SALVAR ARQUIVO
# ============================================================

Path(
    "assets"
).mkdir(
    parents=True,
    exist_ok=True
)


Path(
    "assets/pacman.svg"
).write_text(
    svg,
    encoding="utf-8"
)


print(
    "assets/pacman.svg generated successfully."
)
