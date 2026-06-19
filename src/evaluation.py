import pandas as pd

def evaluation(routing_results_df):
    print("[5/7] Evaluating KPIs across Scenarios...")

    if routing_results_df is None or routing_results_df.empty:
        print("  -> [!] Bỏ qua đánh giá KPI vì không có dữ liệu Routing.")
        return None

        # Gom nhóm theo cả tình trạng giao thông (traffic_condition) và kịch bản di chuyển (scenario)
    summary = routing_results_df.groupby(['traffic_condition', 'scenario']).agg(
        avg_time_min=('time', 'mean'),             # Thời gian giao trung bình (phút)
        total_distance_km=('distance', 'sum'),      # Tổng quãng đường (km)
        avg_distance_km=('distance', 'mean'),       # Quãng đường trung bình (km)
        total_cost_vnd=('cost', 'sum'),             # Tổng chi phí vận chuyển (VND)
        avg_cost_vnd=('cost', 'mean'),              # Chi phí trung bình mỗi đơn (VND)
        total_co2_kg=('co2', 'sum'),                # Tổng phát thải CO2 (kg)
        avg_co2_kg=('co2', 'mean'),                 # Phát thải trung bình mỗi đơn (kg)
        delivery_count=('order_id', 'count')        # Số lượng đơn hoàn thành tìm đường
    ).reset_index()
    # Làm tròn số liệu để báo cáo đẹp mắt
    for col in summary.columns:
        if summary[col].dtype == 'float64':
            summary[col] = summary[col].round(2)

    # Lưu ra file CSV
    summary.to_csv("results/summary_results.csv", index=False)
    print("  -> KPIs calculated. Saved to results/summary_results.csv")

    # Lưu ra file Excel báo cáo phân tích KPI đa chiều chuyên sâu
    try:
        summary.to_excel("results/summary_results.xlsx", index=False, sheet_name="KPIs Multimodal")
        print("  -> Extended KPI report saved to results/summary_results.xlsx")
    except Exception as e:
        print(f"  -> [!] Cảnh báo: Không thể ghi file Excel: {e}")

    return summary