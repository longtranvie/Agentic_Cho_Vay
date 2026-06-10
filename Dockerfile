# Đóng gói API thẩm định để chạy 1 lệnh — ADR-0020.
#
# Build:   docker build -t loan-agent .
# Chạy:    docker run -p 8000:8000 -e LOAN_API_KEY=<khóa> loan-agent
# Tài liệu API tự sinh: http://localhost:8000/docs
#
# ⚠️ Sau proxy doanh nghiệp (MITM): bước pip cần CA bundle nội bộ. Ví dụ truyền qua
#    build-arg + pip config, hoặc COPY corp-ca.pem và đặt PIP_CERT/REQUESTS_CA_BUNDLE.
#    Không nướng .env / key vào image — xem .dockerignore.

FROM python:3.11-slim

WORKDIR /app

# Cài deps trước để tận dụng cache layer (chỉ cài lại khi requirements đổi).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Mã nguồn + cấu hình + dữ liệu chính sách (RAG cần data/policies).
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

ENV PYTHONPATH=/app/src \
    LOAN_LLM_PROVIDER=mock \
    LOAN_RAG_BACKEND=keyword

EXPOSE 8000

# Production: đặt LOAN_API_KEY (bật auth), LOAN_LLM_PROVIDER=openai + OPENAI_API_KEY,
# và các biến CA nếu chạy sau proxy.
CMD ["uvicorn", "loan_agent.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
