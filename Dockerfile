FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# ابتدا فایل‌های مربوط به پکیج‌ها را کپی کن
COPY pyproject.toml pdm.lock ./

# PDM را نصب کن و سپس پکیج‌های پروژه را نصب کن
RUN pip install pdm

RUN pdm install 
# حالا بقیه کدهای برنامه را کپی کن
COPY . /app

# CMD برای اجرای برنامه
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]