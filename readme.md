# TÀI LIỆU KIẾN TRÚC HỆ THỐNG
**Dự án:** Multimodal Urban Freight Transportation (Logistics Đa phương thức đô thị tại TP.HCM)
**Vai trò:** Hướng dẫn luồng chạy, cấu trúc mã nguồn và thuật toán áp dụng.

---

## 1. Cấu trúc thư mục (Directory Structure)
Hệ thống được thiết kế theo dạng module (Decoupled Architecture), chia tách rõ ràng giữa Dữ liệu, Mã nguồn và Kết quả đầu ra:

```text
project/
├── data/                          # Chứa dữ liệu đầu vào (Input)
│   ├── metro.csv                  # Danh sách 14 ga Metro
│   ├── waterbus.csv               # Danh sách 7 bến Waterbus
│   ├── hub_candidates.csv         # Danh sách 15 Hub ứng viên
│   └── orders.csv                 # Danh sách 300 đơn hàng giả lập
├── results/                       # Chứa kết quả tự động sinh ra (Output)
│   ├── multimodal_graph.pkl       # File Cache lưu bản đồ mạng lưới (để chạy nhanh)
│   ├── selected_hubs.csv          # Danh sách 5 Hub được chọn tối ưu nhất
│   ├── routing_results.csv        # Kết quả tìm đường (Thời gian, quãng đường cho từng đơn)
│   ├── summary_results.xlsx       # File Excel KPI (Trung bình thời gian, CO2)
│   └── simulation_log.txt         # Log giả lập tracking đơn hàng
└── src/                           # Chứa mã nguồn Python
    ├── load_data.py               # Module 1: Đọc và làm sạch dữ liệu
    ├── build_graph.py             # Module 2: Tải và vẽ bản đồ đa phương thức
    ├── select_hub.py              # Module 3: Chạy thuật toán chọn Hub
    ├── routing.py                 # Module 4: Chạy thuật toán tìm đường (Dijkstra)
    ├── evaluation.py              # Module 5: Đánh giá KPI và tính CO2
    ├── simulation.py              # Module 6: Sinh log sự kiện
    └── main.py                    # File thực thi điều phối toàn bộ Pipeline