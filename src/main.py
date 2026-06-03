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

    metro, waterbus, hubs, orders = load_data()
    if metro is None: return

    graph_path = "results/multimodal_graph.pkl"
    G = None
    if os.path.exists(graph_path):
        try:
            with open(graph_path, 'rb') as f:
                G = pickle.load(f)
            print("[2/7] Graph loaded from cache.")
        except Exception:
            print("[!] Cache lỗi. Tạo lại Graph...")
            os.remove(graph_path)

    if G is None:
        G = build_graph(metro, waterbus, graph_path)

    selected_hubs = select_hub(hubs, orders)
    routing_results = routing(G, orders, selected_hubs)
    evaluation(routing_results)
    simulation()
    print("[7/7] Pipeline Hoàn Thành!")


if __name__ == "__main__":
    main()