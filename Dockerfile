FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY pyproject.toml pdm.lock ./
RUN pip install pdm
RUN pip install uvicorn
RUN pip install pytest
RUN pdm install
COPY . /app
CMD ["pdm", "run", "uvicorn", "app.main:app", "--reload"]