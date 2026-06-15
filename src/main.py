import os
import pickle
from load_data import load_data
from build_graph import build_graph
from select_hub import select_hub
from routing import routing
from evaluation import evaluation
from simulation import simulation


def main():
    os.makedirs("results", exist_ok=True)

    # Cập nhật nhận thêm biến dữ liệu metro_edges từ load_data()
    metro, metro_edges, waterbus, hubs, orders = load_data()
    if metro is None:
        print("[!] Lỗi nạp dữ liệu. Kết thúc Pipeline.")
        return

    graph_path = "results/multimodal_graph.pkl"
    G = None
    if os.path.exists(graph_path):
        try:
            with open(graph_path, 'rb') as f:
                G = pickle.load(f)
            print("[2/7] Graph loaded from cache.")
        except Exception:
            print("[!] Cache lỗi hoặc cấu trúc cũ không khớp. Tiến hành tạo lại Graph...")
            os.remove(graph_path)

    if G is None:
        # Cập nhật truyền đồng bộ metro_edges vào để xây dựng đồ thị
        G = build_graph(metro, metro_edges, waterbus, graph_path)

    selected_hubs = select_hub(hubs, orders)
    routing_results = routing(G, orders, selected_hubs)
    evaluation(routing_results)
    simulation()
    print("[7/7] Pipeline Hoàn Thành!")


if __name__ == "__main__":
    main()