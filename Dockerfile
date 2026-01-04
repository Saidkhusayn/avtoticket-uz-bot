# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Set environment variable for bot token (you can modify as needed)
ENV TELEGRAM_API_TOKEN=your_telegram_api_token_here

# Expose any necessary ports (default for Telegram bot is not used, but here for standard practice)
EXPOSE 5000

# Command to run the bot
CMD ["python", "main.py"]
