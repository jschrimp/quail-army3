import random
from dataclasses import dataclass, field
from typing import Dict, List
import matplotlib.pyplot as plt


# -----------------------------
# DATA STRUCTURES
# -----------------------------
@dataclass
class Nation:
    name: str
    population: float
    resources: float
    military: float
    trade_openness: float  # between 0 and 1
    strategy: str = "cooperate"
    history_resources: List[float] = field(default_factory=list)
    history_population: List[float] = field(default_factory=list)
    history_military: List[float] = field(default_factory=list)
    history_strategy: List[str] = field(default_factory=list)

    def record_history(self) -> None:
        self.history_resources.append(self.resources)
        self.history_population.append(self.population)
        self.history_military.append(self.military)
        self.history_strategy.append(self.strategy)


# -----------------------------
# INITIAL SETUP
# -----------------------------
def create_nations() -> Dict[str, Nation]:
    return {
        "Quail Empire": Nation(
            name="Quail Empire",
            population=100.0,
            resources=120.0,
            military=60.0,
            trade_openness=0.75,
        ),
        "Fox Confederacy": Nation(
            name="Fox Confederacy",
            population=85.0,
            resources=95.0,
            military=85.0,
            trade_openness=0.45,
        ),
        "Deer Republic": Nation(
            name="Deer Republic",
            population=110.0,
            resources=140.0,
            military=40.0,
            trade_openness=0.85,
        ),
        "Turtle Kingdom": Nation(
            name="Turtle Kingdom",
            population=70.0,
            resources=160.0,
            military=35.0,
            trade_openness=0.60,
        ),
    }


def create_trade_matrix() -> Dict[str, Dict[str, float]]:
    return {
        "Quail Empire": {
            "Fox Confederacy": 8.0,
            "Deer Republic": 12.0,
            "Turtle Kingdom": 6.0,

        },
        "Fox Confederacy": {
            "Quail Empire": 5.0,
            "Deer Republic": 4.0,
            "Turtle Kingdom": 3.0,
        },
        "Deer Republic": {
            "Quail Empire": 10.0,
            "Fox Confederacy": 6.0,
            "Turtle Kingdom": 8.0,
        },
        "Turtle Kingdom": {
            "Quail Empire": 4.0,
            "Fox Confederacy": 2.0,
            "Deer Republic": 7.0,
        },
    }


# -----------------------------
# STRATEGY RULES
# -----------------------------
def choose_strategy(nation: Nation) -> str:
    """
    Simple decision rules:
    - If resources are low, isolate or compete.
    - If military is weak and resources are strong, cooperate.
    - If military is strong, sometimes compete.
    """
    if nation.resources < 60:
        return random.choice(["isolate", "compete"])
    if nation.military > 90 and nation.resources > 80:
        return random.choice(["compete", "cooperate"])
    if nation.trade_openness > 0.7:
        return "cooperate"
    return random.choice(["cooperate", "isolate"])


# -----------------------------
# ECONOMIC DYNAMICS
# -----------------------------
def apply_trade(nations: Dict[str, Nation], trade_matrix: Dict[str, Dict[str, float]]) -> None:
    """
    Trade adds resources depending on trade openness of both countries.
    """
    resource_changes = {name: 0.0 for name in nations.keys()}
    for exporter_name, partners in trade_matrix.items():
        exporter = nations[exporter_name]
        for importer_name, base_trade in partners.items():
            importer = nations[importer_name]
            if exporter.strategy == "isolate" or importer.strategy == "isolate":
                effective_trade = 0.0
            else:
                effective_trade = (
                        base_trade
                        * exporter.trade_openness
                        * importer.trade_openness
                )
            if exporter.strategy == "compete":
                effective_trade *= 0.7
            if importer.strategy == "compete":
                effective_trade *= 0.7
            # Both sides benefit slightly from trade
            resource_changes[exporter_name] += effective_trade * 0.6
            resource_changes[importer_name] += effective_trade * 0.4
    for name, delta in resource_changes.items():
        nations[name].resources += delta


def apply_internal_growth(nations: Dict[str, Nation]) -> None:
    """
    Nations consume resources to sustain population.
    Growth depends on available resources.
    """
    for nation in nations.values():
        consumption = nation.population * 0.18
        nation.resources -= consumption
        if nation.resources > 100:
            nation.population *= 1.03
        elif nation.resources > 50:
            nation.population *= 1.01
        else:
            nation.population *= 0.97

        # Keep values from going negative
        nation.resources = max(nation.resources, 0.0)
        nation.population = max(nation.population, 1.0)


def apply_military_changes(nations: Dict[str, Nation]) -> None:
    """
    Competing nations spend more on military.
    Cooperating nations invest less.
    """
    for nation in nations.values():
        if nation.strategy == "compete":
            military_gain = 4.0
            military_cost = 6.0
        elif nation.strategy == "isolate":
            military_gain = 2.0
            military_cost = 3.0
        else:
            military_gain = 1.0
            military_cost = 1.5
        nation.military += military_gain
        nation.resources -= military_cost
        nation.resources = max(nation.resources, 0.0)
        nation.military = max(nation.military, 0.0)


def apply_random_shocks(nations: Dict[str, Nation], shock_probability: float = 0.20) -> List[str]:
    """
    Random events to make the simulation more realistic.
    """
    events = []
    for nation in nations.values():
        if random.random() < shock_probability:
            shock_type = random.choice(["drought", "trade disruption", "conflict", "harvest boom"])
            if shock_type == "drought":
                loss = random.uniform(10, 25)

                nation.resources = max(nation.resources - loss, 0.0)
                events.append(f"{nation.name} suffered drought: -{loss:.1f} resources")
            elif shock_type == "trade disruption":
                nation.trade_openness = max(nation.trade_openness - 0.10, 0.10)
                events.append(f"{nation.name} suffered trade disruption: lower openness")
            elif shock_type == "conflict":
                loss = random.uniform(5, 15)
                nation.population = max(nation.population - loss, 1.0)
                nation.military = max(nation.military - loss * 0.5, 0.0)
                events.append(f"{nation.name} suffered conflict: -{loss:.1f} population")
            elif shock_type == "harvest boom":
                gain = random.uniform(10, 25)
                nation.resources += gain
                events.append(f"{nation.name} gained harvest boom: +{gain:.1f} resources")
    return events


# -----------------------------
# SIMULATION
# -----------------------------
def run_simulation(turns: int = 30, seed: int = 42) -> Dict[str, Nation]:
    random.seed(seed)
    nations = create_nations()
    trade_matrix = create_trade_matrix()
    print("\n=== STARTING QUAIL EMPIRE SIMULATION ===\n")
    for turn in range(1, turns + 1):
        print(f"--- Turn {turn} ---")
        # Choose strategies
        for nation in nations.values():
            nation.strategy = choose_strategy(nation)
            # Apply system changes
            apply_trade(nations, trade_matrix)
            apply_internal_growth(nations)
            apply_military_changes(nations)

            shock_events = apply_random_shocks(nations)
        # Record history
        for nation in nations.values():
            nation.record_history()
        # Print turn summary
        for nation in nations.values():
            print(
                f"{nation.name:18} | Strategy: {nation.strategy:10} "
                f"| Pop: {nation.population:7.1f} "
                f"| Res: {nation.resources:7.1f} "
                f"| Mil: {nation.military:7.1f}"
            )
        if shock_events:
            print(" Events:")
            for event in shock_events:
                print(f" - {event}")
    print()
    return nations


# -----------------------------
# REPORTING
# -----------------------------
def print_final_summary(nations: Dict[str, Nation]) -> None:
    print("\n=== FINAL SUMMARY ===\n")
    for nation in nations.values():
        status = classify_nation(nation)
        print(
            f"{nation.name:18} | Final Pop: {nation.population:7.1f} "
            f"| Final Res: {nation.resources:7.1f} "
            f"| Final Mil: {nation.military:7.1f} "
            f"| Status: {status}"
        )


def classify_nation(nation: Nation) -> str:
    if nation.resources > 120 and nation.population > 100:
        return "Strong Growth"
    if nation.resources < 25 or nation.population < 40:
        return "Collapse Risk"
    if nation.military > 100 and nation.resources < 50:
        return "Over-Militarized"
    return "Stable / Mixed"


def plot_results(nations: Dict[str, Nation]) -> None:
    turns = list(range(1, len(next(iter(nations.values())).history_resources) + 1))
    # Resources plot
    plt.figure(figsize=(10, 6))
    for nation in nations.values():
        plt.plot(turns, nation.history_resources, label=nation.name)
    plt.title("Resources Over Time")
    plt.xlabel("Turn")
    plt.ylabel("Resources")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    # Population plot
    plt.figure(figsize=(10, 6))
    for nation in nations.values():
        plt.plot(turns, nation.history_population, label=nation.name)
    plt.title("Population Over Time")
    plt.xlabel("Turn")
    plt.ylabel("Population")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    # Military plot
    plt.figure(figsize=(10, 6))
    for nation in nations.values():
        plt.plot(turns, nation.history_military, label=nation.name)
    plt.title("Military Strength Over Time")
    plt.xlabel("Turn")
    plt.ylabel("Military")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    allNations = run_simulation(turns=30, seed=42)
    print_final_summary(allNations)
    plot_results(allNations)