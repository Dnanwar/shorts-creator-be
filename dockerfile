FROM python:3.11-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    libu2f-udev \
    fonts-liberation \
    libappindicator3-1 \
    libdbus-glib-1-2 \
    libcurl4 \
    libexpat1 \
    libpango-1.0-0 \
    libxrandr2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxext6 \
    libxcb1 \
    libx11-6 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libnspr4 \
    libatspi2.0-0 \
    libvulkan1 && \
    rm -rf /var/lib/apt/lists/*

# Add Brave's official GPG key and repository
RUN curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" > /etc/apt/sources.list.d/brave-browser-release.list

# Install Brave Browser v1.52.130
RUN apt-get update && \
    apt-get install -y brave-browser=1.52.130 && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver 114.0.5735.90
RUN wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set Brave binary path for Selenium
ENV BRAVE_BIN=/usr/bin/brave-browser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
