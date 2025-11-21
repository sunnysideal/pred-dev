# My Home Assistant Add-on

A custom Home Assistant add-on that can interact with your Home Assistant instance.

## Features

- Access to Home Assistant API
- Read entity states
- Call services
- Authenticate automatically using supervisor token

## Installation

### Option 1: Add to your Home Assistant (Production)

1. Add this repository to your Home Assistant add-on store:
   - Go to **Settings** → **Add-ons** → **Add-on Store** (bottom right)
   - Click the three dots menu → **Repositories**
   - Add: `https://github.com/YOUR_USERNAME/YOUR_REPO`

2. Install the add-on from the store
3. Configure the add-on options
4. Start the add-on

### Option 2: Local Development

For local development and testing:

1. Copy this folder to your Home Assistant's add-ons directory:
   ```
   /addon_configs/local/my_ha_addon/
   ```

2. Restart Home Assistant or reload add-ons

3. The add-on will appear in the add-on store under "Local add-ons"

## Development Setup

### Prerequisites

- Home Assistant instance (running or test instance)
- Python 3.9+ (for local testing)
- Docker (for building the add-on)

### Local Development Without Docker

For faster development, you can test the Python code directly:

1. Install Python dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

2. Set environment variables:
   ```bash
   # Windows PowerShell
   $env:SUPERVISOR_TOKEN="your_home_assistant_long_lived_token"
   ```

3. Modify `app/main.py` to use your Home Assistant URL:
   ```python
   self.ha_url = "http://YOUR_HA_IP:8123/api"
   ```

4. Run the application:
   ```bash
   python app/main.py
   ```

### Getting a Long-Lived Access Token

For local development, you need a long-lived access token:

1. In Home Assistant, go to your profile (click your username in the sidebar)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Give it a name (e.g., "Dev Add-on")
5. Copy the token and use it as `SUPERVISOR_TOKEN`

### Building the Docker Image

```bash
docker build -t my-ha-addon .
```

### Testing in Home Assistant

1. Copy the entire add-on folder to:
   - `/usr/share/hassio/addons/local/my_ha_addon/` (on Home Assistant OS)
   - Or your configured add-ons directory

2. Restart Home Assistant or use the "Reload" button in the add-ons page

3. Install and start the add-on

## Configuration

Available options in the add-on configuration:

- **log_level**: Set the logging level (trace, debug, info, notice, warning, error, fatal)

## API Usage Examples

### Get All Entity States

```python
ha_api = HomeAssistantAPI()
states = ha_api.get_states()
for state in states:
    print(f"{state['entity_id']}: {state['state']}")
```

### Get Specific Entity State

```python
state = ha_api.get_entity_state("sensor.temperature")
print(f"Temperature: {state['state']}°C")
```

### Call a Service

```python
# Turn on a light
ha_api.call_service("light", "turn_on", {
    "entity_id": "light.living_room"
})

# Send a notification
ha_api.call_service("notify", "notify", {
    "message": "Hello from my add-on!"
})
```

## Project Structure

```
.
├── app/
│   ├── main.py           # Main application code
│   └── requirements.txt  # Python dependencies
├── config.json           # Add-on configuration
├── Dockerfile            # Container definition
├── build.json            # Build configuration
├── run.sh                # Entry point script
└── README.md             # This file
```

## Troubleshooting

### Check Add-on Logs

In Home Assistant:
1. Go to **Settings** → **Add-ons**
2. Click on your add-on
3. Click the "Log" tab

### Common Issues

- **Authentication errors**: Ensure `homeassistant_api: true` is set in `config.json`
- **Connection refused**: Check that Home Assistant is accessible
- **Module not found**: Ensure all dependencies are in `requirements.txt`

## Next Steps

1. Modify `app/main.py` with your custom logic
2. Add additional Python files to the `app/` directory as needed
3. Update `config.json` with any additional configuration options
4. Test locally before deploying

## Resources

- [Home Assistant Add-on Documentation](https://developers.home-assistant.io/docs/add-ons)
- [Home Assistant API](https://developers.home-assistant.io/docs/api/rest/)
- [Supervisor API](https://developers.home-assistant.io/docs/api/supervisor/)
