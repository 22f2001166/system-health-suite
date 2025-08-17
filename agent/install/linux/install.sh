#!/usr/bin/env bash
set -e
APP_DIR="$HOME/system-health-suite/agent"
sudo mkdir -p /opt/syshealth-agent
sudo cp -r "$APP_DIR"/* /opt/syshealth-agent/
sudo cp "$APP_DIR/install/linux/systemd.service" /etc/systemd/system/syshealth-agent.service
sudo systemctl daemon-reload
sudo systemctl enable --now syshealth-agent
