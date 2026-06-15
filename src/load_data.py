import pandas as pd
import os


def clean_dataframe(df):
    # 1. Xóa khoảng trắng thừa ở đầu/cuối tên cột và đổi thành chữ thường
    df.columns = df.columns.str.strip().str.lower()

    # Đổi tên cột nếu bị viết là 'lng' hoặc 'long'
    df.rename(columns={'lng': 'lon', 'long': 'lon'}, inplace=True)

    # 2. Xóa các chữ cái lạc vào cột số (Ví dụ chữ "Tren " trong tọa độ)
    if 'lat' in df.columns:
        df['lat'] = df['lat'].astype(str).str.replace(r'[a-zA-Z\s]', '', regex=True).astype(float)
    if 'lon' in df.columns:
        df['lon'] = df['lon'].astype(str).str.replace(r'[a-zA-Z\s]', '', regex=True).astype(float)

    return df


def load_data(data_dir="data"):
    print("[1/7] Loading and cleaning data...")
    try:
        metro = pd.read_csv(os.path.join(data_dir, "metro.csv"))
        waterbus = pd.read_csv(os.path.join(data_dir, "waterbus.csv"))
        hubs = pd.read_csv(os.path.join(data_dir, "hub_candidates.csv"))
        orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))

        # Đọc thêm file danh sách cạnh nối của Metro
        metro_edges = pd.read_csv(os.path.join(data_dir, "HCMC_Metro_Edges.csv"))

        # Áp dụng Data Cleaning
        metro = clean_dataframe(metro)
        waterbus = clean_dataframe(waterbus)
        hubs = clean_dataframe(hubs)
        orders = clean_dataframe(orders)
        metro_edges = clean_dataframe(metro_edges)  # Làm sạch tiêu đề cột của file edges

        print(
            f"  -> Loaded: {len(metro)} Metro Stations, {len(metro_edges)} Metro Edges, {len(waterbus)} Waterbus, {len(hubs)} Hubs, {len(orders)} Orders.")
        return metro, metro_edges, waterbus, hubs, orders
    except Exception as e:
        print(f"Lỗi khi load dữ liệu: {e}")
        return None, None, None, None, None