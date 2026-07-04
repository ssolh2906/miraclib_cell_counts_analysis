FROM python:3.12-slim

# HF Spaces runs the container as user 1000 — create it before any COPY.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
