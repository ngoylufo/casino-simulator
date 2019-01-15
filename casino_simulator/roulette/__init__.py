import statistics
from .gameObjects import RouletteSimulator

configurations = {
    "player_class": "Martingale",
    "configurations": {
        "game": {"table_limits": {"max": 500, "min": 5}},
        "session": {"init_duration": 250, "init_stake": 100, "samples": 50}
    }
}


def simulate():
    answer = input("Use custom configurations? (Yes/No) ")
    if answer == "Yes":
        configurations["player_class"] = input("Player (Available: Martingale): ")
        mn = int(input("Min table limit: "))
        mx = int(input("Max table limit: "))
        configurations["configurations"]["game"]["table_limits"] = {"max": mx, "min": mn}

    simulator = RouletteSimulator(**configurations)
    simulator.gather()
    durations, maxima = simulator.durations, simulator.maxima

    print(f"""
{configurations["player_class"]}
Durations
    min : {min(durations)}
    max : {max(durations)}
    mean: {statistics.mean(durations):.2f}
    dev : {statistics.stdev(durations):.2f}

Maxima
    min : {min(maxima)}
    max : {max(maxima)}
    mean: {statistics.mean(maxima):.2f}
    dev : {statistics.stdev(maxima):.2f}
""")
