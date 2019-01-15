import abc
from fractions import Fraction
from .exceptions import InvalidObjectError, InvalidBetError


class Outcome(object):
    """An :class:'Outcome' in a casino table game on which a bet can be placed.
    :class:'Outcome's have names and odds, they can also generate the amount of
    their respective payouts.

    Creating :class:'Outcome' objects.
        >>> _35 = Fraction(35)
        >>> oc1, oc2 = Outcome('00', _35), Outcome('17', _35)
        >>> oc1, str(oc2)
        (<Outcome '00' 35:1>, "17 (35:1)")
    """
    _hash = None

    def __init__(self, name, odds):
        """Initialize a new :class:'Outcome' object with a given name and odds.

        :class:'Outcome' initialization.
            >>> oc = Outcome('Dozen 1', Fraction(2))

        :param name: The name of the :class:'Outcome'.
        :param odds: Odds of the :class:'Outcome'.
        """
        if not isinstance(odds, Fraction):
            raise InvalidObjectError
        self.name = name
        self.odds = odds

    def win_amount(self, amount):
        """The payout the :class:'Outcome' gives.

        :return Fraction: Product of the odds and amount bet.
        """
        return (self.odds * amount)

    def __eq__(self, other):
        """Compares two :class:'Outcome's for equality based on their names
        ignoring their respective odds.

        Comparing :class:'Outcome's for equality.
            >>> _35 = Fraction(35)
            >>> oc1, oc2 = Outcome('00', _35), Outcome('17', _35)
            >>> oc1 == oc2  # Outcomes with different names
            False

        :param other: The object to compare the :class:'Outcome' to.
        :return bool: The evaluation of the comparison.
        """
        if not isinstance(other, Outcome):
            return False
        return self.name == other.name

    def __ne__(self, other):
        """Compares two :class:'Outcome's for inequality based on their names
        ignoring their respective odds.

        Comparing :class:'Outcome's for inequality.
            >>> _35 = Fraction(35)
            >>> oc1, oc2 = Outcome('00', _35), Outcome('17', _35)
            >>> oc1 != oc2  # Outcomes with different names
            True

        :param other: :class:'Outcome' object to compare to.
        :return bool: The evaluation of the comparison.
        """
        if not isinstance(other, Outcome):
            return True
        return self.name != other.name

    def __hash__(self):
        """Returns the hash value for the :class:'Outcome'.

        The hash value of an :class:'Outcome' is generated from its name. The
        hash is evaluated once and cached to be returned on subsequent calls.

        :return int: The cached hash value of the :class:'Outcome'.
        """
        if self._hash is None:
            self._hash = hash(self.name)
        return self._hash

    def __repr__(self):
        """The type representation of an :class:'Outcome' object.

        Create an :class:'Outcome' object and get it's representation.
            >>> Outcome('Line 1-2-3-5', Fraction(6))
            <Outcome 'Line 1-2-3-5' 6:1>

        :return string: Type representation of the :class:'Outcome'.
        """
        numerator = self.odds._numerator
        denominator = self.odds._denominator
        return "<Outcome '%s' %d:%d>" % (self.name, numerator, denominator)

    def __str__(self):
        """The string representaion of an :class:'Outcome' object.

        Create an :class:'Outcome' object and print it as a string.
            >>> print(Outcome('Line 1-2-3-5', 6))
            Line 1-2-3-5 (6:1)

        :return string: String representation of the :class:'Outcome'.
        """
        numerator = self.odds._numerator
        denominator = self.odds._denominator
        return "%s (%d:%d)" % (self.name, numerator, denominator)


class OutcomeFactory(object):
    """Creates unique outcomes."""
    outcomes = dict()

    def make(self, name, odds):
        """Produces an outcome object."""
        if name in self.outcomes:
            return self.outcomes[name]
        return self._outcome(name, odds)

    def _outcome(self, name, odds):
        """Creates a new outcome object."""
        self.outcomes[name] = Outcome(name, Fraction(odds))
        return self.outcomes[name]


class Bet(object):
    """The amount the a player has wagered on a specific :class:'Outcome'.

    :class:'Bet's are responsible for maintaining an association an amount, an
    :class:'Outcome', and a specific :class:'Player'.

    Creating :class:'Bet's:
        >>> bet = Bet(45, Outcome('Red', Fraction(1)))
        >>> bet, str(bet)
        (<Bet '45', 'Red (1:1)'>, "45 on Red")
    """

    def __init__(self, amount, outcome):
        """Initialize a :class:'Bet' instance wagering an amount on a specific
        :class:'Outcome'.

        Creating a :class:'Bet'
            >>> bet = Bet(45, 'Red')
        """
        if not isinstance(amount, int) or not isinstance(outcome, Outcome):
            raise InvalidObjectError
        self.amount, self.outcome = amount, outcome

    def win_amount(self):
        """Return amount won by the :class:'Bet'."""
        return self.outcome.win_amount(self.amount) + self.amount

    def lose_amount(self):
        """Return amount lost by the :class:'Bet'."""
        return self.amount

    def __repr__(self):
        """The type representation of an :class:'Bet' object.

        Create a Bet object and get its representation.
            >>> Bet(50, Outcome('Split 1-2', 17))
            <Bet '50', 'Split 1-2 (17:1)'>

        :return string: Type representation of the :class:'Bet'.
        """
        return "<Bet '%d', '%s'>" % (self.amount, self.outcome)

    def __str__(self):
        """The string representation of an :class:'Bet' object.

        Create a Bet object and print its representation.
            >>> print(Bet(50, Outcome('Split 1-2', 17)))
            50 on Split 1-2

        :return string: String representation of the :class:'Bet'.
        """
        # TODO: Change self.outcome to self.outcome.name
        return "%d on %s" % (self.amount, self.outcome.name)


class Table(abc.ABC):
    """The Table on which the casino games are played."""

    def __init__(self):
        self.build_components()

    @abc.abstractmethod
    def build_components(self):
        pass

    @abc.abstractmethod
    def is_valid(self, bet):
        """Determines whether the bet placed on the :class:'Table' is valid.

        :return bool:
        """

    def place_bet(self, bet):
        """Places a :class:'Bet' on the :class:'Table'.

        Before a :class:'Bet' can be placed on the :class:'Table' it is first
        validated.
        """
        if not self.is_valid(bet):
            raise InvalidBetError
        self.bets.append(bet)

    def clear(self):
        """Clears all :class:'Bet's on the :class:'Table'."""
        self.bets.clear()

    def __iter__(self):
        """Returns an iterator over all :class:'Bet's currently sitting on the
        table."""
        return iter(self.bets)

    def __repr__(self):
        """The type representation of an :class:'Table' object."""
        return "<Table '%d Bets'>" % len(self.bets)

    # TODO Add __str__ method for table returning an easy-to-read string
    # representation of all current bets on the table.
    def __str__(self):
        bets = ', '.join([repr(bet) for bet in self.bets])
        return "Table(%s)" % (bets)


class Player(abc.ABC):
    stake = None
    table = None

    def __init__(self, table):
        self.table = table

    def set_stake(self, stake):
        self.stake = stake

    def can_bet(self, bet):
        if bet.amount > self.stake or not self.is_valid(bet):
            return False
        return True

    def is_valid(self, bet):
        return self.table.is_valid(bet)

    @abc.abstractmethod
    def can_continue(self):
        pass

    def playing(self):
        # maybe this should do more
        return self.can_continue()

    @abc.abstractmethod
    def place_bet(self, bet):
        pass

    @abc.abstractmethod
    def make_bet(self):
        pass

    def win(self, bet):
        self.stake += bet.win_amount()

    @abc.abstractmethod
    def lose(self, bet):
        pass


class Game(abc.ABC):
    """The game class"""

    def __init__(self, configurations):
        self.build_components(configurations)

    @abc.abstractmethod
    def build_components(self, configurations):
        pass

    @abc.abstractmethod
    def cycle(self, player):
        pass


class Simulator(abc.ABC):
    """docstring for Simulator"""

    def __init__(self, configurations, player_class):
        """Initiates the simulator with a given player class and other
        configuration settings."""
        self.setup_session(configurations)
        self.create_player(player_class)

    @abc.abstractmethod
    def setup_session(self, configurations):
        """Sets up all the components and attributes required to run the casino
        game simulation."""

    @abc.abstractmethod
    def create_player(self, player_class):
        """Creates a player to participate in the casino game."""

    @abc.abstractmethod
    def session(self):
        """Simulates a game session."""

    @abc.abstractmethod
    def gather(self):
        """Gathers all information produced by a game session."""
