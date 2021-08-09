FROM python:3.9.6-slim
ENV ISTIO_QUIT_API=http://localhost:15020
ENV ENVOY_ADMIN_API=http://localhost:15000
COPY --from=redboxoss/scuttle:latest /scuttle /bin/scuttle
COPY . /app
RUN cd /app && pip install -e . && pip install flask fastapi uvicorn
ENTRYPOINT ["scuttle", "python", "/app/main.py"]
