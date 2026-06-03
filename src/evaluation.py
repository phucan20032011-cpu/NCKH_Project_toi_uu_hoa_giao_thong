import pandas as pd

def evaluation(routing_results_df):
    print("[5/7] Evaluating KPIs...")

    # KIỂM TRA AN TOÀN TRƯỚC KHI TÍNH TOÁN
    if routing_results_df is None or routing_results_df.empty:
        print("  -> [!] Bỏ qua đánh giá KPI vì không có dữ liệu Routing (Danh sách đường đi trống).")
        return None

    # Tính toán tổng hợp theo từng kịch bản
    summary = routing_results_df.groupby('scenario').agg(
        avg_time=('time', 'mean'),
        total_distance=('distance', 'sum')
    ).reset_index()

    # Tính phát thải CO2
    summary['CO2_emissions'] = summary['total_distance'] * 0.12

    summary.to_excel("results/summary_results.xlsx", index=False)
    print("  -> KPIs calculated. Saved to results/summary_results.xlsx")
    return summary