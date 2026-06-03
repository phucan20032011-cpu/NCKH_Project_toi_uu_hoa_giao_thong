import networkx as nx
import pandas as pd
import osmnx as ox


def routing(G, orders_df, hubs_df):
    print("[4/7] Running Routing...")
    results = []

    # BƯỚC 1: Lọc riêng các node đường bộ (Tránh chọn nhầm nhà ga chưa được kết nối)
    road_nodes = [n for n, d in G.nodes(data=True) if d.get('mode') not in ['metro_station', 'waterbus_station']]
    G_road = G.subgraph(road_nodes)

    scenarios = {
        'Road Only': ['road'],
        'Full Multimodal': ['road', 'metro', 'waterbus']
    }

    # BƯỚC 2: Chọn Hub số 1 làm điểm xuất phát và tìm node đường bộ gần Hub nhất
    hub = hubs_df.iloc[0]
    hub_node = ox.distance.nearest_nodes(G_road, X=hub['lon'], Y=hub['lat'])

    # BƯỚC 3: Chạy thuật toán giao 300 đơn hàng
    for order_idx, order in orders_df.iterrows():
        # Tìm node đường bộ gần với khách hàng nhất
        order_node = ox.distance.nearest_nodes(G_road, X=order['lon'], Y=order['lat'])

        # Bỏ qua nếu điểm giao trùng với Hub
        if hub_node == order_node:
            continue

        for scenario_name, allowed_modes in scenarios.items():
            valid_edges = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d.get('mode') in allowed_modes]
            G_sub = G.edge_subgraph(valid_edges)

            try:
                # Thuật toán Dijkstra
                time = nx.shortest_path_length(G_sub, source=hub_node, target=order_node, weight='travel_time')
                path = nx.shortest_path(G_sub, source=hub_node, target=order_node, weight='travel_time')

                dist_m = sum([G_sub[path[i]][path[i + 1]][0].get('length', 0) for i in range(len(path) - 1)])

                results.append({
                    'order_id': order['order_id'],
                    'scenario': scenario_name,
                    'time': time,
                    'distance': dist_m / 1000  # Đổi ra km
                })
            except nx.NetworkXNoPath:
                pass  # Không tìm được đường thì bỏ qua kịch bản này

    # BƯỚC 4: Lưu kết quả
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res.to_csv("results/routing_results.csv", index=False)
        print(f"  -> Routing done. Đã tìm được đường đi cho {len(df_res)} kịch bản/đơn hàng.")
    else:
        print("  -> [Cảnh báo] Không tìm thấy đường đi nào!")

    return df_res