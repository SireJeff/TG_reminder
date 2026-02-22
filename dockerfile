# Use an official lightweight Python image.
FROM python:3.11-slim

# Install any system dependencies (e.g. gcc) if needed.
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container.
COPY . .

# Run the bot.
CMD ["python", "src/bot.py"]
