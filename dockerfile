FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Copy real files instead of symlink
RUN rm src/deps/common_avito_utils
RUN rm -rf src/deps/common_avito_utils_tmp

COPY src/deps/common_avito_utils_tmp src/deps/common_avito_utils

CMD ["python3", "main.py"]