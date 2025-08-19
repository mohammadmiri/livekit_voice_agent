FROM python:3.12-slim

# Install system packages (adjust list as needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libapparmor-dev \
    libdbus-1-dev \
    python3-apt \
    && rm -rf /var/lib/apt/lists/*

RUN python3.12 -m ensurepip --upgrade

WORKDIR /app

# Copy Python dependencies file
COPY requirements.txt .

# Install only Python packages
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD ["python", "agent.py", "connect", "--room", "default-room", "--participant-identity", "voice-agent"]
# CMD ["python", "agent.py", "start"]
CMD ["python", "print", "hello"]