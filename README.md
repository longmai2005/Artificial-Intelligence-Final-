# ⚡ Smart Energy AI - Hệ Thống Quản Lý & Dự Báo Năng Lượng Thông Minh

> **Đồ án Kết thúc học phần Trí tuệ Nhân tạo**
> Ứng dụng Web giúp hộ gia đình giám sát tiêu thụ điện, dự báo hóa đơn bằng Machine Learning và tư vấn tiết kiệm năng lượng thông qua Trợ lý ảo AI.

## 🌟 Tính năng Chính

### 1. 🏠 Dành cho Người dùng (User)

* **Real-time Dashboard:** Theo dõi biểu đồ tiêu thụ điện và chi phí ước tính trong 24h tới.
* **AI Forecasting:** Dự báo tải điện chính xác sử dụng thuật toán **LightGBM**.
* **Mô phỏng Thiết bị:** Bật/tắt các thiết bị ảo (Máy lạnh, Đèn, Tivi...) để xem sự thay đổi của hóa đơn.
* **AI Chatbot:** Trợ lý ảo tích hợp **Google Gemini Pro**, trả lời câu hỏi tự nhiên về tiết kiệm điện.
* **Bảo mật:** Đăng ký/Đăng nhập an toàn với xác thực **Email OTP**.

### 2. 🛠 Dành cho Quản trị viên (Admin)

* **System Monitoring:** Theo dõi KPI hệ thống (Tổng User, User Online).
* **Log Viewer:** Xem nhật ký hoạt động hệ thống theo thời gian thực.
* **User Management:** Quản lý danh sách người dùng, xóa tài khoản vi phạm.

---

## 🏗 Kiến trúc Hệ thống (Project Structure)

Dự án được tổ chức theo mô hình **MVC (Model-View-Controller)** cải tiến:

```text
Artificial-Intelligence-Final-/
├── checkpoints/             # Chứa mô hình đã huấn luyện (.pkl)
│   └── best_model_lightgbm.pkl
├── data/                    # Cơ sở dữ liệu dạng JSON & Logs
│   ├── history.json         # Lịch sử dự báo
│   ├── users.json           # Thông tin người dùng (Hashed password)
│   └── system.log           # Nhật ký hệ thống
├── reports/                 # Báo cáo kết quả Model & Data cleaning
├── src/                     # Mã nguồn chính
│   ├── backend/             # Xử lý Logic, Auth, AI Engine
│   ├── components/          # Giao diện (Streamlit UI components)
│   ├── models/              # Huấn luyện & Xử lý dữ liệu (Train/Clean)
│   ├── utils/               # CSS Styling & Helper functions
│   └── app.py               # Main Entry Point
├── requirements.txt         # Các thư viện phụ thuộc
├── test_model.py            # Script kiểm thử Model
└── README.md                # Tài liệu dự án

```

---

## 🚀 Hướng dẫn Cài đặt & Chạy

### 1. Yêu cầu tiên quyết

* Python 3.10 hoặc 3.11
* Git

### 2. Cài đặt

Bước 1: Clone dự án về máy

```bash
git clone https://github.com/longmai2005/Artificial-Intelligence-Final-.git
cd Artificial-Intelligence-Final-

```

Bước 2: Tạo và kích hoạt môi trường ảo (Khuyên dùng)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

```

Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt

```

### 3. Cấu hình Môi trường (.env) (nếu cần thiết)

Tạo file `.env` (hoặc cấu hình trực tiếp trong `src/backend/auth.py` và `ai_engine.py` nếu chạy local demo) để điền API Key:

```ini
GOOGLE_API_KEY=your_gemini_api_key_here
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

```

### 4. Chạy ứng dụng

```bash
streamlit run src/app.py

```

*Truy cập vào đường dẫn: `http://localhost:8501*`*

---

## 📊 Hiệu năng Mô hình (Model Performance)

Chúng tôi đã thử nghiệm các mô hình LSTM, LightGBM và Random Forest. Kết quả cho thấy **LightGBM** tối ưu nhất cho bài toán này.

* **RMSE (Root Mean Squared Error):** *Xem chi tiết trong `reports/model_report.txt*`
* **Training Speed:** Nhanh gấp 5 lần so với LSTM.

---

## 🧪 Quy trình Huấn luyện lại (Retrain)

Nếu bạn có dữ liệu mới và muốn huấn luyện lại mô hình:

1. Đặt file dữ liệu thô vào thư mục `data/`.
2. Chạy script làm sạch dữ liệu:
```bash
python -m src.models.clean_data

```


3. Chạy script huấn luyện:
```bash
python -m src.models.train_build

```


*Mô hình mới sẽ được lưu vào `checkpoints/best_model_lightgbm.pkl`.*

---

## 👨‍💻 Đội ngũ Thực hiện

* **Mai Phước Long** - *23020005*
* **Lê Bảo Khanh** - *23020001*
* **Nguyễn Tiến Dũng** - *23020008*

## 📜 Giấy phép (License)

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

*Made with ❤️ by Group 8*
