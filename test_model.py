import joblib
import os

model_path = 'checkpoints/best_model_random_forest.pkl'

if os.path.exists(model_path):
    print("✅ File tồn tại!")
    try:
        model = joblib.load(model_path)
        print(f"✅ Kiểu dữ liệu model: {type(model)}")
        print("🚀 Model đã sẵn sàng để dự báo!")
    except Exception as e:
        print(f"❌ File hỏng hoặc lỗi load: {e}")
else:
    print("❌ Không tìm thấy file model. Hãy chạy train_build.py trước!")