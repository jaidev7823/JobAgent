def log_data(text):
    with open("outputs/logs.txt", "a") as f:
        f.write(text + "\n\n")
