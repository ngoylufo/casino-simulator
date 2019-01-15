from importlib import import_module


def simulate(casino_game):
    game = import_module(f".{casino_game}", "casino_simulator")
    game.simulate()
