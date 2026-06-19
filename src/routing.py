import networkx as nx
import osmnx as ox
import pandas as pd


def get_nearest_hub(order_lat, order_lon, hubs_df):
    best_idx = hubs_df.index[0]
    min_dist = float("inf")
    for idx, hub in hubs_df.iterrows():
        # Khoảng cách Euclid bình phương (nhanh và đủ chính xác cho phạm vi Q1)
        dist = (hub["lat"] - order_lat) ** 2 + (hub["lon"] - order_lon) ** 2
        if dist < min_dist:
            min_dist = dist
            best_idx = idx
    return hubs_df.loc[best_idx]


def get_best_edge_data(G_sub, u, v, traffic_condition):
    edges = G_sub[u][v]
    best_key = list(edges.keys())[0]
    min_w = float("inf")
    for key, data in edges.items():
        t = data.get("travel_time", 0)
        if traffic_condition == "Peak" and data.get("mode") == "road":
            w = t * 2.5
        else:
            w = t
        if w < min_w:
            min_w = w
            best_key = key
    return edges[best_key]


def routing(G, orders_df, hubs_df):
    print("[4/7] Running Routing across Traffic Conditions & Scenarios...")
    results = []

    # Lấy các nút giao thông đường bộ để tìm node gần nhất cho Hub/Order
    road_nodes = [
        n
        for n, d in G.nodes(data=True)
        if d.get("mode") not in ["metro_station", "waterbus_station"]
    ]
    G_road = G.subgraph(road_nodes)

    traffic_conditions = ["Off-Peak", "Peak"]
    scenarios = {
        "Road Only": ["road"],
        "Road + Metro": ["road", "metro", "transfer"],
        "Road + Waterbus": ["road", "waterbus", "transfer"],
        "Full Multimodal": ["road", "metro", "waterbus", "transfer"],
    }

    # Ánh xạ các Node cho các Hub được chọn để tăng tốc tìm kiếm
    hub_nodes = {}
    for _, hub in hubs_df.iterrows():
        hub_nodes[hub["hub_id"]] = ox.distance.nearest_nodes(
            G_road, X=hub["lon"], Y=hub["lat"]
        )

    for order_idx, order in orders_df.iterrows():
        # 1. Tìm Hub tối ưu gần nhất cho đơn hàng này
        nearest_hub = get_nearest_hub(order["lat"], order["lon"], hubs_df)
        hub_node = hub_nodes[nearest_hub["hub_id"]]

        # 2. Tìm Node đường bộ gần nhất với khách nhận
        order_node = ox.distance.nearest_nodes(
            G_road, X=order["lon"], Y=order["lat"]
        )

        if hub_node == order_node:
            continue

        for traffic in traffic_conditions:
            # Hàm tính trọng số thời gian di chuyển động theo tình trạng giao thông
            def get_weight(u, v, edge_dict):
                min_w = float("inf")
                for key, d in edge_dict.items():
                    t = d.get("travel_time", 0)
                    if traffic == "Peak" and d.get("mode") == "road":
                        w = t * 2.5
                    else:
                        w = t
                    if w < min_w:
                        min_w = w
                return min_w

            for scenario_name, allowed_modes in scenarios.items():
                # Lọc các cạnh hợp lệ thuộc kịch bản
                valid_edges = []
                for u, v, k, d in G.edges(keys=True, data=True):
                    mode = d.get("mode")
                    if mode == "transfer":
                        transfer_type = d.get("transfer_type")
                        if (
                            scenario_name == "Road + Metro"
                            and transfer_type != "metro"
                        ):
                            continue
                        if (
                            scenario_name == "Road + Waterbus"
                            and transfer_type != "waterbus"
                        ):
                            continue
                    if mode in allowed_modes:
                        valid_edges.append((u, v, k))

                G_sub = G.edge_subgraph(valid_edges)

                try:
                    # Dijkstra tìm đường đi nhanh nhất
                    path = nx.shortest_path(
                        G_sub,
                        source=hub_node,
                        target=order_node,
                        weight=get_weight,
                    )

                    dist_km = 0
                    time_min = 0
                    co2_emit = 0
                    cost_vnd = 0

                    for i in range(len(path) - 1):
                        edge_data = get_best_edge_data(
                            G_sub, path[i], path[i + 1], traffic
                        )
                        l_km = edge_data.get("length", 0) / 1000
                        mode = edge_data.get("mode", "road")

                        # Cộng dồn khoảng cách
                        dist_km += l_km

                        # Cộng dồn thời gian di chuyển (tính thêm ùn tắc)
                        t_edge = edge_data.get("travel_time", 0)
                        if traffic == "Peak" and mode == "road":
                            t_edge *= 2.5
                        time_min += t_edge

                        # Cộng dồn khí thải CO2
                        co2_emit += l_km * edge_data.get("co2", 0.12)

                        # Cộng dồn chi phí tiền tệ
                        if mode == "road":
                            cost_vnd += l_km * 3000.0  # 3,000 VND / km xe máy
                        elif mode == "transfer":
                            cost_vnd += edge_data.get(
                                "cost", 7500.0
                            )  # Phí vé xe bus/metro

                    results.append(
                        {
                            "order_id": order["order_id"],
                            "hub_id": nearest_hub["hub_id"],
                            "traffic_condition": traffic,
                            "scenario": scenario_name,
                            "time": time_min,
                            "distance": dist_km,
                            "cost": cost_vnd,
                            "co2": co2_emit,
                        }
                    )
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    pass

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res.to_csv("results/routing_results.csv", index=False)
        print(f"  -> Routing completed. Saved routes for {len(df_res)} cases.")
    return df_res