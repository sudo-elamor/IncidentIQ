import time
import random

from config import LOGS_PER_SECOND, LATENCY_MS_MIN, LATENCY_MS_MAX
from utils.csv_reader import read_loghub_csv
from utils.log_generator import generate_log
from utils.logger import log_output, logger  # <- unified logger

def main():
    dataset = "linux"
    csv_path = f"data/{dataset}_logs.csv"

    rows = read_loghub_csv(csv_path, dataset)
    logger.info(f"[Feeder] Loaded {len(rows)} rows from {csv_path}")

    interval = 1 / LOGS_PER_SECOND

    while True:
        row = random.choice(rows)
        log = generate_log(row, dataset=dataset)
        log_output(log)

        # Random latency
        latency = random.randint(LATENCY_MS_MIN, LATENCY_MS_MAX) / 1000
        time.sleep(interval + latency)


if __name__ == "__main__":
    logger.info("[Feeder] Starting Feeder...")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("[Feeder] Stopped by user")
