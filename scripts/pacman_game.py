"""Partida autonoma pre-calculada para uma animacao SVG sem JavaScript."""
from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from math import ceil, cos, hypot, pi, sin, sqrt
import random

NAMES = ("blinky", "pinky", "inky", "clyde")
COLORS = ("#ff3939", "#ff93dc", "#32ddff", "#ffa241")
HOMES = ((9, 15), (9, 16), (9, 18), (9, 19))
CORNERS = ((1, 33), (1, 1), (17, 33), (17, 1))
POWERS = frozenset(((1, 1), (1, 33), (17, 1), (17, 33)))
SPAWN, EXIT = (12, 17), (7, 17)
EPSILON = 1e-8


class Signal:
    def __init__(self, initial):
        self.points = [(0.0, initial)]

    def set(self, time, value):
        if value == self.points[-1][1]:
            return
        if abs(time - self.points[-1][0]) < EPSILON:
            self.points[-1] = (time, value)
        else:
            self.points.append((time, value))

    def at(self, time):
        for moment, value in reversed(self.points):
            if moment <= time + EPSILON:
                return value
        return self.points[0][1]


class Motion:
    def __init__(self, initial):
        self.points = [(0.0, initial, True)]
        self.warps = []

    def add(self, time, value, force=False):
        time = round(time, 8)
        if abs(time - self.points[-1][0]) < EPSILON:
            self.points[-1] = (time, value, self.points[-1][2] or force)
            return
        if len(self.points) >= 2 and not self.points[-1][2] and not force:
            ta, a, _ = self.points[-2]
            tb, b, _ = self.points[-1]
            if tb > ta and time > tb:
                fraction = (tb - ta) / (time - ta)
                expected = tuple(a[i] + (value[i] - a[i]) * fraction for i in (0, 1))
                if hypot(expected[0] - b[0], expected[1] - b[1]) < 0.00001:
                    self.points.pop()
        self.points.append((time, value, force))

    def jump(self, time, value):
        old = self.points[-1][1]
        if hypot(old[0] - value[0], old[1] - value[1]) < EPSILON:
            self.add(time, value)
            return
        # Apenas os reinicios, com os personagens ocultos, podem reposicionar.
        while len(self.points) > 1 and self.points[-1][0] >= time - .001:
            self.points.pop()
        self.add(time - .001, old, force=True)
        self.add(time, value, force=True)
        self.warps.append((time - .001, time))


@dataclass
class Actor:
    name: str
    cell: tuple
    destination: tuple | None = None
    progress: float = 0.0
    previous: tuple | None = None
    direction: tuple = (0, -1)
    mode: str = "chase"
    release: float = 0.0

    def position(self, center):
        x, y = center(self.cell)
        if self.destination is not None:
            nx, ny = center(self.destination)
            return x + (nx - x) * self.progress, y + (ny - y) * self.progress
        return x, y

    def reverse(self):
        if self.destination is not None:
            self.cell, self.destination = self.destination, self.cell
            self.progress = 1 - self.progress
        self.previous = None
        self.direction = (-self.direction[0], -self.direction[1])


class Game:
    def __init__(self, grid, outside, inside, center, seed=2026):
        self.grid, self.outside, self.inside, self.center = grid, outside, inside, center
        self.rng = random.Random(seed)
        self.distances = self.all_distances(inside)
        self.time, self.score, self.high, self.level, self.lives = 0.0, 0, 12340, 1, 3
        self.status, self.status_at, self.pause_until = "ready", 0.0, 1.1
        self.power_until, self.combo, self.play_time = 0.0, 0, 0.0
        self.remaining = set(outside)
        self.events, self.captures = [], []
        self.visits = {}
        self.pac = Actor("pacman", SPAWN)
        self.ghosts = [
            Actor(name, home, mode="house", release=1.1 + .6 + i * .8)
            for i, (name, home) in enumerate(zip(NAMES, HOMES))
        ]
        self.actors = [self.pac, *self.ghosts]
        self.motion = {a.name: Motion(a.position(center)) for a in self.actors}
        self.facing = {a.name: Signal(a.direction) for a in self.actors}
        self.visibility = {a.name: Signal(1) for a in self.actors}
        self.ghost_mode = {g.name: Signal("house") for g in self.ghosts}
        self.ghost_fill = {g.name: Signal(color) for g, color in zip(self.ghosts, COLORS)}
        self.signals = {
            "score": Signal(0), "high": Signal(12340), "level": Signal(1),
            "lives": Signal(3), "message": Signal("READY!"),
            "power": Signal(0), "maze": Signal("#0878ff"),
            "pac_normal": Signal(1), "pac_death": Signal(0),
            "death_angle": Signal(35),
        }
        self.dots = {cell: Signal(1) for cell in outside}
        self.history = []
        self.snapshot()

    @staticmethod
    def all_distances(graph):
        result = {}
        for start in graph:
            distance, queue = {start: 0}, deque([start])
            while queue:
                cell = queue.popleft()
                for other in graph[cell]:
                    if other not in distance:
                        distance[other] = distance[cell] + 1
                        queue.append(other)
            result[start] = distance
        return result

    def distance(self, a, b):
        return self.distances[a][b]

    def nearest_floor(self, target):
        return min(self.outside, key=lambda p: (abs(p[0] - target[0]) + abs(p[1] - target[1]), p))

    def speed(self, actor):
        if actor is self.pac:
            return 6.25 + min(self.level - 1, 4) * .10
        if actor.mode == "eyes":
            return 12.5
        if actor.mode == "frightened":
            return 3.2
        if actor.mode in ("house", "leaving"):
            return 4.4
        return (5.1, 4.95, 4.85, 4.75)[NAMES.index(actor.name)] + min(self.level - 1, 5) * .08

    def pac_choice(self):
        start = self.pac.cell
        dangerous = [g for g in self.ghosts if g.mode in ("chase", "leaving")
                     and g.cell in self.outside]
        frightened = [g for g in self.ghosts if g.mode == "frightened"]
        danger_distance = lambda cell: min(
            (min(self.distance(cell, g.cell),
                 self.distance(cell, g.destination) if g.destination in self.outside else 999)
             for g in dangerous), default=999)
        hunting = None
        if frightened:
            target = min(frightened, key=lambda g: self.distance(start, g.cell))
            distance = self.distance(start, target.cell)
            if distance <= 8 and self.power_until - self.time > distance / 5.0 + .5:
                hunting = target.cell

        # Dijkstra considera a comida e o perigo nos corredores, sem enxergar atraves de paredes.
        costs, previous, heap = {start: 0.0}, {start: None}, [(0.0, start)]
        target = None
        while heap:
            cost, cell = heappop(heap)
            if cost > costs[cell] + EPSILON:
                continue
            if cell != start and ((hunting is not None and cell == hunting)
                                  or (hunting is None and cell in self.remaining)):
                target = cell
                break
            for other in self.outside[cell]:
                danger = danger_distance(other)
                penalty = max(0, 6 - danger) ** 2 * 2.2
                recent = self.time - self.visits.get(other, -100)
                memory = max(0, .6 - recent) * 2
                step = 1 + penalty + memory
                # Uma pastilha perto do perigo e mais atraente do que um ponto comum.
                if other in POWERS and other in self.remaining and dangerous:
                    step = max(.15, step * .12)
                value = cost + step
                if value + EPSILON < costs.get(other, float("inf")):
                    costs[other], previous[other] = value, cell
                    heappush(heap, (value, other))
        if target is None:
            options = self.outside[start]
            return max(options, key=lambda cell: (danger_distance(cell), self.rng.random()))
        while previous[target] != start:
            target = previous[target]
        return target

    def ghost_choice(self, ghost):
        home = HOMES[NAMES.index(ghost.name)]
        if ghost.mode == "house":
            if self.time + EPSILON < ghost.release:
                return None
            ghost.mode = "leaving"
        if ghost.mode in ("eyes", "leaving"):
            target = home if ghost.mode == "eyes" else EXIT
            if ghost.cell == target:
                if ghost.mode == "eyes":
                    ghost.mode, ghost.release = "house", self.time + 1.0
                    self.events.append((self.time, "regenerated", ghost.name))
                    return None
                ghost.mode = "chase"
            else:
                return min(self.inside[ghost.cell], key=lambda cell: self.distance(cell, target))

        options = [cell for cell in self.outside[ghost.cell] if cell != ghost.previous]
        options = options or self.outside[ghost.cell]
        if ghost.mode == "frightened":
            return self.rng.choice(options)

        index = NAMES.index(ghost.name)
        if self.play_time % 27 < 4.5:
            target = CORNERS[index]
        else:
            pr, pc = self.pac.cell
            dr, dc = self.pac.direction
            if index == 0:
                target = self.pac.cell
            elif index == 1:
                target = self.nearest_floor((pr + dr * 4, pc + dc * 4))
            elif index == 2:
                br, bc = self.ghosts[0].cell
                target = self.nearest_floor((2 * (pr + dr * 2) - br,
                                             2 * (pc + dc * 2) - bc))
            else:
                target = self.pac.cell if self.distance(ghost.cell, self.pac.cell) > 8 else CORNERS[index]
        return min(options, key=lambda cell: (self.distance(cell, target),
                    ((-1, 0), (0, -1), (1, 0), (0, 1)).index(
                        (cell[0] - ghost.cell[0], cell[1] - ghost.cell[1]))))

    def set_destination(self, actor):
        if actor.destination is not None:
            return
        target = self.pac_choice() if actor is self.pac else self.ghost_choice(actor)
        if target is not None:
            graph = self.outside if actor is self.pac or actor.mode in ("chase", "frightened") else self.inside
            if target not in graph[actor.cell]:
                raise ValueError(f"Movimento fora do corredor: {actor.name}: {actor.cell} -> {target}")
            actor.destination = target
            actor.direction = (target[0] - actor.cell[0], target[1] - actor.cell[1])
            self.facing[actor.name].set(self.time, actor.direction)

    def eat(self, cell):
        self.visits[cell] = self.time
        if cell not in self.remaining:
            return
        self.remaining.remove(cell)
        self.dots[cell].set(self.time, 0)
        self.score += 50 if cell in POWERS else 10
        if cell in POWERS:
            self.power_until = self.time + max(4.5, 8.0 - (self.level - 1) * .5)
            self.combo = 0
            self.events.append((self.time, "power", cell))
            for ghost in self.ghosts:
                if ghost.mode in ("chase", "frightened"):
                    ghost.mode = "frightened"
                    ghost.reverse()
                    self.facing[ghost.name].set(self.time, ghost.direction)
        self.high = max(self.high, self.score)
        if not self.remaining:
            self.status, self.status_at, self.pause_until = "clear", self.time, self.time + 1.6
            self.events.append((self.time, "level_clear", self.level))

    def eat_ghost(self, ghost):
        points = 200 * 2 ** min(self.combo, 3)
        self.combo += 1
        self.score += points
        self.high = max(self.high, self.score)
        self.captures.append((self.time, points, ghost.position(self.center)))
        self.events.append((self.time, "ghost_eaten", ghost.name))
        ghost.mode = "eyes"
        if ghost.destination is not None:
            home = HOMES[NAMES.index(ghost.name)]
            forward = 1 - ghost.progress + self.distance(ghost.destination, home)
            backward = ghost.progress + self.distance(ghost.cell, home)
            if backward < forward:
                ghost.reverse()
                self.facing[ghost.name].set(self.time, ghost.direction)

    def die(self):
        self.lives -= 1
        self.power_until = self.time
        self.status, self.status_at, self.pause_until = "dying", self.time, self.time + 1.0
        self.events.append((self.time, "death", self.lives))

    def reset_actors(self):
        self.pac = Actor("pacman", SPAWN)
        self.ghosts = [
            Actor(name, home, mode="house", release=self.time + 1.6 + i * .8)
            for i, (name, home) in enumerate(zip(NAMES, HOMES))
        ]
        self.actors = [self.pac, *self.ghosts]
        for actor in self.actors:
            self.motion[actor.name].jump(self.time, actor.position(self.center))
            self.facing[actor.name].set(self.time, actor.direction)
        self.power_until, self.combo = self.time, 0
        self.status, self.status_at, self.pause_until = "ready", self.time, self.time + 1.1

    def transition(self):
        if self.time + EPSILON < self.pause_until:
            return
        if self.status == "ready":
            self.status, self.status_at = "playing", self.time
            self.eat(self.pac.cell)
        elif self.status == "dying":
            if self.lives:
                self.reset_actors()
            else:
                self.status, self.status_at, self.pause_until = "gameover", self.time, self.time + 2.4
                self.events.append((self.time, "game_over", self.score))
        elif self.status == "clear":
            self.level += 1
            self.remaining, self.visits = set(self.outside), {}
            for dot in self.dots.values():
                dot.set(self.time, 1)
            self.events.append((self.time, "level_started", self.level))
            self.reset_actors()
        elif self.status == "gameover":
            self.score, self.lives, self.level = 0, 3, 1
            self.play_time, self.visits = 0.0, {}
            self.remaining = set(self.outside)
            for dot in self.dots.values():
                dot.set(self.time, 1)
            self.events.append((self.time, "new_game", None))
            self.reset_actors()

    def snapshot(self):
        time = self.time
        elapsed = time - self.status_at
        normal = self.status in ("playing", "ready") or (self.status == "clear" and elapsed < .5)
        death = self.status == "dying" and elapsed < .85
        for actor in self.actors:
            self.motion[actor.name].add(time, actor.position(self.center))
            visible = normal if actor is self.pac else (
                self.status in ("playing", "ready") or (self.status == "dying" and elapsed < .12))
            self.visibility[actor.name].set(time, int(visible or (actor is self.pac and death)))
        for ghost, color in zip(self.ghosts, COLORS):
            self.ghost_mode[ghost.name].set(time, ghost.mode)
            frightened = ghost.mode == "frightened"
            flashing = frightened and self.power_until - time < 2 and int(time * 8) % 2 == 0
            self.ghost_fill[ghost.name].set(time, "#ffffff" if flashing else "#163cdb" if frightened else color)
        message = {"ready": "READY!", "clear": "STAGE CLEAR", "gameover": "GAME OVER"}.get(self.status, "")
        power = ceil(max(0, self.power_until - time)) if self.status == "playing" else 0
        maze = "#ffffff" if self.status == "clear" and int(elapsed * 8) % 2 == 0 else "#0878ff"
        for name, value in (
            ("score", self.score), ("high", self.high), ("level", self.level),
            ("lives", self.lives), ("message", message), ("power", power),
            ("maze", maze), ("pac_normal", int(normal)), ("pac_death", int(death)),
            ("death_angle", round(min(179.9, 35 + elapsed / .85 * 145), 1) if death else 35),
        ):
            self.signals[name].set(time, value)
        self.history.append((time, self.status, self.level, self.lives, len(self.remaining)))

    @staticmethod
    def collision_time(a0, a1, b0, b1, radius=18.0):
        rx, ry = a0[0] - b0[0], a0[1] - b0[1]
        dx, dy = a1[0] - a0[0] - b1[0] + b0[0], a1[1] - a0[1] - b1[1] + b0[1]
        c = rx * rx + ry * ry - radius * radius
        if c <= .000001:
            return 0.0
        a, b = dx * dx + dy * dy, 2 * (rx * dx + ry * dy)
        discriminant = b * b - 4 * a * c
        if a < EPSILON or discriminant < 0:
            return None
        first = (-b - sqrt(discriminant)) / (2 * a)
        return max(0.0, first) if -EPSILON <= first <= 1 + EPSILON else None

    def advance(self):
        if self.status != "playing":
            self.time = min(self.time + .04, self.pause_until)
            self.snapshot()
            self.transition()
            self.snapshot()
            return
        if self.time >= self.power_until - EPSILON:
            for ghost in self.ghosts:
                if ghost.mode == "frightened":
                    ghost.mode = "chase"
        for actor in self.actors:
            self.set_destination(actor)
        self.snapshot()
        dt = .04
        for actor in self.actors:
            if actor.destination is not None:
                dt = min(dt, (1 - actor.progress) / self.speed(actor))
        if self.power_until > self.time + EPSILON:
            dt = min(dt, self.power_until - self.time)
        old = {a.name: a.position(self.center) for a in self.actors}
        predicted = {}
        for actor in self.actors:
            x, y = old[actor.name]
            dr, dc = actor.direction
            distance = self.speed(actor) * dt * 30 if actor.destination is not None else 0
            predicted[actor.name] = (x + dc * distance, y + dr * distance)
        impacts = []
        for ghost in self.ghosts:
            if ghost.mode in ("chase", "frightened"):
                fraction = self.collision_time(old["pacman"], predicted["pacman"],
                                               old[ghost.name], predicted[ghost.name])
                if fraction is not None:
                    impacts.append(fraction)
        if impacts:
            dt *= min(impacts)
        self.time += dt
        self.play_time += dt
        arrived = []
        for actor in self.actors:
            if actor.destination is not None:
                actor.progress += self.speed(actor) * dt
                if actor.progress >= 1 - EPSILON:
                    actor.previous, actor.cell = actor.cell, actor.destination
                    actor.destination, actor.progress = None, 0.0
                    arrived.append(actor)
        if self.pac in arrived:
            self.eat(self.pac.cell)
        for ghost in self.ghosts:
            if ghost in arrived and ghost.mode in ("eyes", "leaving"):
                home = HOMES[NAMES.index(ghost.name)]
                if ghost.mode == "eyes" and ghost.cell == home:
                    ghost.mode, ghost.release = "house", self.time + 1
                    self.events.append((self.time, "regenerated", ghost.name))
                elif ghost.mode == "leaving" and ghost.cell == EXIT:
                    ghost.mode = "chase"
        if self.status == "playing":
            for ghost in self.ghosts:
                if ghost.mode not in ("chase", "frightened"):
                    continue
                a, b = self.pac.position(self.center), ghost.position(self.center)
                if hypot(a[0] - b[0], a[1] - b[1]) <= 18.000001:
                    if ghost.mode == "frightened":
                        self.eat_ghost(ghost)
                    else:
                        self.die()
                        break
        self.snapshot()

    def simulate(self, minimum=150, maximum=300):
        iterations = 0
        while self.time < maximum:
            self.advance()
            iterations += 1
            if iterations > 150000:
                raise ValueError("A simulacao ficou sem avancar o relogio.")
            if self.time >= minimum and self.status in ("clear", "gameover") and self.time - self.status_at >= 1.0:
                break
        # O ciclo termina com uma pausa, sem arrastar sprites atraves do mapa.
        end = self.time + .35
        for signal in self.visibility.values():
            signal.set(self.time, 0)
        self.signals["pac_normal"].set(self.time, 0)
        self.signals["pac_death"].set(self.time, 0)
        for actor, initial in zip(self.actors, (SPAWN, *HOMES)):
            self.motion[actor.name].add(end - .01, actor.position(self.center))
            self.motion[actor.name].jump(end, self.center(initial))
        self.duration = end + .05
        for motion in self.motion.values():
            motion.add(self.duration, motion.points[-1][1])
        self.signals["high"].points = [(0.0, self.high)]
        return self


def pac_path(angle):
    radians = angle * pi / 180
    x, y = 11 * cos(radians), 11 * sin(radians)
    large = int(angle < 90)
    return f"M0,0 L{x:.4f},{-y:.4f} A11,11 0 {large} 0 {x:.4f},{y:.4f} Z"


def animation(points, attribute, duration, formatter=str, linear=False, transform=None):
    # Todos os elementos usam o mesmo relogio, inclusive pontos, cores e placar.
    clean = []
    for time, value in points:
        formatted = formatter(value)
        key = f"{min(1, max(0, time / duration)):.9f}"
        if clean and key == clean[-1][0]:
            clean[-1] = (key, formatted)
        elif not clean or linear or formatted != clean[-1][1]:
            clean.append((key, formatted))
    if len(clean) == 1:
        return ""
    if float(clean[-1][0]) < 1:
        clean.append(("1", clean[-1][1]))
    tag = "animateTransform" if transform else "animate"
    extra = f' type="{transform}"' if transform else ""
    values = ";".join(value for _, value in clean)
    times = ";".join(time for time, _ in clean)
    return (f'<{tag} attributeName="{attribute}"{extra} '
            f'values="{values}" keyTimes="{times}" dur="{duration:.8f}s" '
            f'calcMode="{"linear" if linear else "discrete"}" repeatCount="indefinite"/>')


def signal_animation(game, signal, attribute, formatter=str):
    return animation(signal.points, attribute, game.duration, formatter)


def opacity_group(game, signal, condition, body, extra=""):
    initial = int(condition(signal.points[0][1]))
    change = signal_animation(game, signal, "opacity", lambda value: str(int(condition(value))))
    return f'<g opacity="{initial}" {extra}>{change}{body}</g>'


def number_display(game, signal, x, y, digits=6, size=19, color="#ffe329"):
    parts = []
    for column in range(digits):
        for digit in range(10):
            selected = lambda value, col=column, d=digit: int(f"{int(value):0{digits}d}"[-digits:][col]) == d
            initial = int(selected(signal.points[0][1]))
            changes = signal_animation(game, signal, "opacity", lambda value: str(int(selected(value))))
            if initial or changes:
                parts.append(f'<text x="{x + column * size * .6:g}" y="{y:g}" '
                             f'font-size="{size}" fill="{color}" opacity="{initial}">{digit}{changes}</text>')
    return "".join(parts)


def render_game(game, walls, width=1200, height=690, namespace="http://www.w3.org/2000/svg"):
    duration = game.duration
    position = lambda value: f"{value[0]:.5f} {value[1]:.5f}"
    wall_animation = signal_animation(game, game.signals["maze"], "stroke")
    dots = []
    for cell, signal in sorted(game.dots.items()):
        x, y = game.center(cell)
        power = cell in POWERS
        pulse = ('<animate attributeName="r" values="4.8;6;4.8" '
                 'dur="0.7s" repeatCount="indefinite"/>') if power else ""
        dots.append(
            f'<circle cx="{x:g}" cy="{y:g}" r="{5.5 if power else 2.2}" '
            f'fill="#ffe8a3" opacity="1">{signal_animation(game, signal, "opacity")}{pulse}</circle>'
        )
    ghosts = []
    for name, color in zip(NAMES, COLORS):
        mode, facing, fill = game.ghost_mode[name], game.facing[name], game.ghost_fill[name]
        translate = animation([(t, value) for t, value, _ in game.motion[name].points],
                              "transform", duration, position, linear=True, transform="translate")
        initial = game.motion[name].points[0][1]
        body_opacity = signal_animation(game, mode, "opacity", lambda value: str(int(value != "eyes")))
        body_fill = signal_animation(game, fill, "fill")
        pupils = []
        for offset in (-4.4, 4.4):
            cx = signal_animation(game, facing, "cx", lambda value, base=offset: f"{base + value[1] * 1.3:g}")
            cy = signal_animation(game, facing, "cy", lambda value: f"{-1.5 + value[0] * 1.6:g}")
            pupils.append(f'<circle cx="{offset - 1.3:g}" cy="-1.5" r="1.6" fill="#1847bd">{cx}{cy}</circle>')
        eyes = (
            '<ellipse cx="-4.4" cy="-1.5" rx="3.3" ry="4" fill="white"/>'
            '<ellipse cx="4.4" cy="-1.5" rx="3.3" ry="4" fill="white"/>'
            + "".join(pupils)
        )
        eyes = opacity_group(game, mode, lambda value: value != "frightened", eyes, 'data-part="eyes"')
        face_color = signal_animation(game, fill, "fill", lambda value: "#163cdb" if value == "#ffffff" else "#fff2c7")
        face_stroke = signal_animation(game, fill, "stroke", lambda value: "#163cdb" if value == "#ffffff" else "#fff2c7")
        face = (
            f'<g fill="#fff2c7">{face_color}<circle cx="-3.6" cy="-2" r="1.3"/>'
            '<circle cx="3.6" cy="-2" r="1.3"/></g>'
            f'<path d="M-6,5 L-4,3 L-2,5 L0,3 L2,5 L4,3 L6,5" '
            f'fill="none" stroke="#fff2c7" stroke-width="1.5">{face_stroke}</path>'
        )
        face = opacity_group(game, mode, lambda value: value == "frightened", face, 'data-part="frightened-face"')
        body = (
            f'<path data-part="body" fill="{color}" opacity="1" '
            'd="M-10.5,11 V-1 A10.5,10.5 0 0 1 10.5,-1 '
            f'V11 L7,8 L3.5,11 L0,8 L-3.5,11 L-7,8 Z">{body_fill}{body_opacity}</path>'
        )
        content = opacity_group(game, game.visibility[name], bool, body + eyes + face)
        ghosts.append(f'<g id="{name}" data-character="ghost" transform="translate({position(initial)})">{translate}{content}</g>')

    angles = {(-1, 0): -90, (0, 1): 0, (1, 0): 90, (0, -1): 180}
    rotate = signal_animation(game, game.facing["pacman"], "transform", lambda value: str(angles[value]))
    rotate = rotate.replace("<animate ", '<animateTransform type="rotate" ').replace("</animate>", "</animateTransform>")
    # A rotacao e discreta: a boca sempre aponta para o corredor escolhido.
    normal = (
        '<path fill="#ffe329" d="M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z">'
        '<animate attributeName="d" values="M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z;'
        'M0,0 L10.95,-1 A11,11 0 1 0 10.95,1 Z;'
        'M0,0 L8.8,-6.6 A11,11 0 1 0 8.8,6.6 Z" dur="0.2s" repeatCount="indefinite"/>'
        '</path><circle cx="2.5" cy="-5.5" r="1.3" fill="#05070c"/>'
    )
    normal = opacity_group(game, game.signals["pac_normal"], bool, normal, 'data-part="normal"')
    death = (
        f'<path fill="#ffe329" d="{pac_path(35)}">'
        f'{signal_animation(game, game.signals["death_angle"], "d", pac_path)}</path>'
    )
    death = opacity_group(game, game.signals["pac_death"], bool, death, 'data-part="death"')
    pac_motion = animation([(t, value) for t, value, _ in game.motion["pacman"].points],
                           "transform", duration, position, linear=True, transform="translate")
    initial = game.motion["pacman"].points[0][1]
    pacman = (
        f'<g id="pacman" data-character="pacman" transform="translate({position(initial)})">'
        f'{pac_motion}<g transform="rotate(180)">{rotate}{normal}{death}</g></g>'
    )
    lives = []
    for index, x in enumerate((1060, 1084, 1108)):
        icon = f'<path transform="translate({x} 42) scale(.65)" d="{pac_path(36.87)}"/>'
        lives.append(opacity_group(game, game.signals["lives"], lambda value, i=index: value > i, icon))
    messages = []
    for message in ("READY!", "STAGE CLEAR", "GAME OVER"):
        messages.append(opacity_group(
            game, game.signals["message"], lambda value, target=message: value == target,
            f'<text x="600" y="402" text-anchor="middle" font-size="16" fill="#ffe329">{message}</text>'
        ))
    popups = []
    for index, (time, points, (x, y)) in enumerate(game.captures):
        signal = Signal(0)
        signal.set(time, 1)
        signal.set(time + .85, 0)
        popups.append(opacity_group(
            game, signal, bool,
            f'<text x="{x:g}" y="{y - 17:g}" text-anchor="middle" '
            f'font-size="13" fill="#ffffff">{points}</text>',
            f'id="capture-{index}"'
        ))
    power_hud = opacity_group(
        game, game.signals["power"], lambda value: value > 0,
        '<text x="75" y="673" font-size="15" fill="#ffe329">POWER</text>'
        + number_display(game, game.signals["power"], 138, 673, digits=2, size=15)
    )
    gate_x, gate_y = game.center((8, 17))
    return f"""<svg xmlns="{namespace}" width="{width}" height="{height}"
      viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description"
      data-duration="{duration:.8f}" data-game="autonomous-pacman">
      <title id="title">Pac-Man</title>
      <desc id="description">Partida automatica: perseguicao, pastilhas de poder,
      fantasmas assustados, olhos retornando a casa, vidas, pontuacao e fases.
      A partida se repete continuamente, sem precisar interagir.</desc>
      <rect width="{width}" height="{height}" rx="18" fill="#05070c"/>
      <g font-family="Courier New,monospace" font-weight="700" font-size="19">
        <text x="75" y="48" fill="white">SCORE</text>
        {number_display(game, game.signals["score"], 145, 48)}
        <text x="470" y="48" fill="white">HIGH SCORE</text>
        {number_display(game, game.signals["high"], 600, 48)}
        <text x="965" y="48" fill="white">LIVES</text>
        <g fill="#ffe329">{"".join(lives)}</g>
        <text x="995" y="673" font-size="15" fill="white">STAGE</text>
        {number_display(game, game.signals["level"], 1060, 673, digits=2, size=15)}
        {power_hud}
        {"".join(messages)}
        {"".join(popups)}
      </g>
      <g id="maze" fill="none" stroke="#0878ff" stroke-width="3"
         stroke-linecap="round" stroke-linejoin="round">{wall_animation}{walls}</g>
      <line id="ghost-door" x1="{gate_x - 12:g}" x2="{gate_x + 12:g}"
         y1="{gate_y:g}" y2="{gate_y:g}" stroke="#ff91dd" stroke-width="3"/>
      <g id="pellets">{"".join(dots)}</g>
      {"".join(ghosts)}
      {pacman}
    </svg>
"""


def validate_game(game, left=75, top=78, cell_size=30):
    walls = [
        (left + col * cell_size, top + row * cell_size,
         left + (col + 1) * cell_size, top + (row + 1) * cell_size)
        for row, line in enumerate(game.grid) for col, tile in enumerate(line) if tile == "#"
    ]
    minimum = float("inf")
    for name, motion in game.motion.items():
        for (ta, a, _), (tb, b, _) in zip(motion.points, motion.points[1:]):
            warp = any(ta >= start - EPSILON and tb <= end + EPSILON for start, end in motion.warps)
            if warp:
                visible = game.visibility[name].at((ta + tb) / 2)
                if visible:
                    raise ValueError(f"{name}: reposicionamento visivel ao reiniciar.")
                continue
            if abs(a[0] - b[0]) > .0001 and abs(a[1] - b[1]) > .0001:
                raise ValueError(f"{name}: movimento diagonal cortando um canto.")
            for x1, y1, x2, y2 in walls:
                dx = max(x1 - max(a[0], b[0]), min(a[0], b[0]) - x2, 0)
                dy = max(y1 - max(a[1], b[1]), min(a[1], b[1]) - y2, 0)
                distance = hypot(dx, dy)
                minimum = min(minimum, distance)
                if distance < 12.5 - .0001:
                    raise ValueError(f"{name}: animacao cruzando uma parede.")
    return minimum
