# 🛠️ Development Guide

Welcome to the Google Sheets Telegram Bot development guide! This document will help you set up your development environment and contribute to the project.

## 📋 Table of Contents

- [🚀 Quick Setup](#-quick-setup)
- [🏗️ Architecture](#️-architecture)
- [📝 Code Style](#-code-style)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🔧 Environment Setup](#-environment-setup)
- [📦 Dependencies](#-dependencies)
- [🐛 Debugging](#-debugging)
- [🤝 Contributing](#-contributing)

## 🚀 Quick Setup

### Prerequisites

- Python 3.8+
- Git
- Google Cloud Platform account
- Telegram Bot Token

### Development Environment Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/theknyazzev/google-sheets-tg-bot.git
   cd google-sheets-tg-bot

   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Google Sheets API setup:**
   - Place your `credentials.json` in the project root
   - Ensure service account has access to your test sheet

4. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Start development server:**
   ```bash
   python main.py
   ```

## 🏗️ Architecture

### Project Structure

```
google-sheets-telegram-bot/
├── 📁 src/
│   ├── 🤖 main.py              # Entry point, bot initialization
│   ├── ⚙️ config.py            # Configuration management
│   ├── 📊 google_sheets.py     # Google Sheets API wrapper
│   ├── 🎮 handlers.py          # Telegram command handlers
│   ├── ⌨️ keyboards.py         # Inline keyboard layouts
│   ├── 🛡️ middlewares.py       # Authentication & rate limiting
│   ├── 🔧 utils.py             # Utility functions
│   └── 🧪 test_bot.py          # Unit tests
├── 📁 tests/                   # Test files
├── 📁 docs/                    # Additional documentation
├── 📋 requirements.txt         # Production dependencies
├── 📋 requirements-dev.txt     # Development dependencies
├── 🔑 credentials.json         # Google API credentials
├── 📝 .env                     # Environment variables
├── 📚 README.md               # Main documentation
└── 🛠️ DEVELOPMENT.md          # This file
```

### Component Breakdown

#### 🤖 main.py
- Bot initialization and startup
- Dispatcher configuration
- Middleware registration
- Graceful shutdown handling

#### ⚙️ config.py
- Environment variable loading
- Configuration validation
- Settings management

#### 📊 google_sheets.py
- Google Sheets API client
- CRUD operations on spreadsheets
- Error handling and retry logic
- Data validation

#### 🎮 handlers.py
- Command handlers (`/start`, `/find`, `/row`)
- Callback query handlers
- Message processing logic
- User interaction flow

#### ⌨️ keyboards.py
- Inline keyboard generation
- Dynamic button creation
- Navigation controls

#### 🛡️ middlewares.py
- User authentication
- Rate limiting
- Request logging
- Error tracking

## 📝 Code Style

### Python Standards

We follow PEP 8 with some modifications:

```python
# Line length: 88 characters (Black formatter)
# String quotes: Double quotes preferred
# Import order: isort configuration

# Example function
async def get_sheet_data(
    sheet_id: str, 
    range_name: str, 
    retries: int = 3
) -> List[List[str]]:
    """
    Fetch data from Google Sheets.
    
    Args:
        sheet_id: Google Sheets document ID
        range_name: A1 notation range
        retries: Number of retry attempts
        
    Returns:
        List of rows with cell values
        
    Raises:
        SheetsAPIError: When API request fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Failed to fetch sheet data: {e}")
        raise
```

### Formatting Tools

```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Check style
flake8 .
mypy .
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🧪 Testing

### Test Structure

```
tests/
├── test_config.py          # Configuration tests
├── test_google_sheets.py   # Google Sheets API tests
├── test_handlers.py        # Handler function tests
├── test_keyboards.py       # Keyboard generation tests
├── test_middlewares.py     # Middleware tests
├── test_utils.py           # Utility function tests
└── conftest.py             # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_handlers.py

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

### Test Examples

```python
# tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, User, Chat

from src.handlers import cmd_start
from src.keyboards import get_main_keyboard

@pytest.fixture
def mock_message():
    return Message(
        message_id=1,
        date=1234567890,
        chat=Chat(id=123, type="private"),
        from_user=User(id=123, is_bot=False, first_name="Test"),
        content_type="text",
        options={}
    )

@pytest.mark.asyncio
async def test_cmd_start(mock_message):
    """Test /start command handler."""
    with patch('src.handlers.bot') as mock_bot:
        mock_bot.send_message = AsyncMock()
        
        await cmd_start(mock_message)
        
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert "Welcome" in kwargs['text']
        assert kwargs['reply_markup'] is not None
```

### Mocking Google Sheets API

```python
# tests/test_google_sheets.py
import pytest
from unittest.mock import patch, MagicMock

from src.google_sheets import GoogleSheetsClient

@pytest.fixture
def mock_sheets_client():
    with patch('src.google_sheets.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        client = GoogleSheetsClient()
        yield client, mock_service

@pytest.mark.asyncio
async def test_get_sheet_data(mock_sheets_client):
    """Test fetching data from Google Sheets."""
    client, mock_service = mock_sheets_client
    
    # Mock API response
    mock_service.spreadsheets().values().get().execute.return_value = {
        'values': [['Name', 'Age'], ['John', '25'], ['Jane', '30']]
    }
    
    result = await client.get_sheet_data('sheet_id', 'A1:B3')
    
    assert len(result) == 3
    assert result[0] == ['Name', 'Age']
    assert result[1] == ['John', '25']
```

## 🚀 Deployment

### Production Environment

1. **Server Setup:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx supervisor
   
   # Create application user
   sudo useradd -m -s /bin/bash botuser
   sudo su - botuser
   ```

2. **Application Deployment:**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/google-sheets-telegram-bot.git
   cd google-sheets-telegram-bot
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Setup environment
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Supervisor Configuration:**
   ```ini
   # /etc/supervisor/conf.d/telegram-bot.conf
   [program:telegram-bot]
   command=/home/botuser/google-sheets-telegram-bot/venv/bin/python main.py
   directory=/home/botuser/google-sheets-telegram-bot
   user=botuser
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/telegram-bot.err.log
   stdout_logfile=/var/log/telegram-bot.out.log
   environment=PATH="/home/botuser/google-sheets-telegram-bot/venv/bin"
   ```

4. **Start Services:**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start telegram-bot
   ```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  telegram-bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Environment Variables

```env
# Production .env
BOT_TOKEN=your_production_bot_token
GOOGLE_SHEET_ID=your_production_sheet_id
WORKSHEET_NAME=Sheet1
ALLOWED_USER_IDS=123456789,987654321
LOG_LEVEL=INFO
LOG_FILE=/var/log/telegram-bot/bot.log
REDIS_URL=redis://localhost:6379/0  # For rate limiting
SENTRY_DSN=your_sentry_dsn  # For error tracking
```

## 🔧 Environment Setup

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=22.0.0
isort>=5.10.0
flake8>=4.0.0
mypy>=0.950
pre-commit>=2.17.0
```

### IDE Configuration

#### VS Code Settings

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm Configuration

- Set Python interpreter to `./venv/bin/python`
- Enable Black formatter
- Configure isort with Black profile
- Enable flake8 and mypy inspections

## 📦 Dependencies

### Core Dependencies

```txt
# requirements.txt
aiogram==3.13.1          # Telegram Bot framework
google-api-python-client==2.70.0  # Google Sheets API
google-auth-httplib2==0.1.0       # Google Auth
google-auth-oauthlib==0.8.0       # Google OAuth
python-dotenv==0.19.2             # Environment variables
redis==4.3.4                      # Rate limiting (optional)
sentry-sdk==1.12.1               # Error tracking (optional)
```

### Development Tools

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks

## 🐛 Debugging

### Logging Configuration

```python
# config.py
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # File handler
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    if log_file:
        file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
```

### Debug Mode

```python
# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher

async def main():
    """Main function."""
    # Enable debug logging
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Debug middleware
    if DEBUG:
        from aiogram.middlewares import LoggingMiddleware
        dp.middleware.setup(LoggingMiddleware())
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

### Common Issues

#### Google Sheets API Errors

```python
# Error: 403 Forbidden
# Solution: Check service account permissions

# Error: 400 Bad Request
# Solution: Validate range format (A1:Z100)

# Error: 429 Too Many Requests
# Solution: Implement exponential backoff
```

#### Telegram Bot Errors

```python
# Error: 401 Unauthorized
# Solution: Check BOT_TOKEN

# Error: 400 Bad Request
# Solution: Validate message format and keyboard markup

# Error: 409 Conflict
# Solution: Only one bot instance should run
```

## 🤝 Contributing

### Workflow

1. **Fork the repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make changes and test:**
   ```bash
   # Write code
   # Add tests
   pytest
   black .
   isort .
   flake8 .
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/amazing-feature
   # Create Pull Request on GitHub
   ```

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

### Pull Request Guidelines

- Clear description of changes
- Tests for new features
- Documentation updates
- Code style compliance
- No breaking changes without major version bump

### Code Review Process

1. Automated checks must pass
2. At least one reviewer approval
3. All discussions resolved
4. Up-to-date with main branch

---

## 📞 Support

For development questions:

- 💬 [GitHub Discussions](https://github.com/yourusername/google-sheets-telegram-bot/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/google-sheets-telegram-bot/issues)
- 📧 Email: dev@example.com

---

<div align="center">

**Happy Coding! 🚀**

</div>
