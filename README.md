# 📊 Google Sheets Telegram Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![Google Sheets](https://img.shields.io/badge/Google-Sheets-green?style=for-the-badge&logo=google-sheets&logoColor=white)](https://sheets.google.com/)
[![aiogram](https://img.shields.io/badge/aiogram-3.13.1-blue?style=for-the-badge)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Powerful Telegram bot for Google Sheets API integration with aiogram 3.x**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-bot-commands) • [🛠️ Development](DEVELOPMENT.md) • [📝 License](#-license)

</div>

---

## ✨ Features

<table>
<tr>
<td>🔐</td>
<td><strong>Access Control</strong></td>
<td>Strict verification of Telegram user IDs</td>
</tr>
<tr>
<td>🔍</td>
<td><strong>Table Search</strong></td>
<td>Search rows by any value with instant results</td>
</tr>
<tr>
<td>📋</td>
<td><strong>Data Viewing</strong></td>
<td>Get specific rows by number</td>
</tr>
<tr>
<td>📄</td>
<td><strong>All Rows</strong></td>
<td>View all rows with pagination and navigation</td>
</tr>
<tr>
<td>✏️</td>
<td><strong>Editing</strong></td>
<td>Modify cell values in the table</td>
</tr>
<tr>
<td>📊</td>
<td><strong>Data Structure</strong></td>
<td>View column names and metadata</td>
</tr>
<tr>
<td>🛡️</td>
<td><strong>Spam Protection</strong></td>
<td>Rate limiting to prevent frequent requests</td>
</tr>
<tr>
<td>🎯</td>
<td><strong>Easy Navigation</strong></td>
<td>Intuitive buttons and slider interface</td>
</tr>
</table>

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- Google Cloud Platform account
- Google Sheets API access

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theknyazzev/google-sheets-tg-bot.git
   cd google-sheets-telegram-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit the .env file with your data
   ```

4. **Configure Google Sheets API:**
   - Place your `credentials.json` in the root folder
   - Make sure your service account has access to the sheet

5. **Run the bot:**
   ```bash
   python main.py
   ```

## 📖 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and main menu | `/start` |
| `/find [value]` | Search rows by value | `/find John` |
| `/row [number]` | Get specific row | `/row 5` |

### Interactive Buttons

- 🔍 **Search** - Search across all table cells
- 📄 **All Rows** - View all data with navigation
- 📊 **Structure** - Information about table columns
- ✏️ **Edit** - Modify table data

## 🔧 Configuration

### Environment Variables (.env)

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# Google Sheets
GOOGLE_SHEET_ID=your_google_sheet_id
WORKSHEET_NAME=Sheet1

# Access (User IDs separated by commas)
ALLOWED_USER_IDS=123456789,987654321

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

### Google Cloud Platform Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Sheets API
3. Create a service account
4. Download `credentials.json`
5. Grant access to your service account for the spreadsheet

## 📁 Project Structure

```
google-sheets-telegram-bot/
├── 📁 src/
│   ├── 🤖 main.py              # Application entry point
│   ├── ⚙️ config.py            # Configuration and settings
│   ├── 📊 google_sheets.py     # Google Sheets API integration
│   ├── 🎮 handlers.py          # Bot command handlers
│   ├── ⌨️ keyboards.py         # Inline keyboards
│   ├── 🛡️ middlewares.py       # Access and rate limit middleware
│   ├── 🔧 utils.py             # Utility functions
│   └── 🧪 test_bot.py          # Tests
├── 📋 requirements.txt         # Python dependencies
├── 🔑 credentials.json         # Google API keys
├── 📝 .env                     # Environment variables
├── 📚 README.md               # Documentation
├── 🛠️ DEVELOPMENT.md          # Developer guide
└── 📄 LICENSE                 # MIT license
```

## 🔐 Security

- ✅ Access control by Telegram ID
- ✅ Rate limiting to prevent spam
- ✅ Input data validation
- ✅ Secure credentials storage
- ✅ Logging of all operations

## 📈 Monitoring

The bot keeps detailed logs of all operations:

- Incoming commands and messages
- API requests to Google Sheets
- Errors and exceptions
- Performance information

Logs are written to `bot.log` file and displayed in console.

## 🤝 Contributing

We welcome contributions to the project! Please read the [developer guide](DEVELOPMENT.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make a commit (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you have questions or suggestions:

- 🐛 [Create an Issue](https://github.com/theknyazzev/google-sheets-tg-bot/issues)
      - 💬 [Discussions](https://github.com/theknyazzev/google-sheets-tg-bot/discussions)
- 📧 Email: theknyazzev@gmail.com

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/theknyazzev/google-sheets-tg-bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/theknyazzev/google-sheets-tg-bot?style=social)
![GitHub issues](https://img.shields.io/github/issues/theknyazzev/google-sheets-tg-bot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/theknyazzev/google-sheets-tg-bot)

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
    
**[⬆ Back to Top](#-google-sheets-telegram-bot)**

Made with ❤️ for the community

</div>
