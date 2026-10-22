"""Regras da partida autonoma e integridade dos trajetos exportados."""
from collections import Counter
from math import hypot
import unittest
import xml.etree.ElementTree as ET

import generate_pacman as maze
from pacman_game import Game, HOMES, POWERS, SPAWN, render_game, validate_game


def new_game(seed=2026):
    grid = maze.make_maze()
    return Game(grid, maze.make_graph(grid), maze.make_graph(grid, True), maze.center, seed)


class Rules(unittest.TestCase):
    def setUp(self):
        self.game = new_game()

    def until(self, predicate, limit=400):
        for _ in range(limit):
            if predicate():
                return
            self.game.advance()
        self.fail("A transicao esperada nao ocorreu.")

    def test_red_ghost_retargets_the_pacman_position(self):
        game = self.game
        ghost = game.ghosts[0]
        ghost.mode, ghost.cell, ghost.previous = "chase", (4, 17), None
        game.play_time = 8
        game.pac.cell = (4, 25)
        self.assertEqual(game.ghost_choice(ghost), (4, 18))
        game.pac.cell = (4, 9)
        self.assertEqual(game.ghost_choice(ghost), (4, 16))

    def test_swept_collision_catches_opposite_directions(self):
        fraction = Game.collision_time((0, 0), (30, 0), (30, 0), (0, 0))
        self.assertAlmostEqual(fraction, .2)
        self.assertIsNone(Game.collision_time((0, 0), (30, 0), (0, 60), (30, 60)))

    def test_power_reverses_without_teleporting_and_stacks_points(self):
        game = self.game
        ghost = game.ghosts[0]
        ghost.cell, ghost.destination, ghost.progress = (4, 8), (4, 9), .4
        ghost.mode = "chase"
        before = ghost.position(game.center)
        game.eat((1, 1))
        self.assertEqual(ghost.mode, "frightened")
        self.assertEqual(ghost.position(game.center), before)
        self.assertEqual((ghost.cell, ghost.destination), ((4, 9), (4, 8)))
        self.assertEqual(game.score, 50)
        for ghost in game.ghosts:
            game.eat_ghost(ghost)
            self.assertEqual(ghost.mode, "eyes")
        self.assertEqual(game.score, 50 + 200 + 400 + 800 + 1600)
        self.assertEqual([points for _, points, _ in game.captures], [200, 400, 800, 1600])

    def test_eyes_return_to_the_house_and_regenerate(self):
        game = self.game
        game.status = "playing"
        ghost = game.ghosts[0]
        ghost.mode, ghost.cell = "eyes", (7, 17)
        self.until(lambda: any(event[1] == "regenerated" for event in game.events))
        self.assertEqual(ghost.cell, HOMES[0])
        self.assertEqual(ghost.mode, "house")
        self.assertGreater(ghost.release, game.time)

    def test_power_expiry_restores_the_chase(self):
        game = self.game
        game.status, game.time, game.power_until = "playing", 10.0, 9.0
        ghost = game.ghosts[0]
        ghost.mode, ghost.cell = "frightened", (4, 8)
        game.advance()
        self.assertEqual(ghost.mode, "chase")

    def test_death_preserves_the_remaining_dots_and_score(self):
        game = self.game
        game.eat(SPAWN)
        remaining = set(game.remaining)
        game.die()
        self.assertEqual(game.lives, 2)
        self.until(lambda: game.status == "ready")
        self.assertEqual(game.pac.cell, SPAWN)
        self.assertEqual(game.remaining, remaining)
        self.assertEqual(game.score, 10)

    def test_empty_board_starts_the_next_level(self):
        game = self.game
        game.remaining = {SPAWN}
        game.eat(SPAWN)
        self.assertEqual(game.status, "clear")
        self.until(lambda: game.level == 2)
        self.assertEqual(game.status, "ready")
        self.assertEqual(game.remaining, set(game.outside))
        self.assertEqual(game.lives, 3)

    def test_game_over_restarts_without_input(self):
        game = self.game
        game.lives, game.score = 1, 800
        game.die()
        self.until(lambda: any(event[1] == "new_game" for event in game.events))
        self.assertEqual((game.status, game.lives, game.score, game.level), ("ready", 3, 0, 1))


class CompleteAnimation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = new_game().simulate()
        walls = "".join(f'<path d="{maze.rounded_path(p)}"/>' for p in maze.wall_contours(cls.game.grid))
        cls.svg = render_game(cls.game, walls)
        cls.root = ET.fromstring(cls.svg)

    def test_default_game_demonstrates_all_requested_mechanics(self):
        counts = Counter(event[1] for event in self.game.events)
        for event in ("power", "ghost_eaten", "regenerated", "death", "level_clear", "level_started", "game_over"):
            self.assertGreater(counts[event], 0, event)
        self.assertTrue(any(value == "#ffffff" for signal in self.game.ghost_fill.values() for _, value in signal.points))

    def test_every_rendered_movement_clears_the_walls(self):
        self.assertGreaterEqual(validate_game(self.game, maze.LEFT, maze.TOP, maze.CELL), 15 - 1e-6)
        for name, motion in self.game.motion.items():
            self.assertEqual(motion.points[0][1], motion.points[-1][1], name)

    def test_dots_disappear_when_pacman_reaches_them(self):
        from bisect import bisect_right
        positions = self.game.motion["pacman"].points
        times = [p[0] for p in positions]
        for cell, signal in self.game.dots.items():
            for time, visible in signal.points:
                if visible or time == 0:
                    continue
                index = max(0, bisect_right(times, time) - 1)
                t0, a, _ = positions[index]
                t1, b, _ = positions[min(index + 1, len(positions) - 1)]
                fraction = 0 if t1 == t0 else (time - t0) / (t1 - t0)
                actual = (a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction)
                expected = maze.center(cell)
                self.assertLess(hypot(actual[0] - expected[0], actual[1] - expected[1]), .001)

    def test_svg_has_one_clock_and_valid_keyframes(self):
        ids = [e.attrib["id"] for e in self.root.iter() if "id" in e.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        transforms = []
        for element in self.root.iter():
            if "keyTimes" not in element.attrib:
                continue
            keys = [float(v) for v in element.attrib["keyTimes"].split(";")]
            self.assertEqual(keys[0], 0)
            self.assertEqual(keys[-1], 1)
            self.assertTrue(all(a <= b for a, b in zip(keys, keys[1:])))
            self.assertEqual(len(keys), len(element.attrib["values"].split(";")))
            self.assertAlmostEqual(float(element.attrib["dur"][:-1]), self.game.duration, places=7)
            if element.attrib.get("type") == "translate":
                transforms.append(element)
        self.assertEqual(len(transforms), 5)
        self.assertLess(len(self.svg.encode("utf-8")), 1_000_000)


if __name__ == "__main__":
    unittest.main()
