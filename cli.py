import click


@click.group()
def main():
    """
    CLI for the Python Casino Game Simulator.

    From here you can play a simulation of all the available casino games as
    well as run test on all or individual games.
    """


@main.command()
@click.argument('game')
def play(game):
    """Simulate the desired game with the selected player."""
    import casino_simulator
    click.echo(f"Starting '{game.capitalize()}' simulation...")
    casino_simulator.simulate(game)


@main.command()
@click.argument('game', default='all')
@click.option(
    '--verbosity', '-v',
    default='0', type=int,
    help='The level of verbosity to use when running the tests.'
)
def test(game, verbosity):
    """Runs tests on the package as a whole as well as on specific games."""
    import unittest

    message = 'simulator' if game == 'all' else f"'{game.capitalize()}' game"
    location = '' if game == 'all' else game
    click.echo(f"Running tests on the {message}...")
    tests = unittest.TestLoader().discover(f'tests/{location}')
    unittest.TextTestRunner(verbosity=verbosity).run(tests)


if __name__ == '__main__':
    main()
