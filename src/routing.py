import networkx as nx
import pandas as pd
import osmnx as ox


def routing(G, orders_df, hubs_df):
    print("[4/7] Running Routing...")
    results = []

    road_nodes = [n for n, d in G.nodes(data=True) if d.get('mode') not in ['metro_station', 'waterbus_station']]
    G_road = G.subgraph(road_nodes)

    scenarios = {
        'Road Only': ['road'],
        'Full Multimodal': ['road', 'metro', 'waterbus']
    }

    hub = hubs_df.iloc[0]
    hub_node = ox.distance.nearest_nodes(G_road, X=hub['lon'], Y=hub['lat'])

    for order_idx, order in orders_df.iterrows():
        order_node = ox.distance.nearest_nodes(G_road, X=order['lon'], Y=order['lat'])
        if hub_node == order_node:
            continue

        for scenario_name, allowed_modes in scenarios.items():
            valid_edges = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d.get('mode') in allowed_modes]
            G_sub = G.edge_subgraph(valid_edges)

            try:
                time = nx.shortest_path_length(G_sub, source=hub_node, target=order_node, weight='travel_time')
                path = nx.shortest_path(G_sub, source=hub_node, target=order_node, weight='travel_time')

                # Tính tổng quãng đường và TỔNG CO2 CHI TIẾT THEO TỪNG PHƯƠNG TIỆN
                dist_km = 0
                co2_emit = 0
                for i in range(len(path) - 1):
                    edge_data = G_sub[path[i]][path[i + 1]][0]
                    l_km = edge_data.get('length', 0) / 1000

                    dist_km += l_km
                    # Lấy hệ số CO2 của đúng phương tiện đó (mặc định 0.12 nếu không có)
                    co2_emit += l_km * edge_data.get('co2', 0.12)

                results.append({
                    'order_id': order['order_id'],
                    'scenario': scenario_name,
                    'time': time,
                    'distance': dist_km,
                    'co2': co2_emit  # Đã thêm cột CO2 vào bảng chi tiết
                })
            except nx.NetworkXNoPath:
                pass

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res.to_csv("results/routing_results.csv", index=False)
        print(f"  -> Routing done. Đã tìm đường cho {len(df_res)} đơn.")
    return df_res