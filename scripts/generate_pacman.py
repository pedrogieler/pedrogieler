"""Gera o labirinto e uma partida autonoma, sem dependencias externas."""
from math import hypot
from pathlib import Path
import os

WIDTH, HEIGHT = 1200, 690
COLS, ROWS, CELL = 35, 19, 30
LEFT, TOP = (WIDTH - COLS * CELL) / 2, 78
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


def center(cell):
    row, col = cell
    return LEFT + (col + 0.5) * CELL, TOP + (row + 0.5) * CELL


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


def generate(seed=2026):
    if __package__:
        from .pacman_game import Game, render_game, validate_game
    else:
        from pacman_game import Game, render_game, validate_game
    grid = make_maze()
    game = Game(grid, make_graph(grid), make_graph(grid, ghost=True), center, seed).simulate()
    clearance = validate_game(game, LEFT, TOP, CELL)
    walls = "".join(
        f'<path d="{rounded_path(points)}"/>' for points in wall_contours(grid)
    )
    svg = render_game(game, walls, WIDTH, HEIGHT, NS)
    return svg, game, clearance


if __name__ == "__main__":
    svg, game, clearance = generate(int(os.environ.get("PACMAN_SEED", "2026")))
    output = Path("assets/pacman.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Partida autonoma gerada: {game.duration:.1f}s; "
          f"{len(game.captures)} fantasmas comidos; "
          f"distancia minima do centro a parede: {clearance:g}px.")
