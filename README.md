## [Mobile part see here](https://github.com/gubnota/otp_sync)

# OTP_mail converts mails to messages

![video](https://github.com/user-attachments/assets/c8811b38-0ba9-471d-af6a-83a3f731d3c7)

## Prerequisites

- VPS
- available Domain name (you can use 3rd level domain name)
- set MX record for your subdomain to point to your VPS node

```txt
sub.domain.com.  IN  MX  10 sub.domain.com.
```

```sh
dig sub.domain.com MX
```

- Allow SMTP traffic on your VPS

```sh
sudo ufw allow 25/tcp
```

## .env

1. create `.env` (see env.example)
2. make sure BOT_TOKEN is the correct secret for your Telegram bot.

## Production

```sh
docker compose up --build
```

## Development

- Using pip:

```bash
pip install -r requirements.txt
```

- Using poetry:

```bash
poetry install
```

- Using uv:

```bash
uv sync
```

- make sure you run `main.py` to start the bot and the SMTP server.

```sh
uv run main.py
```

- test it by sending a test email to your bot (local loop back address):

```sh
uv run test_email.py
```
