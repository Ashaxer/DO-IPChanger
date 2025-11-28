#!/bin/bash

# Get the path of the running script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ask for interval for check.py
read -p "Run check.py every how many hours? (default 2): " interval
interval=${interval:-2}  # default 2 hours

# Ask if webhook cronjob should be installed
read -p "Install webhook cronjob? (y/N): " webhook_choice
webhook_choice=${webhook_choice,,}  # lowercase

# Prepare cronjobs
check_cron="0 */$interval * * * cd $SCRIPT_PATH && $SCRIPT_PATH/venv/bin/python3 check.py"

if [[ "$webhook_choice" == "y" ]]; then
    webhook_cron="@reboot cd $SCRIPT_PATH && $SCRIPT_PATH/venv/bin/python3 webhook.py"
fi

# Add cronjobs without removing existing ones
(crontab -l 2>/dev/null; echo "$check_cron") | crontab -
if [[ "$webhook_choice" == "y" ]]; then
    (crontab -l 2>/dev/null; echo "$webhook_cron") | crontab -
fi

echo "Cronjobs installed successfully!"
