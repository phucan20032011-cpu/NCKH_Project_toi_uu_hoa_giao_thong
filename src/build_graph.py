import osmnx as ox
import networkx as nx
import pickle
import math

ox.settings.log_console = True


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Bán kính trái đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def add_transit_layer(G, df, mode_name, speed_kmh, co2_factor):
    """Hàm chung để thêm Metro hoặc Waterbus vào đồ thị"""
    for idx, row in df.iterrows():
        node_id = f"{mode_name}_{idx}"
        G.add_node(node_id, y=row['lat'], x=row['lon'], mode=f'{mode_name}_station')

        if idx > 0:
            prev_node = f"{mode_name}_{idx - 1}"
            dist_km = calculate_distance(row['lat'], row['lon'], df.iloc[idx - 1]['lat'], df.iloc[idx - 1]['lon'])
            time_min = (dist_km / speed_kmh) * 60

            # Cạnh hai chiều
            G.add_edge(prev_node, node_id, length=dist_km * 1000, travel_time=time_min, mode=mode_name, co2=co2_factor)
            G.add_edge(node_id, prev_node, length=dist_km * 1000, travel_time=time_min, mode=mode_name, co2=co2_factor)


def build_graph(metro_df, waterbus_df, save_path="results/multimodal_graph.pkl"):
    print("[2/7] Building Multimodal Graph...")

    # 1. Tải Road Graph (Chỉ lấy mạng lưới Quận 1 để test chạy mượt trước)
    places = ["District 1, Ho Chi Minh City, Vietnam"]
    G = ox.graph_from_place(places, network_type='drive')

    # Gán thuộc tính đường bộ
    for u, v, key, data in G.edges(keys=True, data=True):
        length_km = data.get('length', 0) / 1000
        data['travel_time'] = (length_km / 30) * 60  # 30 km/h
        data['mode'] = 'road'
        data['co2'] = 0.12

        # 2. Thêm Metro (40km/h) & Waterbus (20km/h)
    add_transit_layer(G, metro_df, 'metro', speed_kmh=40, co2_factor=0.02)
    add_transit_layer(G, waterbus_df, 'waterbus', speed_kmh=20, co2_factor=0.05)

    # (Tương lai: Có thể code thêm logic nối Transfer 500m tại đây)

    with open(save_path, 'wb') as f:
        pickle.dump(G, f)
    print("  -> Graph saved.")
    return G
