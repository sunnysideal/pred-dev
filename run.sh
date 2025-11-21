#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Home Assistant Add-on..."

# Get configuration options
LOG_LEVEL=$(bashio::config 'log_level')
bashio::log.info "Log level: ${LOG_LEVEL}"

# Export Home Assistant environment variables
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export HASSIO_TOKEN="${SUPERVISOR_TOKEN}"

# Start the application
bashio::log.info "Starting application..."
cd /app
python3 main.py
