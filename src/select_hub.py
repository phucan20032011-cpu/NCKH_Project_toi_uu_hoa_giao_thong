import pandas as pd
from scipy.spatial import distance
import numpy as np


def select_hub(hubs_df, orders_df, num_hubs=5):
    print("[3/7] Selecting Optimal Hubs...")
    hubs_coords = hubs_df[['lat', 'lon']].values
    orders_coords = orders_df[['lat', 'lon']].values

    dist_matrix = distance.cdist(orders_coords, hubs_coords, 'euclidean')

    selected_indices = []
    for _ in range(num_hubs):
        best_hub = -1
        min_total_dist = float('inf')

        for i in range(len(hubs_df)):
            if i in selected_indices: continue
            temp_selected = selected_indices + [i]
            total_dist = np.sum(np.min(dist_matrix[:, temp_selected], axis=1))
            if total_dist < min_total_dist:
                min_total_dist, best_hub = total_dist, i

        selected_indices.append(best_hub)

    selected_hubs = hubs_df.iloc[selected_indices].copy()
    selected_hubs.to_csv("results/selected_hubs.csv", index=False)
    print("  -> Selected Hubs saved.")
    return selected_hubs