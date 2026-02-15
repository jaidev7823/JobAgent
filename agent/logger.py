def log_data(text):
    with open("agent/output/logs.txt", "a") as f:
        f.write(text + "\n\n")
