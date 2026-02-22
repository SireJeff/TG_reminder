# Remindino

**Remindino** is a powerful and versatile Telegram bot designed to help you organize your life. It features task management, goal tracking, reminders, countdowns, weekly scheduling, and much more. Built with Python and Telebot, it's easy to deploy and customize.

## Features

-   **Task Management**: Add, track, and complete tasks with optional due dates.
-   **Goal Tracking**: Set goals with daily, weekly, monthly, seasonal, or yearly check-ins.
-   **Reminders**: Create reminders with custom repeat intervals.
-   **Countdowns**: Keep track of important upcoming events.
-   **Weekly Schedule**: Manage your weekly recurring events.
-   **Random Check-ins**: Get random prompts throughout the day to stay mindful.
-   **Summaries**: Receive daily or custom summaries of your upcoming items.
-   **Quotes**: Store and retrieve your favorite quotes.
-   **Multi-language Support**: Currently supports English and Persian (Farsi).
-   **Timezone Aware**: Handles timezones for accurate scheduling.

## Prerequisites

-   Python 3.11 or higher
-   A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
-   Docker (optional, for containerized deployment)

## Installation

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/remindino.git
    cd remindino
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Copy `.env.example` to `.env` and fill in your details.
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and set `TELEGRAM_BOT_TOKEN`.

5.  **Run the bot:**
    ```bash
    python src/bot.py
    ```

### Docker Setup

1.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```

    This will start the bot in a container and persist data in the `data/` directory.

## Configuration

The bot is configured via environment variables. See `.env.example` for a template.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token | (Required) |
| `DB_PATH` | Path to the SQLite database file | `data/bot.db` |

## Project Structure

```
.
├── src/                # Source code
│   ├── bot.py          # Main entry point
│   ├── database.py     # Database initialization and connection
│   ├── modules/        # Bot modules (tasks, goals, etc.)
│   └── ...
├── data/               # Data directory (ignored by git, used for DB)
├── docker-compose.yml  # Docker Compose configuration
├── dockerfile          # Dockerfile
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
