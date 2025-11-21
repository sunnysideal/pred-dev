# Development Helper Script
# This script helps you test the add-on locally without Docker

import os
import sys

# Load environment variables from .env file
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✓ Loaded environment variables from .env")
    else:
        print("⚠ Warning: .env file not found. Copy .env.example to .env")
        sys.exit(1)

if __name__ == "__main__":
    # Load environment variables
    load_env()
    
    # Modify the API URL for local development
    import app.main as main
    
    # Override the URL in the HomeAssistantAPI class for local dev
    original_init = main.HomeAssistantAPI.__init__
    
    def dev_init(self):
        original_init(self)
        # Use the local HA URL instead of supervisor URL
        ha_url = os.environ.get('HA_URL', 'http://homeassistant.local:8123')
        self.ha_url = f"{ha_url}/api"
        print(f"✓ Using Home Assistant URL: {self.ha_url}")
    
    main.HomeAssistantAPI.__init__ = dev_init
    
    print("Starting add-on in development mode...")
    print("Press Ctrl+C to stop\n")
    
    # Run the main application
    main.main()
