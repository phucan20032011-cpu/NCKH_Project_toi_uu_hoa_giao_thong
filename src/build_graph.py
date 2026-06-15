import osmnx as ox
import networkx as nx
import pickle
import math
import pandas as pd

ox.settings.log_console = True


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Bán kính trái đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def add_waterbus_layer(G, df, speed_kmh=20, co2_factor=0.05):
    """Giữ nguyên logic nối tuần tự cho bến sông (Waterbus)"""
    for idx, row in df.iterrows():
        node_id = f"waterbus_{idx}"
        # Khởi tạo Node với thuộc tính tên ga thực tế từ CSV để chuẩn hóa đối chiếu
        G.add_node(node_id, y=row['lat'], x=row['lon'], mode='waterbus_station', station_name=row['name'].strip())

        if idx > 0:
            prev_node = f"waterbus_{idx - 1}"
            dist_km = calculate_distance(row['lat'], row['lon'], df.iloc[idx - 1]['lat'], df.iloc[idx - 1]['lon'])
            time_min = (dist_km / speed_kmh) * 60

            G.add_edge(prev_node, node_id, length=dist_km * 1000, travel_time=time_min, mode='waterbus', co2=co2_factor)
            G.add_edge(node_id, prev_node, length=dist_km * 1000, travel_time=time_min, mode='waterbus', co2=co2_factor)


def add_metro_layer_with_edges(G, metro_df, edges_df, speed_kmh=40, co2_factor=0.02):
    """Logic MỚI: Khởi tạo tất cả ga Metro và nối các ga dựa hoàn toàn vào file HCMC_Metro_Edges.csv"""

    # Bước 1: Thêm toàn bộ các ga (Nodes) vào đồ thị
    # Sử dụng luôn Tên Ga làm ID (Key) hoặc đối chiếu chính xác để tránh thuật toán nối nhầm điểm số thành điểm chữ
    station_coords = {}
    for _, row in metro_df.iterrows():
        station_name = row['name'].strip()
        node_id = f"metro_{station_name}"  # Tạo ID dạng: metro_Bến Thành, metro_Suối Tiên...
        G.add_node(node_id, y=row['lat'], x=row['lon'], mode='metro_station', station_name=station_name)
        station_coords[station_name] = (row['lat'], row['lon'])

    # Bước 2: Duyệt qua file Edges để vẽ các đoạn đường ray nối giữa các ga
    for _, edge in edges_df.iterrows():
        from_st = str(edge['from_station']).strip()
        to_st = str(edge['to_station']).strip()
        line_name = edge['line']

        node_u = f"metro_{from_st}"
        node_v = f"metro_{to_st}"

        # Kiểm tra xem cả 2 ga này có tồn tại trong file tọa độ metro.csv không
        if from_st in station_coords and to_st in station_coords:
            coord_u = station_coords[from_st]
            coord_v = station_coords[to_st]

            # Tính khoảng cách địa lý thực tế giữa 2 ga đan chéo nhau
            dist_km = calculate_distance(coord_u[0], coord_u[1], coord_v[0], coord_v[1])
            time_min = (dist_km / speed_kmh) * 60

            # Tạo liên kết 2 chiều cho đường ray Metro
            G.add_edge(node_u, node_v, length=dist_km * 1000, travel_time=time_min, mode='metro', line=line_name,
                       co2=co2_factor)
            G.add_edge(node_v, node_u, length=dist_km * 1000, travel_time=time_min, mode='metro', line=line_name,
                       co2=co2_factor)
        else:
            # Cảnh báo nếu file Edges định nghĩa sai tên ga so với file danh mục gốc
            print(f"  -> [!] Cảnh báo: Không tìm thấy tọa độ cho liên kết giữa '{from_st}' và '{to_st}'")


def build_graph(metro_df, metro_edges_df, waterbus_df, save_path="results/multimodal_graph.pkl"):
    print("[2/7] Building Multimodal Graph...")

    # 1. Tải Road Graph từ OpenStreetMap (Khu vực Q1)
    places = ["District 1, Ho Chi Minh City, Vietnam"]
    G = ox.graph_from_place(places, network_type='drive')

    # Gán thuộc tính mặc định cho đường bộ
    for u, v, key, data in G.edges(keys=True, data=True):
        length_km = data.get('length', 0) / 1000
        data['travel_time'] = (length_km / 30) * 60  # Vận tốc shipper 30 km/h
        data['mode'] = 'road'
        data['co2'] = 0.12

    # 2. Áp dụng các tầng giao thông công cộng đầu vào công nghệ cao
    add_metro_layer_with_edges(G, metro_df, metro_edges_df, speed_kmh=40, co2_factor=0.02)
    add_waterbus_layer(G, waterbus_df, speed_kmh=20, co2_factor=0.05)

    with open(save_path, 'wb') as f:
        pickle.dump(G, f)
    print("  -> Graph saved completely with multi-line Metro connectivity.")
    return G