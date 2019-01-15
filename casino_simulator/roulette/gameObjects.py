import random
from ..gameObjects import (Outcome, OutcomeFactory, Bet, Table, Player, Game,
                           Simulator)
from ..exceptions import InvalidObjectError


class Bin(object):
    """A numbered :class:'Bin' in a roulette wheel containing a number of
    associated :class:'Outcome's.

    Essentially a :class:'Bin' is a collection of :class:'Outcome's associated
    with it. The number of :class:'Outcome's a :class:'Bin' holds depends on
    the number of bet combinations that can be made with the :class:'Bin's
    number.

    Creating an :class:'Bin' object.
        >>> outcomes = Outcome('24', 35), Outcome('Split 24-25', 17)
        >>> Bin(35, *outcomes)
        <Bin 35>

    Printing this :class:'Bin' returns something like this.
        Bin(35, { <Outcome '24' 35:1>, <Outcome 'Split 24-25' 17:1> })
    """

    def __init__(self, number, *outcomes):
        """Initialize an instance of a :class:'Bin' with a given number and list
        of :class:'Outcome's.

        Initializing a Bin object.
            >>> outcomes = Outcome('24', 35), Outcome('Split 24-25', 17)
            >>> bin_ = Bin(35, *outcomes)

        :param number: The number of the :class:'Bin'.
        :param outcomes: :class:'Outcome's to initialize the :class:'Bin' with.
        """
        if not isinstance(number, int):
            raise InvalidObjectError
        self.number, self.outcomes = number, frozenset(outcomes)

    def add(self, outcome):
        """Adds an individual :class:'Outcome' to the :class:'Bin'.

        Adding an Outcome to a Bin.
            >>> bin_ = Bin(2)
            >>> bin_.add(Outcome('2', 35))
            >>> print(bin_)
            Bin(2, {<Outcome '2' 35:1>})
        """
        if not isinstance(outcome, Outcome):
            raise InvalidObjectError
        self.outcomes |= set([outcome])

    def __repr__(self):
        """The type representation of a :class:'Bin' object.

        Create Bins object and get their representation.
            >>> outcomes = Outcome('00', 35), Outcome('Split 23-24', 17)
            >>> Bin(37, outcomes[0]), Bin(23, outcomes[1])
            (<Bin 00>, <Bin 23>)

        :return string: Type representation of the :class:'Outcome'.
        """
        return "<Bin %s>" % ("00" if self.number == 37 else str(self.number))

    def __str__(self):
        """The string representation of a :class:'Bin' object.

        Create Bins object and get their representation.
            >>> outcomes = Outcome('00', 35), Outcome('00-0-1-2-3', 6)
            >>> bin_ = Bin(37, *outcomes)

        Printing this :class:'Bin' returns something like this.
            Bin(37, {<Outcome '00' 35:1>, <Outcome '00-0-1-2-3' 6:1>})

        :return string: String representation of the :class:'Bin'.
        """
        outcomes = ', '.join([repr(oc) for oc in self.outcomes])
        return "Bin(%d, {%s})" % (self.number, outcomes)


class Wheel(object):
    """A :class:'Wheel' is collection of 38 numbered :class:'Bin's, who
    themselves are a collection of :class:'Outcome's. The Wheel uses a random
    number generator to select the wining :class:'Bin's.

    Creating a :class:'Wheel'
        >>> wheel = Wheel()

    Creating a :class:'Wheel' with a custome number generator
        >>> rng = NonRandom()  # Custom random number generator
        >>> wheel = Wheel(rng)
    """
    bins = None
    builder = None
    outcomes = set()

    def __init__(self, rng=None):
        """Initialize a Wheel with 38 Bins and a random number generator."""
        self.rng = random.Random() if rng is None else rng
        self.builder = BinBuilder(self)
        self.build_components()

    def build_components(self):
        self.builder.build_bins()

    def add_outcome(self, number, outcome):
        """Adds the given Outcome to the Bin with the given number.

        :param bin: The Bin (number) to add the Outcome to.
        :param outcome: The Outcome to add.
        """
        if not (isinstance(number, int) and 0 <= number <= 37):
            return NotImplemented
        self.bins[number].add(outcome)
        self.outcomes.add(outcome)

    def get_outcome(self, name):
        """Returns the specified outcome.

        :param name: The Outcome to retrieve.
        :return Outcome:
        """
        for oc in self.outcomes:
            if name == oc.name:
                return oc
        else:
            return False

    def get_random_outcome(self):
        """Returns a random outcome.

        :return Outcome:
        """
        return random.choice(list(self.outcomes))

    def next(self):
        """Generates a random number between 0 and 37, and returns the
        randomly selected Bin."""
        choice = self.rng.choice([num for num in range(38)])
        return self.bins[choice]

    def get(self, number):
        """Returns the specified Bin from the internal collection."""
        if isinstance(number, int) and 0 <= number <= 37:
            return self.bins[number]


class BinBuilder(object):
    """Builds bins with outcomes for a wheel"""
    wheel = None
    fact = None

    def __init__(self, wheel=None):
        """"""
        if wheel is not None:
            self.set_wheel(wheel)
        self.fact = OutcomeFactory()

    def set_wheel(self, wheel):
        if not isinstance(wheel, Wheel):
            raise InvalidObjectError
        self.wheel = wheel

    def build_bins(self, wheel=None):
        if wheel is not None:
            self.set_wheel(wheel)
        self.wheel.bins = tuple([Bin(num) for num in range(38)])

        from inspect import getmembers
        members = getmembers(self)

        for name, method in members:
            if name.startswith("generate"):
                method()

    def generate_zero_bets(self):
        """Generates zero bet Outcomes"""
        oc = self.fact.make('00-0-1-2-3', 6)
        for n in [37, 0, 1, 2, 3]:
            self.wheel.add_outcome(n, oc)

    def generate_straight_bets(self):
        """Generates straight bet Outcomes"""
        self.wheel.add_outcome(0, self.fact.make("0", 35))
        for n in range(1, 37):
            oc = self.fact.make(f"{n}", (35))
            self.wheel.add_outcome(n, oc)
        self.wheel.add_outcome(37, self.fact.make("00", (35)))

    def generate_left_right_split_bets(self):
        """Generates left right split bet Outcomes"""
        for c in [1, 2]:
            for r in range(12):
                n = (3 * r) + c
                oc = self.fact.make(f'Split {n}-{n+1}', 17)
                self.wheel.add_outcome(n, oc)
                self.wheel.add_outcome(n + 1, oc)

    def generate_up_down_split_bets(self):
        """Generates up down split bet Outcomes"""
        for n in range(1, 34):
            oc = self.fact.make(f'Split {n}-{n+3}', (17))
            self.wheel.add_outcome(n, oc)
            self.wheel.add_outcome(n + 3, oc)

    def generate_street_bets(self):
        """Generates street bet Outcomes"""
        for r in range(12):
            n = (3 * r) + 1
            oc = self.fact.make(f"Street {n}-{n+1}-{n+2}", (11))
            for i in range(3):
                self.wheel.add_outcome(n + i, oc)

    def generate_corner_bets(self):
        """Generates corner bet Outcomes"""
        for col in (1, 2):
            for r in range(11):
                n = (3 * r) + col
                oc = self.fact.make(f"Corner {n}-{n+1}-{n+3}-{n+4}", (8))
                for i in [0, 1, 3, 4]:
                    self.wheel.add_outcome(n + i, oc)

    def generate_line_bets(self):
        """Generates line bet Outcomes"""
        for r in range(11):
            n = (3 * r) + 1
            oc = self.fact.make(f"Line {n}-{n+1}-{n+2}-{n+3}-{n+4}-{n+5}", (5))
            for i in range(6):
                self.wheel.add_outcome(n + i, oc)

    def generate_dozen_bets(self):
        """Generates dozen bet Outcomes"""
        for d in range(3):
            oc = self.fact.make(f'Dozen {d+1}', (2))
            for n in range(12):
                number = (12 * d) + n + 1
                self.wheel.add_outcome(number, oc)

    def generate_column_bets(self):
        """Generates column bet Outcomes"""
        for c in range(3):
            oc = self.fact.make(f'Column {c+1}', (2))
            for r in range(12):
                number = (3 * r) + c + 1
                self.wheel.add_outcome(number, oc)

    def generate_even_money_bets(self):
        """Generates even money bet Outcomes"""
        red = self.fact.make('Red', 1)
        black = self.fact.make('Black', 1)
        even = self.fact.make('Even', 1)
        odd = self.fact.make('Odd', 1)
        high = self.fact.make('High', 1)
        low = self.fact.make('Low', 1)

        for n in range(1, 37):
            if n < 19:
                self.wheel.add_outcome(n, low)
            else:
                self.wheel.add_outcome(n, high)

            if n % 2:
                self.wheel.add_outcome(n, odd)
            else:
                self.wheel.add_outcome(n, even)

            if n in [1, 3, 5, 7, 9, 12, 14, 16, 18,
                     19, 21, 23, 25, 30, 32, 34, 36]:
                self.wheel.add_outcome(n, red)
            else:
                self.wheel.add_outcome(n, black)


class RouletteTable(Table):
    """The :class:'Table' in a game of roulette consisting of a :class:'Wheel'
    and :class:'Bet's."""

    def __init__(self, _min=10, _max=500):
        """Initialize a new :class:'Table' with a :class:'Wheel' and limits."""
        super(RouletteTable, self).__init__()
        self.min, self.max, self.bets = (_min, _max, list())

    def build_components(self):
        self.wheel = Wheel()

    def is_valid(self, bet):
        """Determines whether the bet placed on the :class:'Table' is valid.

        A :class:'Bet' is valid if the sum of the current :class:'Bet' and all
        other :class:'Bet's placed on the table is greater than or equal to the
        :class:'Table' minimum but less than or equal to the maximum.
        """
        if not(self.max >= bet.amount >= self.min):
            return False

        total = 0
        for current in self:
            total += current.amount
        return self.max >= (total + bet.amount)


class RoulettePlayer(Player):
    rounds = 250

    def set_rounds(self, rounds):
        self.rounds = rounds

    def can_continue(self):
        bet = self.make_bet()
        return self.rounds > 0 and self.can_bet(bet)

    def place_bet(self):
        self.rounds -= 1
        bet = self.make_bet()
        if not (self.can_continue() and self.can_bet(bet)):
            return
        self.stake -= bet.amount
        self.table.place_bet(bet)


class Passenger57(RoulettePlayer):
    """A :class:'Player' who always bets on black."""

    def __init__(self, table):
        """Instantiates a new :class:'Passenger57' :class:'Player'."""
        super(Passenger57, self).__init__(table)
        self.black = self.table.wheel.get_outcome('Black')

    def make_bet(self):
        if not (self.table.min > self.stake):
            amount = random.randint(self.table.min, self.stake)
        else:
            amount = 50
        return Bet(amount, self.black)

    def win(self, bet):
        super(Passenger57, self).win(bet)
        print(f"Player won: ${bet.win_amount()}.00 from a ${bet.amount}.00 bet.")

    def lose(self, bet):
        super(Passenger57, self).lose(bet)
        print(f'Player lost: ${bet.lose_amount()}.00')


class Martingale(RoulettePlayer):
    loss_count = 0

    def __init__(self, table, wager=10):
        super(Martingale, self).__init__(table)
        self.wager = wager
        # define a random wager? table.min <==> table.max * 0.1

    def make_bet(self):
        amount = self.wager * (2**self.loss_count)
        outcome = self.table.wheel.get_random_outcome()
        return Bet(amount, outcome)

    def win(self, bet):
        super(Martingale, self).win(bet)
        self.loss_count = 0
        # print(self.rounds, self.loss_count, self.stake)

    def lose(self, bet):
        self.loss_count += 1
        # print(self.rounds, self.loss_count, self.stake)


class RouletteGame(Game):
    """The game"""
    table = None

    def __init__(self, configurations):
        super(RouletteGame, self).__init__(configurations)

    def build_components(self, configurations):
        limits = configurations['table_limits']
        self.table = RouletteTable(limits["min"], limits["max"])

    def cycle(self, player):
        if not isinstance(player, RoulettePlayer):
            raise InvalidObjectError

        player.place_bet()
        win_bin = self.table.wheel.next()

        for bet in self.table:
            if bet.outcome in win_bin.outcomes:
                player.win(bet)
            else:
                player.lose(bet)
        self.table.clear()


class RouletteSimulator(Simulator):
    """A :class:'RouletteSimulator' responsible for simulating game sessions."""
    init_duration = 250
    init_stake = 100
    samples = 50
    player_class = None

    def __init__(self, configurations, player_class):
        super(RouletteSimulator, self).__init__(configurations, player_class)
        self.durations, self.maxima = (list(), list())

    def setup_session(self, configurations):
        game_config = configurations["game"]
        session_config = configurations["session"]

        self.game = RouletteGame(game_config)
        self.set_init_duration(session_config["init_duration"])
        self.set_init_stake(session_config["init_stake"])
        self.set_samples(session_config["samples"])

    def set_init_duration(self, duration):
        self.init_duration = duration

    def set_init_stake(self, stake):
        self.init_stake = stake

    def set_samples(self, samples):
        self.samples = samples

    def create_player(self, player_class=None):
        available = {
            'Passenger57': Passenger57, 'Martingale': Martingale,
        }
        if player_class is not None:
            self.player_class = player_class

        self.player = available[self.player_class](self.game.table)
        self.player.set_stake(self.init_stake)
        self.player.set_rounds(self.init_duration)

    def session(self):
        stakes = list()

        while self.player.playing():
            self.game.cycle(self.player)
            stakes.append(int(self.player.stake))

        self.create_player()
        return stakes

    def gather(self):
        for sample in range(self.samples):
            session = self.session()
            self.durations.append(len(session))
            self.maxima.append(max(session))
