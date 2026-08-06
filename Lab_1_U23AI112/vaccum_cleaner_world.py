# ==========================================
# AI Lab - Experiment 1 Exercises
# Simple Reflex Agent - Vacuum Cleaner World
# ==========================================

import random

# ======================================================
# EXERCISE 1
# Model-Based Reflex Agent
# ======================================================

print("\n==============================")
print("EXERCISE 1")
print("Model-Based Reflex Agent")
print("==============================")

class VacuumEnvironment:
    def __init__(self):
        self.rooms = {'A': 'Dirty', 'B': 'Dirty'}
        self.location = 'A'
        self.score = 0

    def percept(self):
        return (self.location, self.rooms[self.location])

    def execute(self, action):
        if action == "Suck":
            if self.rooms[self.location] == "Dirty":
                self.rooms[self.location] = "Clean"
                self.score += 10

        elif action == "Right":
            if self.location == "A":
                self.location = "B"
                self.score -= 1

        elif action == "Left":
            if self.location == "B":
                self.location = "A"
                self.score -= 1


class ModelBasedAgent:
    def __init__(self):
        self.memory = {'A': 'Unknown', 'B': 'Unknown'}

    def action(self, percept):
        location, status = percept
        self.memory[location] = status

        if status == "Dirty":
            return "Suck"

        if self.memory['A'] == "Clean" and self.memory['B'] == "Clean":
            return "NoOp"

        if location == "A":
            return "Right"
        else:
            return "Left"


env = VacuumEnvironment()
agent = ModelBasedAgent()

for step in range(20):
    percept = env.percept()
    action = agent.action(percept)

    print(f"Step {step+1}: {percept} -> {action}")

    if action == "NoOp":
        break

    env.execute(action)

print("\nFinal Rooms:", env.rooms)
print("Performance Score:", env.score)

print("\nComparison (20 Steps)")
print("Simple Reflex Agent Score : 2")
print("Model-Based Agent Score   :", env.score)


# ======================================================
# EXERCISE 2
# 1 x N Corridor
# ======================================================

print("\n\n==============================")
print("EXERCISE 2")
print("1 x N Vacuum Cleaner World")
print("==============================")

N = 5

rooms = [random.choice(["Dirty", "Clean"]) for _ in range(N)]
position = 0
score = 0

print("Initial Rooms:", rooms)

while True:

    if rooms[position] == "Dirty":
        print(f"Room {position} is Dirty -> Suck")
        rooms[position] = "Clean"
        score += 10
    else:
        print(f"Room {position} is Clean")

    if all(room == "Clean" for room in rooms):
        break

    if position < N - 1:
        position += 1
    else:
        position = 0

    score -= 1

print("\nFinal Rooms:", rooms)
print("Performance Score:", score)


# ======================================================
# EXERCISE 3
# Dirt Reappears with Probability 0.1
# ======================================================

print("\n\n==============================")
print("EXERCISE 3")
print("Dynamic Environment (Dirt Reappears)")
print("==============================")

rooms = {'A': 'Dirty', 'B': 'Dirty'}
location = 'A'
score = 0

print("Initial Rooms:", rooms)

for step in range(20):

    print(f"\nStep {step+1}")

    if rooms[location] == "Dirty":
        print(f"Agent at {location}: Dirty -> Suck")
        rooms[location] = "Clean"
        score += 10
    else:
        print(f"Agent at {location}: Clean -> Move")
        if location == 'A':
            location = 'B'
        else:
            location = 'A'
        score -= 1

    # Dirt reappears with probability 0.1
    for room in rooms:
        if random.random() < 0.1:
            rooms[room] = "Dirty"

    print("Rooms:", rooms)
    print("Score:", score)

print("\nFinal Rooms:", rooms)
print("Final Performance Score:", score)

print("\nObservation:")
print("Since dirt can reappear randomly, the reflex agent keeps moving")
print("and cleaning whenever required. In this dynamic environment,")
print("continuous monitoring makes the reflex agent rational.")