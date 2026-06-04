import pandas as pd


def evaluation(routing_results_df):
    print("[5/7] Evaluating KPIs...")

    if routing_results_df is None or routing_results_df.empty:
        print("  -> [!] Bỏ qua đánh giá KPI vì không có dữ liệu Routing.")
        return None

    # Gom nhóm và tính tổng/trung bình các KPI cốt lõi
    summary = routing_results_df.groupby('scenario').agg(
        avg_time=('time', 'mean'),  # Thời gian trung bình
        total_distance=('distance', 'sum'),  # Tổng quãng đường
        CO2_emissions=('co2', 'sum')  # Tổng phát thải CO2 (Chính xác theo phương tiện)
    ).reset_index()

    # Lưu ra CSV để bạn có thể xem trực tiếp ngay trong PyCharm
    summary.to_csv("results/summary_results.csv", index=False)
    print("  -> KPIs calculated. Saved to results/summary_results.csv")

    return summary