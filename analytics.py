import time
import pandas as pd


class NetworkAnalytics:
    def __init__(self):
        self.statistics = {
            "action": [],
            "filename": [],
            "data_rate_kbps": [],
            "transfer_time_s": [],
            "timestamp": []
        }

    def record_statistic(self, action, filename, data_rate, transfer_time):
        # Add recorded statistics to list
        self.statistics["action"].append(action)
        self.statistics["filename"].append(filename)
        self.statistics["data_rate_kbps"].append(data_rate)
        self.statistics["transfer_time_s"].append(transfer_time)
        self.statistics["timestamp"].append(time.strftime("%Y-%m-%d %H:%M:%S"))

    def save_to_file(self, filename="network_stats.csv"):
        # Save the statistics to a CSV file.
        df = pd.DataFrame(self.statistics)
        df.to_csv(filename, index=False)
        print(f"Statistics saved to {filename}.")

    def get_statistics(self):
        # Return the recorded statistics as a DataFrame.
        return pd.DataFrame(self.statistics)


