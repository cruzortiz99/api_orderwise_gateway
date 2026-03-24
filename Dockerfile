FROM python:3.14-alpine

COPY . /app
WORKDIR /app
RUN  pip install uv --break-system-packages  && \
  uv sync --no-cache --no-dev
EXPOSE 8000
CMD ["uv", "run", "main.py"]
