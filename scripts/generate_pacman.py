"""Gera o labirinto e as rotas a partir da mesma grade, sem dependencias."""
from collections import defaultdict, deque
from math import hypot
from pathlib import Path
import os
import random

WIDTH, HEIGHT = 1200, 690
COLS, ROWS, CELL = 35, 19, 30
LEFT, TOP = (WIDTH - COLS * CELL) / 2, 78
WALL_STROKE = 3
PAC_RADIUS = 11
STEP_TIME = 0.16
BACKGROUND = "#05070c"
BLUE = "#0878ff"
YELLOW = "#ffe329"
NS = "http://www.w3.org/2000/svg"


def make_maze():
    grid = [["." for _ in range(COLS)] for _ in range(ROWS)]

    def wall(x1, y1, x2, y2, mirror=True):
        for row in range(y1, y2 + 1):
            for col in range(x1, x2 + 1):
                grid[row][col] = "#"
                if mirror:
                    grid[row][COLS - 1 - col] = "#"

    wall(0, 0, COLS - 1, 0)
    wall(0, ROWS - 1, COLS - 1, ROWS - 1)
    wall(0, 0, 0, ROWS - 1)

    # Blocos simetricos, com corredores de pelo menos uma celula.
    for x1, x2 in ((2, 5), (7, 10), (12, 15)):
        wall(x1, 2, x2, 3)
    wall(17, 0, 17, 3)

    wall(2, 5, 5, 5)
    wall(7, 5, 7, 7)
    wall(9, 5, 12, 5)
    wall(12, 5, 12, 6)
    wall(14, 5, 20, 5)
    wall(17, 5, 17, 6)

    wall(2, 7, 5, 9)
    wall(9, 8, 11, 9)
    wall(7, 9, 7, 10)

    wall(2, 11, 5, 12)
    wall(7, 12, 7, 14)
    wall(9, 12, 12, 12)
    wall(12, 12, 12, 13)

    wall(14, 13, 20, 13)
    wall(17, 13, 17, 15)
    wall(2, 14, 5, 14)
    wall(5, 14, 5, 16)
    wall(2, 16, 3, 16)
    wall(9, 15, 12, 15)
    wall(7, 16, 15, 16)
    wall(17, 17, 17, 18)

    # A casa tem uma unica porta. Apenas os fantasmas entram nela.
    wall(14, 8, 20, 8)
    wall(14, 11, 20, 11)
    wall(14, 8, 14, 11)
    grid[8][17] = "D"
    for row in (9, 10):
        for col in range(15, 20):
            grid[row][col] = "H"
    return grid


def make_graph(grid, ghost=False):
    allowed = ".DH" if ghost else "."
    graph = {}
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] not in allowed:
                continue
            cell = (row, col)
            graph[cell] = [
                (nr, nc)
                for nr, nc in ((row - 1, col), (row, col + 1),
                               (row + 1, col), (row, col - 1))
                if 0 <= nr < ROWS and 0 <= nc < COLS
                and grid[nr][nc] in allowed
            ]
    return graph


def shortest_path(graph, start, target):
    previous = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == target:
            path = []
            while cell is not None:
                path.append(cell)
                cell = previous[cell]
            return path[::-1]
        for other in graph[cell]:
            if other not in previous:
                previous[other] = cell
                queue.append(other)
    raise ValueError(f"Corredor desconectado: {start} -> {target}")


def pacman_route(graph, start, rng):
    # Passeio completo e fechado; a ordem muda conforme a semente.
    route, visited, stack = [start], {start}, [start]
    while stack:
        cell = stack[-1]
        options = [other for other in graph[cell] if other not in visited]
        if options:
            other = rng.choice(options)
            visited.add(other)
            stack.append(other)
            route.append(other)
        else:
            stack.pop()
            if stack:
                route.append(stack[-1])
    if visited != set(graph):
        raise ValueError("Existem corredores ou pontos inacessiveis.")
    return route


def ghost_route(graph, outside, start, rng):
    exit_cell = (7, 17)
    route = shortest_path(graph, start, exit_cell)
    previous = route[-2]
    for _ in range(130):
        cell = route[-1]
        options = [other for other in outside[cell] if other != previous]
        other = rng.choice(options or outside[cell])
        previous = cell
        route.append(other)
    # A volta tambem usa os corredores, sem salto ao reiniciar o SVG.
    route.extend(shortest_path(graph, route[-1], start)[1:])
    return route


def center(cell):
    row, col = cell
    return LEFT + (col + 0.5) * CELL, TOP + (row + 0.5) * CELL


def validate_routes(grid, routes):
    """Valida cada trecho e a folga fisica dos personagens junto as paredes."""
    walls = [
        (LEFT + col * CELL, TOP + row * CELL,
         LEFT + (col + 1) * CELL, TOP + (row + 1) * CELL)
        for row in range(ROWS) for col in range(COLS)
        if grid[row][col] == "#"
    ]
    minimum = float("inf")
    for name, route in routes.items():
        if route[0] != route[-1]:
            raise ValueError(f"{name}: o ciclo precisa terminar onde comecou.")
        for a, b in zip(route, route[1:]):
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
                raise ValueError(f"{name}: salto ou diagonal entre {a} e {b}.")
            if any(grid[r][c] == "#" for r, c in (a, b)):
                raise ValueError(f"{name}: rota dentro de uma parede.")
            if name == "pacman" and any(grid[r][c] != "." for r, c in (a, b)):
                raise ValueError("Pac-Man nao pode entrar na casa.")
            ax, ay = center(a)
            bx, by = center(b)
            for x1, y1, x2, y2 in walls:
                dx = max(x1 - max(ax, bx), min(ax, bx) - x2, 0)
                dy = max(y1 - max(ay, by), min(ay, by) - y2, 0)
                clearance = hypot(dx, dy)
                minimum = min(minimum, clearance)
                if clearance < PAC_RADIUS + WALL_STROKE / 2:
                    raise ValueError(f"{name}: personagem encostando na parede.")
    return minimum


def wall_contours(grid):
    # Contorna a uniao dos blocos: sem emendas azuis no meio das paredes.
    edges = set()
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] != "#":
                continue
            for nr, nc, a, b in (
                (row - 1, col, (col, row), (col + 1, row)),
                (row, col + 1, (col + 1, row), (col + 1, row + 1)),
                (row + 1, col, (col + 1, row + 1), (col, row + 1)),
                (row, col - 1, (col, row + 1), (col, row)),
            ):
                if not (0 <= nr < ROWS and 0 <= nc < COLS) or grid[nr][nc] != "#":
                    edges.add((a, b))
    outgoing = defaultdict(set)
    for a, b in edges:
        outgoing[a].add(b)
    contours = []
    while edges:
        first, current = min(edges)
        previous, points = first, [first]
        edges.remove((first, current))
        while current != first:
            points.append(current)
            dx, dy = current[0] - previous[0], current[1] - previous[1]
            directions = ((-dy, dx), (dx, dy), (dy, -dx), (-dx, -dy))
            candidates = [
                (current[0] + vx, current[1] + vy) for vx, vy in directions
                if (current, (current[0] + vx, current[1] + vy)) in edges
            ]
            if not candidates:
                raise ValueError("Contorno aberto no labirinto.")
            following = candidates[0]
            edges.remove((current, following))
            previous, current = current, following
        # Mantem apenas os cantos para desenhar curvas limpas.
        corners = []
        for i, point in enumerate(points):
            before, after = points[i - 1], points[(i + 1) % len(points)]
            if ((point[0] - before[0]) * (after[1] - point[1])
                    != (point[1] - before[1]) * (after[0] - point[0])):
                corners.append((LEFT + point[0] * CELL, TOP + point[1] * CELL))
        contours.append(corners)
    return contours


def rounded_path(points, radius=4):
    incoming, outgoing = [], []
    for i, (x, y) in enumerate(points):
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % len(points)]
        before, after = hypot(x - px, y - py), hypot(nx - x, ny - y)
        cut = min(radius, before / 2, after / 2)
        incoming.append((x - (x - px) / before * cut, y - (y - py) / before * cut))
        outgoing.append((x + (nx - x) / after * cut, y + (ny - y) / after * cut))
    pieces = [f"M{incoming[0][0]:g},{incoming[0][1]:g}"]
    for i, (x, y) in enumerate(points):
        if i:
            pieces.append(f"L{incoming[i][0]:g},{incoming[i][1]:g}")
        pieces.append(f"Q{x:g},{y:g} {outgoing[i][0]:g},{outgoing[i][1]:g}")
    return " ".join(pieces) + " Z"


def motion(route, duration, rotate=False):
    points = [center(cell) for cell in route]
    path = "M" + " L".join(f"{x:g},{y:g}" for x, y in points)
    rotation = ' rotate="auto"' if rotate else ""
    return (f'<animateMotion dur="{duration:g}s" repeatCount="indefinite" '
            f'calcMode="paced" path="{path}"{rotation}/>')


def ghost(name, color, route, duration):
    # Somente o Pac-Man gira. Os fantasmas ficam sempre em pe.
    return f"""
    <g id="{name}" data-character="ghost">
      {motion(route, duration)}
      <path fill="{color}" d="M-10.5,11 V-1 A10.5,10.5 0 0 1 10.5,-1
        V11 L7,8 L3.5,11 L0,8 L-3.5,11 L-7,8 Z"/>
      <ellipse cx="-4.4" cy="-1.5" rx="3.3" ry="4" fill="white"/>
      <ellipse cx="4.4" cy="-1.5" rx="3.3" ry="4" fill="white"/>
      <circle cx="-3.5" cy="-1.2" r="1.6" fill="#1847bd"/>
      <circle cx="5.3" cy="-1.2" r="1.6" fill="#1847bd"/>
    </g>"""


def build_scene(seed=2026):
    grid = make_maze()
    outside, inside = make_graph(grid), make_graph(grid, ghost=True)
    rng = random.Random(seed)
    routes = {"pacman": pacman_route(outside, (12, 17), rng)}
    for name, start in (
        ("blinky", (9, 15)), ("pinky", (9, 16)),
        ("inky", (9, 18)), ("clyde", (9, 19)),
    ):
        routes[name] = ghost_route(inside, outside, start, rng)
    clearance = validate_routes(grid, routes)
    return grid, routes, clearance


def generate(seed=2026):
    grid, routes, clearance = build_scene(seed)
    pac_route = routes["pacman"]
    duration = (len(pac_route) - 1) * STEP_TIME
    first_visit = {}
    for step, cell in enumerate(pac_route):
        first_visit.setdefault(cell, step)
    powers = {(1, 1), (1, 33), (17, 1), (17, 33)}
    pellets = []
    for cell, first in sorted(first_visit.items()):
        x, y = center(cell)
        power = cell in powers
        eaten = max(0.00001, first / (len(pac_route) - 1))
        blink = ('<animate attributeName="r" values="4.8;6;4.8" dur="0.7s" '
                 'repeatCount="indefinite"/>') if power else ""
        pellets.append(
            f'<circle cx="{x:g}" cy="{y:g}" r="{5.5 if power else 2.2}" fill="#ffe8a3">'
            f'<animate attributeName="opacity" values="1;0;1" '
            f'keyTimes="0;{eaten:.6f};0.999999" calcMode="discrete" '
            f'dur="{duration:g}s" repeatCount="indefinite"/>{blink}</circle>'
        )
    walls = "".join(
        f'<path d="{rounded_path(points)}"/>' for points in wall_contours(grid)
    )
    gate_x, gate_y = center((8, 17))
    ghosts = "".join(
        ghost(name, color, routes[name], (len(routes[name]) - 1) * speed)
        for name, color, speed in (
            ("blinky", "#ff3939", 0.19), ("pinky", "#ff93dc", 0.205),
            ("inky", "#32ddff", 0.215), ("clyde", "#ffa241", 0.225),
        )
    )
    lives = "".join(
        f'<path transform="translate({x} 42) scale(.65)" '
        'd="M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z"/>'
        for x in (1060, 1084, 1108)
    )
    svg = f"""<svg xmlns="{NS}" width="{WIDTH}" height="{HEIGHT}"
      viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
      <title id="title">Pac-Man</title>
      <desc id="description">Pac-Man e quatro fantasmas percorrem um labirinto
      simetrico. Todos os movimentos respeitam as paredes e os corredores.</desc>
      <rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="{BACKGROUND}"/>
      <g font-family="Courier New,monospace" font-weight="700" font-size="19">
        <text x="75" y="48" fill="white">SCORE <tspan fill="{YELLOW}">007950</tspan></text>
        <text x="470" y="48" fill="white">HIGH SCORE <tspan fill="{YELLOW}">012340</tspan></text>
        <text x="965" y="48" fill="white">LIVES</text>
      </g>
      <g fill="{YELLOW}">{lives}</g>
      <g id="maze" fill="none" stroke="{BLUE}" stroke-width="{WALL_STROKE}"
         stroke-linecap="round" stroke-linejoin="round">{walls}</g>
      <line id="ghost-door" x1="{gate_x - 12:g}" x2="{gate_x + 12:g}"
         y1="{gate_y:g}" y2="{gate_y:g}" stroke="#ff91dd" stroke-width="3"/>
      <g id="pellets">{"".join(pellets)}</g>
      {ghosts}
      <g id="pacman" data-character="pacman">
        {motion(pac_route, duration, rotate=True)}
        <path fill="{YELLOW}" d="M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z">
          <animate attributeName="d"
            values="M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z;
                    M0,0 L10.95,-1 A11,11 0 1 0 10.95,1 Z;
                    M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z"
            dur="0.2s" repeatCount="indefinite"/>
        </path>
        <circle cx="2.5" cy="-5.5" r="1.3" fill="{BACKGROUND}"/>
      </g>
    </svg>
"""
    return svg, grid, routes, clearance


if __name__ == "__main__":
    svg, grid, routes, clearance = generate(int(os.environ.get("PACMAN_SEED", "2026")))
    output = Path("assets/pacman.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Pac-Man gerado: {len(routes['pacman']) - 1} movimentos; "
          f"folga minima do centro ate a parede: {clearance:g}px.")
