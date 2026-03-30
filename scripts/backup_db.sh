#!/usr/bin/env sh
set -eu
mkdir -p data/backups
cp data/bot.db data/backups/bot-backup.db
echo "Backup created at data/backups/bot-backup.db"
