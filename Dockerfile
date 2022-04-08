FROM python:3.11.0a7-slim
ENV ISTIO_QUIT_API=http://localhost:15020
ENV ENVOY_ADMIN_API=http://localhost:15000
COPY --from=redboxoss/scuttle:latest /scuttle /bin/scuttle
COPY . /app
RUN cd /app\
    && pip install -e .\
    && pip install flask fastapi uvicorn typing\
    && echo "default:x:1001:0:Default Application User:/app:/sbin/nologin" >> /etc/passwd
USER default
WORKDIR /app
ENTRYPOINT ["scuttle", "python", "/app/main.py"]
