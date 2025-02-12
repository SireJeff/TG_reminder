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

# (Optional) Expose a port if your project uses one.
# EXPOSE 5000

# Run the bot.
CMD ["python", "bot.py"]
