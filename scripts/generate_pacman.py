from pathlib import Path

WIDTH = 1200
HEIGHT = 460

PACMAN_DURATION = 18

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def wall(x, y, w, h, r=8):
    return f'''
    <rect
        x="{x}"
        y="{y}"
        width="{w}"
        height="{h}"
        rx="{r}"
        fill="#05070c"
        stroke="#086fff"
        stroke-width="7"
    />
    '''


def pellet(x, y, delay=0):
    return f'''
    <circle cx="{x}" cy="{y}" r="4" fill="#ffe5a0">
        <animate
            attributeName="opacity"
            values="1;1;0;0;1"
            keyTimes="0;{delay:.3f};{min(delay + 0.02, 0.94):.3f};0.97;1"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
        />
    </circle>
    '''


def static_pellet(x, y):
    return f'''
    <circle cx="{x}" cy="{y}" r="4" fill="#ffe5a0"/>
    '''


def power_pellet(x, y):
    return f'''
    <circle cx="{x}" cy="{y}" r="9" fill="#fff1c4">
        <animate
            attributeName="r"
            values="8;11;8"
            dur="0.65s"
            repeatCount="indefinite"
        />
    </circle>
    '''


def ghost(color, route, duration, begin):
    return f'''
    <g>
        <animateMotion
            path="{route}"
            dur="{duration}s"
            begin="{begin}s"
            repeatCount="indefinite"
            rotate="auto"
        />

        <g transform="translate(-17,-17)">
            <path
                d="
                    M2 33
                    V17
                    C2 8 8 2 17 2
                    C26 2 32 8 32 17
                    V33
                    L27 28
                    L22 33
                    L17 28
                    L12 33
                    L7 28
                    Z
                "
                fill="{color}"
            />

            <ellipse cx="11" cy="15" rx="5" ry="6" fill="white"/>
            <ellipse cx="23" cy="15" rx="5" ry="6" fill="white"/>

            <circle cx="13" cy="16" r="2.5" fill="#12275c"/>
            <circle cx="25" cy="16" r="2.5" fill="#12275c"/>
        </g>
    </g>
    '''


# ============================================================
# LABIRINTO
# ============================================================

walls = [

    # Borda
    wall(55, 90, 1090, 320, 12),

    # Linha superior
    wall(100, 115, 175, 47),
    wall(350, 115, 175, 47),
    wall(600, 115, 175, 47),
    wall(850, 115, 175, 47),

    # Meio esquerdo
    wall(100, 205, 175, 48),
    wall(325, 185, 48, 115),

    # Meio direito
    wall(925, 205, 120, 48),
    wall(825, 185, 48, 115),

    # Centro inferior
    wall(100, 315, 175, 48),
    wall(340, 315, 145, 48),
    wall(715, 315, 145, 48),
    wall(925, 315, 120, 48),
]


# ============================================================
# CASA DOS FANTASMAS
# ============================================================

ghost_house = '''
<path
    d="
        M505 300
        V225

        Q505 208 522 208

        H560

        M640 208

        H678

        Q695 208 695 225

        V300
        Z
    "
    fill="#05070c"
    stroke="#086fff"
    stroke-width="7"
    stroke-linecap="round"
    stroke-linejoin="round"
/>

<line
    x1="560"
    y1="208"
    x2="640"
    y2="208"
    stroke="#ff70d5"
    stroke-width="6"
/>
'''


# ============================================================
# PONTOS PRINCIPAIS
# ============================================================

route_pellets = [

    (95, 180),
    (125, 180),
    (155, 180),
    (185, 180),
    (215, 180),
    (245, 180),
    (275, 180),
    (305, 180),

    (405, 180),
    (435, 180),
    (465, 180),

    (495, 180),
    (525, 180),

    (675, 180),
    (705, 180),
    (735, 180),
    (765, 180),

    (895, 180),
    (925, 180),
    (955, 180),
    (985, 180),
    (1015, 180),
    (1045, 180),
    (1075, 180),

    (305, 270),
    (335, 270),

    (865, 270),
    (895, 270),

    (300, 385),
    (335, 385),
    (370, 385),
    (405, 385),
    (440, 385),
    (475, 385),

    (510, 385),
    (545, 385),
    (580, 385),
    (615, 385),
    (650, 385),
    (685, 385),

    (720, 385),
    (755, 385),
    (790, 385),
    (825, 385),
    (860, 385),
    (895, 385),
]


pellets = []

for index, (x, y) in enumerate(route_pellets):

    delay = 0.07 + (index * 0.017)

    pellets.append(
        pellet(
            x,
            y,
            min(delay, 0.89)
        )
    )


# ============================================================
# PONTOS ESTÁTICOS
# ============================================================

static_pellets = [

    (92, 120),
    (92, 150),
    (92, 210),
    (92, 240),
    (92, 270),
    (92, 300),
    (92, 340),
    (92, 375),

    (1108, 120),
    (1108, 150),
    (1108, 210),
    (1108, 240),
    (1108, 270),
    (1108, 300),
    (1108, 340),
    (1108, 375),

    (300, 120),
    (325, 120),

    (550, 120),
    (575, 120),

    (800, 120),
    (825, 120),

    (1050, 120),
    (1080, 120),

    (300, 345),
    (320, 345),

    (500, 345),
    (530, 345),

    (670, 345),
    (700, 345),

    (880, 345),
    (900, 345),

]


for x, y in static_pellets:

    pellets.append(
        static_pellet(
            x,
            y
        )
    )


# ============================================================
# POWER PELLETS
# ============================================================

powers = [

    power_pellet(92, 105),
    power_pellet(1108, 105),

    power_pellet(92, 395),
    power_pellet(1108, 395),

]


# ============================================================
# ROTA DO PAC-MAN
# ============================================================

pac_route = (
    "M95 180 "
    "H320 "
    "V270 "
    "H400 "
    "V385 "
    "H895 "
    "V270 "
    "H1105 "
    "V180 "
    "H880 "
    "V385 "
    "H305 "
    "V270 "
    "H95 "
    "V180"
)


# ============================================================
# ROTAS DOS FANTASMAS
# ============================================================

red_route = (
    "M600 245 "
    "H800 "
    "V180 "
    "H1105 "
    "V270 "
    "H895 "
    "V385 "
    "H600 "
    "V300 "
    "H400 "
    "V180 "
    "H95 "
    "V270 "
    "H320 "
    "V245 "
    "H600"
)


pink_route = (
    "M600 245 "
    "H400 "
    "V180 "
    "H95 "
    "V270 "
    "H320 "
    "V385 "
    "H600 "
    "V300 "
    "H895 "
    "V180 "
    "H1105 "
    "V270 "
    "H895 "
    "V245 "
    "H600"
)


cyan_route = (
    "M575 245 "
    "H400 "
    "V270 "
    "H95 "
    "V180 "
    "H320 "
    "V245 "
    "H575 "
    "V385 "
    "H895 "
    "V270 "
    "H1105 "
    "V180 "
    "H880 "
    "V245 "
    "H575"
)


orange_route = (
    "M625 245 "
    "H895 "
    "V270 "
    "H1105 "
    "V180 "
    "H880 "
    "V245 "
    "H625 "
    "V385 "
    "H305 "
    "V270 "
    "H95 "
    "V180 "
    "H320 "
    "V245 "
    "H625"
)


# ============================================================
# SVG
# ============================================================

svg = f'''
<svg
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    xmlns="http://www.w3.org/2000/svg"
>

    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        rx="18"
        fill="#05070c"
    />


    <!-- SCORE -->

    <text
        x="65"
        y="50"
        fill="#ffffff"
        font-family="monospace"
        font-size="20"
        font-weight="bold"
    >
        SCORE
    </text>

    <text
        x="155"
        y="50"
        fill="#ffe500"
        font-family="monospace"
        font-size="20"
        font-weight="bold"
    >
        007950
    </text>


    <!-- HIGH SCORE -->

    <text
        x="460"
        y="50"
        fill="#ffffff"
        font-family="monospace"
        font-size="18"
        font-weight="bold"
    >
        HIGH SCORE
    </text>

    <text
        x="600"
        y="50"
        fill="#ffe500"
        font-family="monospace"
        font-size="18"
        font-weight="bold"
    >
        012340
    </text>


    <!-- LIVES -->

    <text
        x="950"
        y="50"
        fill="#ffffff"
        font-family="monospace"
        font-size="20"
        font-weight="bold"
    >
        LIVES
    </text>

    <g fill="#ffe329">

        <path d="
            M1050 45
            L1036 36
            A16 16 0 1 0 1036 54
            Z
        "/>

        <path d="
            M1090 45
            L1076 36
            A16 16 0 1 0 1076 54
            Z
        "/>

        <path d="
            M1130 45
            L1116 36
            A16 16 0 1 0 1116 54
            Z
        "/>

    </g>


    <!-- LABIRINTO -->

    <g>

        {''.join(walls)}

        {ghost_house}

    </g>


    <!-- PONTOS -->

    <g>

        {''.join(pellets)}

        {''.join(powers)}

    </g>


    <!-- READY -->

    <text
        x="555"
        y="195"
        fill="#ffe500"
        font-family="monospace"
        font-size="18"
        font-weight="bold"
    >
        READY!

        <animate
            attributeName="opacity"
            values="1;1;0;0"
            keyTimes="0;0.06;0.10;1"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
        />

    </text>


    <!-- FANTASMAS -->

    {ghost("#ff3131", red_route, 14.5, 0)}

    {ghost("#ff86df", pink_route, 15.8, -2.5)}

    {ghost("#24d8ff", cyan_route, 16.8, -5.1)}

    {ghost("#ff9e2f", orange_route, 15.2, -7.8)}


    <!-- PAC-MAN -->

    <g>

        <animateMotion
            path="{pac_route}"
            dur="{PACMAN_DURATION}s"
            repeatCount="indefinite"
            rotate="auto"
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

                <animate
                    attributeName="d"
                    values="
                        M18 0 L-6 -15 A18 18 0 1 0 -6 15 Z;
                        M18 0 L-14 -4 A18 18 0 1 0 -14 4 Z;
                        M18 0 L-6 -15 A18 18 0 1 0 -6 15 Z
                    "
                    dur="0.23s"
                    repeatCount="indefinite"
                />

            </path>

            <circle
                cx="3"
                cy="-8"
                r="2.2"
                fill="#111827"
            />

        </g>

    </g>


</svg>
'''


# ============================================================
# SALVAR
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
