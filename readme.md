# TÀI LIỆU KIẾN TRÚC HỆ THỐNG
**Dự án:** Multimodal Urban Freight Transportation (Logistics Đa phương thức đô thị tại TP.HCM)
**Mục tiêu:** Hướng dẫn luồng chạy, cấu trúc mã nguồn, các thuật toán áp dụng và cách đọc hiểu kết quả (Output).

---

## 1. Cấu trúc thư mục (Directory Structure)
Hệ thống được thiết kế theo dạng module (Decoupled Architecture), chia tách rõ ràng giữa Dữ liệu đầu vào, Mã nguồn xử lý và Kết quả đầu ra. 

    project/
    ├── data/                          # Chứa dữ liệu đầu vào (Input do Người B cung cấp)
    │   ├── metro.csv                  # Danh sách 14 ga Metro
    │   ├── waterbus.csv               # Danh sách 7 bến Waterbus
    │   ├── hub_candidates.csv         # Danh sách 15 Hub ứng viên
    │   └── orders.csv                 # Danh sách 300 đơn hàng giả lập
    ├── results/                       # Chứa kết quả tự động sinh ra (Output)
    │   ├── multimodal_graph.pkl       # File Cache lưu bản đồ mạng lưới (để chạy nhanh)
    │   ├── selected_hubs.csv          # Danh sách 5 Hub được chọn tối ưu nhất
    │   ├── routing_results.csv        # Kết quả tìm đường (Thời gian, quãng đường cho từng đơn)
    │   ├── summary_results.xlsx       # File Excel KPI (Trung bình thời gian, CO2)
    │   └── simulation_log.txt         # Log giả lập tracking mô phỏng đơn hàng
    └── src/                           # Chứa mã nguồn Python
        ├── load_data.py               # Module 1: Đọc và làm sạch dữ liệu
        ├── build_graph.py             # Module 2: Tải và xây dựng đồ thị đa phương thức
        ├── select_hub.py              # Module 3: Chạy thuật toán chọn Hub (Greedy)
        ├── routing.py                 # Module 4: Chạy thuật toán tìm đường (Dijkstra)
        ├── evaluation.py              # Module 5: Đánh giá KPI và tính toán phát thải CO2
        ├── simulation.py              # Module 6: Sinh log sự kiện mô phỏng
        └── main.py                    # File thực thi điều phối toàn bộ Pipeline

---

## 2. Luồng chạy & Logic toàn bộ hệ thống (System Flow)
Trái tim của dự án nằm ở file `main.py`. Tệp này điều phối một **Pipeline (Luồng xử lý dữ liệu)** đi qua 7 bước tuần tự:

1. **Load Data (`load_data.py`):** Đọc các file `.csv` từ thư mục `data/`. Tự động quét và làm sạch các dữ liệu lỗi (xóa khoảng trắng thừa, xóa chữ cái lọt vào cột tọa độ).
2. **Build Graph (`build_graph.py`):** Kết nối qua API với máy chủ OpenStreetMap để tải bản đồ mạng lưới đường bộ thực tế của khu vực. Sau đó, hệ thống "vẽ" thêm các tuyến Metro và tuyến Waterbus đè lên bản đồ này để tạo thành một Đồ thị Đa phương thức (Multimodal Graph).
3. **Hub Selection (`select_hub.py`):** Quét 15 vị trí Hub ứng viên, tính toán khoảng cách đến 300 khách hàng và chốt chọn ra 5 Hub tối ưu nhất phục vụ cho tập khách hàng đó.
4. **Routing (`routing.py`):** Ánh xạ (Map) vị trí Hub và tọa độ khách hàng vào các nút giao thông thực tế trên bản đồ. Chạy xe giao hàng ảo qua các kịch bản: Giao hoàn toàn bằng xe máy (Road Only) và Giao đa phương thức (Multimodal).
5. **Evaluation (`evaluation.py`):** Lấy kết quả tìm đường từ bước 4, gom nhóm lại (groupby), tính trung bình thời gian giao hàng, tổng quãng đường và nhân với hệ số phát thải để ra lượng CO₂.
6. **Simulation (`simulation.py`):** In ra một file log text giả lập các sự kiện theo thời gian thực (tracking tiến trình của một đơn hàng).
7. **Export:** Xuất và lưu toàn bộ kết quả ra thư mục `results/`.

---

## 3. Các thư viện cốt lõi (Core Libraries)
Hệ thống sử dụng các thư viện mạnh mẽ của Python trong lĩnh vực Data Science và Hệ thống thông tin địa lý (GIS):

* **`pandas`:** Đọc/ghi file CSV, Excel và tính toán, thao tác bảng biểu siêu tốc.
* **`osmnx`:** Giao tiếp với OpenStreetMap để tự động tải mạng lưới đường bộ (bao gồm ngã tư, chiều dài đoạn đường, tốc độ giới hạn).
* **`networkx`:** Quản lý đồ thị (Graph). Lưu trữ mạng lưới thành các Nút (Node) và Cạnh (Edge), cung cấp các hàm nền tảng để chạy thuật toán tìm đường.
* **`scipy`:** Dùng hàm `cdist` để tính toán ma trận khoảng cách giữa hàng trăm tọa độ gần như tức thì.
* **`scikit-learn`:** Cung cấp thuật toán *Cây không gian (Spatial Indexing)* giúp tìm kiếm các điểm lân cận trên bản đồ siêu tốc.

---

## 4. Các thuật toán & Kỹ thuật được áp dụng (Algorithms & Techniques)

| Tên thuật toán / Kỹ thuật | Nơi áp dụng | Mục đích và Cách hoạt động |
| :--- | :--- | :--- |
| **1. Biểu thức chính quy (Regex)** | `load_data.py` | **Làm sạch dữ liệu (Data Cleaning):** Tự động phát hiện và gọt bỏ các ký tự chữ cái vô tình lọt vào cột tọa độ số (VD: gõ nhầm chữ "Tren"), đảm bảo hệ thống tính toán toán học không bị gián đoạn. |
| **2. Công thức Haversine** | `build_graph.py` | **Tính khoảng cách địa lý:** Vì Trái Đất có hình cầu, công thức này dùng lượng giác (sin, cos) để đo chiều dài (km) uốn cong bề mặt giữa các ga tàu, từ đó suy ra thời gian di chuyển. |
| **3. Thuật toán Tham lam (Greedy)** | `select_hub.py` | **Tối ưu hóa vị trí (Facility Location):** Ở mỗi vòng lặp, thuật toán "tham lam" chọn ra 1 Hub giúp làm giảm tổng khoảng cách giao của 300 đơn xuống thấp nhất. Lặp 5 lần để chốt 5 Hub tối ưu cục bộ. |
| **4. Tìm kiếm lân cận (K-NN)** | `routing.py` | **Ánh xạ không gian (Map Matching):** Khi có tọa độ (Lat/Lon) của khách hàng, thuật toán quét không gian để tìm "nút giao thông đường bộ" gần nhất với họ để gán làm điểm kết thúc cho shipper. |
| **5. Thuật toán Dijkstra** | `routing.py` | **Tìm đường đi ngắn nhất:** Quét qua mạng lưới đường bộ + Metro + Waterbus, thuật toán loang ra và ưu tiên vạch ra lộ trình có **tổng thời gian di chuyển thấp nhất** từ Hub đến khách hàng. |
| **6. Lọc đồ thị con (Subgraph Filtering)** | `routing.py` | **Xử lý kịch bản giao thông:** Thay vì tạo nhiều bản đồ, thuật toán dùng chung 1 đồ thị gốc. Với kịch bản "Chỉ đường bộ", nó tạm "ẩn" các cạnh Metro/Waterbus đi, ép Dijkstra chỉ tìm đường trên mặt đường bộ. |

---

## 5. Quá trình sinh Output & Cách đọc hiểu kết quả

Toàn bộ minh chứng số liệu của đề tài nằm trong thư mục `results/`:

1. **`multimodal_graph.pkl` (File hệ thống)**
   * *Ý nghĩa:* File nhị phân (Cache) lưu toàn bộ mạng lưới bản đồ. Lần chạy sau hệ thống sẽ nạp file này thay vì tải lại từ đầu để tiết kiệm tối đa thời gian chờ đợi.
2. **`selected_hubs.csv`**
   * *Ý nghĩa:* Danh sách 5 kho trung chuyển (Micro-hub) được hệ thống chọn ra là vị trí tối ưu nhất để đặt cơ sở.
3. **`routing_results.csv`**
   * *Ý nghĩa:* Bảng chi tiết cho từng đơn hàng (gồm mã đơn, kịch bản, số phút giao và số km quãng đường). Cung cấp dữ liệu thô để vẽ biểu đồ chi tiết nếu cần.
4. **`summary_results.xlsx` (File minh chứng quan trọng nhất)**
   * *Ý nghĩa:* File báo cáo KPI tổng. Cung cấp 3 chỉ số cốt lõi: `avg_time` (Thời gian giao trung bình), `total_distance` (Tổng quãng đường) và `CO2_emissions` (Khí thải CO₂). 
   * *Giá trị cốt lõi:* Dùng để chứng minh kịch bản Đa phương thức (Full Multimodal) mang lại thời gian và mức phát thải **THẤP HƠN** so với kịch bản truyền thống (Road Only).
5. **`simulation_log.txt`**
   * *Ý nghĩa:* File text giả lập dòng thời gian cập nhật trạng thái các bước giao hàng (Mô phỏng hệ thống Tracking App dành cho khách hàng).

---

## 6. Hướng dẫn chạy và bảo trì hệ thống

* **Chạy bình thường:** Mở Terminal/Command Prompt trên PyCharm, đảm bảo đã cài đặt các thư viện (`pip install pandas numpy scipy networkx osmnx openpyxl scikit-learn`), sau đó chạy lệnh: `python src/main.py`.
* **Khi có dữ liệu mới:** Chỉ cần ghi đè file CSV mới vào thư mục `data/` (ví dụ: thay đổi tọa độ khách hàng, thêm ứng viên Hub), hệ thống sẽ tự động đọc và tính toán lại từ đầu.
* **Khi muốn mở rộng bản đồ (Ví dụ thêm Quận Bình Thạnh, TP. Thủ Đức):** Sửa tên khu vực trong file `src/build_graph.py` (biến `places`). Sau đó **BẮT BUỘC phải xóa file `results/multimodal_graph.pkl`** cũ đi để hệ thống kết nối lại với mạng và tải bản đồ mới lớn hơn.