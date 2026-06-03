def simulation():
    print("[6/7] Running Event Simulation...")
    logs = [
        "08:00 Order_001 Created",
        "08:05 Order_001 Assigned to Waterbus (Bach Dang)",
        "08:35 Order_001 Delivered successfully"
    ]
    with open("results/simulation_log.txt", "w") as f:
        for log in logs: f.write(log + "\n")
    print("  -> Simulation log saved.")