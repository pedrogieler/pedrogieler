from pathlib import Path

WIDTH = 1200
HEIGHT = 470

# Tempo de uma volta completa do Pac-Man
PACMAN_DURATION = 16


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def wall(x, y, w, h, r=10):
    return f"""
    <rect
        x="{x}"
        y="{y}"
        width="{w}"
        height="{h}"
        rx="{r}"
        fill="#05070c"
        stroke="#1267ff"
        stroke-width="7"
    />

    <rect
        x="{x + 8}"
        y="{y + 8}"
        width="{w - 16}"
        height="{h - 16}"
        rx="{max(r - 4, 4)}"
        fill="none"
        stroke="#001b70"
        stroke-width="2"
    />
    """


def pellet(x, y, index=None):
    if index is None:
        return f"""
        <circle
            cx="{x}"
            cy="{y}"
            r="4"
            fill="#ffe6a3"
        />
        """

    # Faz os pontos desaparecerem aproximadamente
    # na sequência em que o Pac-Man passa.
    t = min(0.88, 0.07 + index * 0.023)

    return f"""
    <circle
        cx="{x}"
        cy="{y}"
        r="4"
        fill="#ffe6a3"
    >
        <animate
            attributeName="opacity"
            values="1;1;0;0;1"
            keyTimes="0;{t:.3f};{min(t + 0.015, 0.93):.3f};0.96;1"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
        />
    </circle>
    """


def power_pellet(x, y):
    return f"""
    <circle
        cx="{x}"
        cy="{y}"
        r="10"
        fill="#fff1c4"
    >
        <animate
            attributeName="r"
            values="8;11;8"
            dur="0.65s"
            repeatCount="indefinite"
        />

        <animate
            attributeName="opacity"
            values="1;0.55;1"
            dur="0.65s"
            repeatCount="indefinite"
        />
    </circle>
    """


def ghost(color, route, duration, begin):
    return f"""
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
                fill="{color}"
            />

            <!-- OLHOS -->

            <ellipse
                cx="13"
                cy="15"
                rx="5"
                ry="6"
                fill="#ffffff"
            />

            <ellipse
                cx="25"
                cy="15"
                rx="5"
                ry="6"
                fill="#ffffff"
            />

            <circle
                cx="15"
                cy="16"
                r="2.5"
                fill="#163c96"
            />

            <circle
                cx="27"
                cy="16"
                r="2.5"
                fill="#163c96"
            />

        </g>

    </g>
    """


# ============================================================
# LABIRINTO
# ============================================================

walls = [

    # Borda externa
    wall(
        55,
        95,
        1090,
        320,
        14
    ),

    # Linha superior
    wall(
        130,
        120,
        180,
        48
    ),

    wall(
        385,
        120,
        175,
        48
    ),

    wall(
        640,
        120,
        175,
        48
    ),

    wall(
        890,
        120,
        180,
        48
    ),

    # Meio esquerdo
    wall(
        130,
        225,
        180,
        50
    ),

    # Meio direito
    wall(
        890,
        225,
        180,
        50
    ),

    # Verticais esquerda
    wall(
        345,
        205,
        45,
        105
    ),

    # Verticais direita
    wall(
        810,
        205,
        45,
        105
    ),

    # Inferior esquerda
    wall(
        130,
        325,
        180,
        48
    ),

    # Inferior centro esquerda
    wall(
        405,
        330,
        145,
        40
    ),

    # Inferior centro direita
    wall(
        650,
        330,
        145,
        40
    ),

    # Inferior direita
    wall(
        890,
        325,
        180,
        48
    ),
]


# ============================================================
# CASA DOS FANTASMAS
# ============================================================

ghost_house = """
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
"""


# ============================================================
# PONTOS
# ============================================================

route_pellets = [

    (90, 190),
    (125, 190),
    (160, 190),
    (195, 190),
    (230, 190),
    (265, 190),
    (300, 190),
    (335, 190),
    (370, 190),

    (410, 190),
    (450, 190),
    (490, 190),
    (530, 190),
    (570, 190),

    (630, 190),
    (670, 190),
    (710, 190),
    (750, 190),
    (790, 190),

    (830, 190),
    (870, 190),
    (910, 190),
    (950, 190),
    (990, 190),
    (1030, 190),
    (1070, 190),
    (1110, 190),

    (1110, 230),
    (1110, 270),
    (1110, 310),
    (1110, 350),
    (1110, 390),

    (1070, 390),
    (1030, 390),
    (990, 390),
    (950, 390),
    (910, 390),
    (870, 390),
    (830, 390),

    (790, 390),
    (750, 390),
    (710, 390),
    (670, 390),
    (630, 390),
    (590, 390),
    (550, 390),
    (510, 390),
    (470, 390),
    (430, 390),
    (390, 390),
    (350, 390),

    (310, 390),
    (270, 390),
    (230, 390),
    (190, 390),
    (150, 390),
    (110, 390),

    (90, 350),
    (90, 310),
    (90, 270),
    (90, 230),
]


pellets = []

for index, (x, y) in enumerate(route_pellets):
    pellets.append(
        pellet(
            x,
            y,
            index
        )
    )


# Pontos internos que não precisam desaparecer
static_pellets = [

    (90, 120),
    (90, 150),

    (1110, 120),
    (1110, 150),

    (335, 125),
    (360, 125),

    (840, 125),
    (865, 125),

    (335, 340),
    (360, 340),

    (840, 340),
    (865, 340),

    (405, 215),
    (445, 215),
    (485, 215),

    (715, 215),
    (755, 215),
    (795, 215),

    (410, 295),
    (450, 295),

    (750, 295),
    (790, 295),
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

power_pellets = [

    power_pellet(
        90,
        110
    ),

    power_pellet(
        1110,
        110
    ),

    power_pellet(
        90,
        400
    ),

    power_pellet(
        1110,
        400
    ),
]


# ============================================================
# ROTA DO PAC-MAN
# ============================================================

pac_route = (
    "M90 190 "
    "H390 "
    "V295 "
    "H455 "
    "V390 "
    "H810 "
    "V295 "
    "H855 "
    "V190 "
    "H1110 "
    "V390 "
    "H810 "
    "V320 "
    "H390 "
    "V390 "
    "H90 "
    "V190"
)


# ============================================================
# ROTAS DOS FANTASMAS
# ============================================================

red_route = (
    "M600 260 "
    "H855 "
    "V190 "
    "H1110 "
    "V390 "
    "H810 "
    "V320 "
    "H600 "
    "V295 "
    "H390 "
    "V190 "
    "H90 "
    "V390 "
    "H390 "
    "V260 "
    "H600"
)


pink_route = (
    "M600 260 "
    "H390 "
    "V190 "
    "H90 "
    "V390 "
    "H390 "
    "V320 "
    "H600 "
    "V390 "
    "H810 "
    "V295 "
    "H1110 "
    "V190 "
    "H855 "
    "V260 "
    "H600"
)


cyan_route = (
    "M570 260 "
    "H390 "
    "V295 "
    "H90 "
    "V190 "
    "H390 "
    "V260 "
    "H570 "
    "V390 "
    "H810 "
    "V295 "
    "H1110 "
    "V190 "
    "H855 "
    "V260 "
    "H570"
)


orange_route = (
    "M630 260 "
    "H855 "
    "V295 "
    "H1110 "
    "V190 "
    "H855 "
    "V260 "
    "H630 "
    "V390 "
    "H390 "
    "V295 "
    "H90 "
    "V190 "
    "H390 "
    "V260 "
    "H630"
)


# ============================================================
# SVG FINAL
# ============================================================

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
            x="-30%"
            y="-30%"
            width="160%"
            height="160%"
        >

            <feGaussianBlur
                stdDeviation="2"
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
                stdDeviation="2.5"
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


    <!-- FUNDO -->

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
        fill="#ffffff"
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
        x="465"
        y="55"
        fill="#ffffff"
        font-family="'Courier New', monospace"
        font-size="20"
        font-weight="700"
    >
        HIGH SCORE
    </text>


    <text
        x="610"
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
        x="940"
        y="55"
        fill="#ffffff"
        font-family="'Courier New', monospace"
        font-size="24"
        font-weight="700"
    >
        LIVES
    </text>


    <!-- Vida 1 -->

    <path
        d="
            M1050 50
            L1034 39
            A18 18 0 1 0 1034 61
            Z
        "
        fill="#ffe329"
    />


    <!-- Vida 2 -->

    <path
        d="
            M1090 50
            L1074 39
            A18 18 0 1 0 1074 61
            Z
        "
        fill="#ffe329"
    />


    <!-- Vida 3 -->

    <path
        d="
            M1130 50
            L1114 39
            A18 18 0 1 0 1114 61
            Z
        "
        fill="#ffe329"
    />


    <!-- ================================================= -->
    <!-- LABIRINTO -->
    <!-- ================================================= -->

    <g filter="url(#blueGlow)">

        {''.join(walls)}

        {ghost_house}

    </g>


    <!-- ================================================= -->
    <!-- PELLETS -->
    <!-- ================================================= -->

    <g>

        {''.join(pellets)}

        {''.join(power_pellets)}

    </g>


    <!-- ================================================= -->
    <!-- FANTASMA VERMELHO -->
    <!-- ================================================= -->

    {ghost(
        "#ff3131",
        red_route,
        13.4,
        0
    )}


    <!-- ================================================= -->
    <!-- FANTASMA ROSA -->
    <!-- ================================================= -->

    {ghost(
        "#ff88dd",
        pink_route,
        15.2,
        -3
    )}


    <!-- ================================================= -->
    <!-- FANTASMA AZUL -->
    <!-- ================================================= -->

    {ghost(
        "#21d4fd",
        cyan_route,
        16.3,
        -6
    )}


    <!-- ================================================= -->
    <!-- FANTASMA LARANJA -->
    <!-- ================================================= -->

    {ghost(
        "#ff9d2e",
        orange_route,
        14.6,
        -8
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
                    M20 0
                    L-7 -16
                    A20 20 0 1 0 -7 16
                    Z
                "
            >

                <!-- BOCA ABRINDO E FECHANDO -->

                <animate
                    attributeName="d"
                    values="
                        M20 0 L-7 -16 A20 20 0 1 0 -7 16 Z;
                        M20 0 L-16 -5 A20 20 0 1 0 -16 5 Z;
                        M20 0 L-7 -16 A20 20 0 1 0 -7 16 Z
                    "
                    dur="0.22s"
                    repeatCount="indefinite"
                />

            </path>


            <!-- OLHO -->

            <circle
                cx="4"
                cy="-9"
                r="2.5"
                fill="#101010"
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
        font-size="19"
        font-weight="700"
    >

        READY!

        <animate
            attributeName="opacity"
            values="1;1;0;0"
            keyTimes="0;0.045;0.10;1"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
        />

    </text>

</svg>
"""


# ============================================================
# SALVAR O SVG
# ============================================================

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

print(
    "assets/pacman.svg generated successfully."
)
