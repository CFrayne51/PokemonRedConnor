import json
import matplotlib.pyplot as plt
import os

def plot_winrates(log_path):
    if not os.path.exists(log_path):
        print(f"Log file {log_path} not found yet. Training must run first.")
        return

    iterations = []
    test_wrs = []
    train_wrs = []

    with open(log_path, "r") as f:
        for line in f:
            data = json.loads(line)
            iterations.append(data["iteration"])
            test_wrs.append(data["test_winrate"])
            train_wrs.append(data["train_winrate"])

    plt.figure(figsize=(10, 5))
    plt.plot(iterations, test_wrs, label="Test (Fixed States)", marker='o')
    plt.plot(iterations, train_wrs, label="Training (Random States)", marker='x')
    plt.xlabel("Iteration (100 Rollouts each)")
    plt.ylabel("Winrate")
    plt.title("Winrate Trend during Training")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_winrates("v2/battle_runs/test_winrates.jsonl")
