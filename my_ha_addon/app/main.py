import os
import sys
import logging
import requests
import json
import yaml
import shutil
from time import sleep
from pathlib import Path

print("=" * 60)
print("ADDON STARTING - main.py is executing")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print("=" * 60)

# Configuration loading
def load_config():
    """Load configuration from YAML file"""
    # Data directory path (persisted on host)
    data_dir = Path("/data")
    config_path = data_dir / "neuralprophet.yaml"
    
    # Bundled config location in container
    bundled_config = Path(__file__).parent.parent / "neuralprophet.yaml"
    
    print(f"=== CONFIG LOADING DEBUG ===")
    print(f"Data directory: {data_dir}")
    print(f"Data directory exists: {data_dir.exists()}")
    print(f"Config path: {config_path}")
    print(f"Config exists: {config_path.exists()}")
    print(f"Bundled config: {bundled_config}")
    print(f"Bundled exists: {bundled_config.exists()}")
    
    # Always copy bundled config to /data/ if it doesn't exist
    if not config_path.exists():
        print(f"Config not found in /data/, attempting to copy...")
        
        if bundled_config.exists():
            try:
                # Ensure data directory exists (it should, but be safe)
                data_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                print(f"Copying: {bundled_config} -> {config_path}")
                shutil.copy2(bundled_config, config_path)
                
                # Verify copy
                if config_path.exists():
                    print(f"✓ Config copied successfully!")
                    print(f"  File size: {config_path.stat().st_size} bytes")
                else:
                    print(f"✗ Copy failed - file doesn't exist after copy")
                    
            except Exception as e:
                print(f"✗ Error copying config: {e}")
                import traceback
                traceback.print_exc()
                # Use bundled config as fallback
                config_path = bundled_config
                print(f"Using bundled config as fallback: {config_path}")
        else:
            print(f"✗ Bundled config not found!")
            # Try to list what's in the parent directory
            parent = bundled_config.parent
            if parent.exists():
                print(f"Contents of {parent}:")
                for item in sorted(parent.iterdir()):
                    print(f"  {item}")
    else:
        print(f"✓ Config already exists in /data/")
    
    # Load the config file
    if config_path.exists():
        print(f"Loading config from: {config_path}")
        try:
            with open(config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
                print(f"✓ Config loaded successfully")
                print(f"=== END CONFIG DEBUG ===\n")
                return loaded_config
        except Exception as e:
            print(f"✗ Error loading config: {e}")
            print(f"=== END CONFIG DEBUG ===\n")
            return {}
    else:
        print(f"✗ No config file found, using defaults")
        print(f"=== END CONFIG DEBUG ===\n")
        return {}

# Set up basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HomeAssistantAPI:
    """Client for interacting with Home Assistant API"""
    
    def __init__(self, config=None):
        # Get the supervisor token from environment
        self.token = os.environ.get('SUPERVISOR_TOKEN')
        
        # Use config if provided, otherwise defaults
        if config is None:
            config = {}
        
        # Home Assistant API endpoint (from config or default)
        self.ha_url = config.get('homeassistant', {}).get('url', "http://supervisor/core/api")
        self.timeout = config.get('homeassistant', {}).get('timeout', 10)
        
        # Get settings from config
        self.max_retries = config.get('settings', {}).get('max_retries', 3)
        self.retry_delay = config.get('settings', {}).get('retry_delay', 5)
        
        # Headers for authentication
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        if not self.token:
            logger.error("SUPERVISOR_TOKEN not found in environment")
            sys.exit(1)
    
    def get_states(self):
        """Get all entity states from Home Assistant"""
        try:
            response = requests.get(
                f"{self.ha_url}/states",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get states: {e}")
            return None
    
    def get_entity_state(self, entity_id):
        """Get state of a specific entity"""
        try:
            response = requests.get(
                f"{self.ha_url}/states/{entity_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get entity state: {e}")
            return None
    
    def call_service(self, domain, service, service_data=None):
        """Call a Home Assistant service"""
        try:
            response = requests.post(
                f"{self.ha_url}/services/{domain}/{service}",
                headers=self.headers,
                json=service_data or {},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call service: {e}")
            return None

def main():
    """Main application entry point"""
    logger.info("Home Assistant Add-on starting...")
    
    # Load configuration
    config = load_config()
    
    logger.info(f"App name: {config.get('app_name', 'Unknown')}")
    logger.info(f"Version: {config.get('version', 'Unknown')}")
    
    # Initialize Home Assistant API client
    ha_api = HomeAssistantAPI(config)
    
    # Get poll interval from config
    poll_interval = config.get('settings', {}).get('poll_interval', 60)
    
    # Get monitored entities from config
    monitored_entities = config.get('entities', [])
    
    # Example: Get all states
    logger.info("Fetching all entity states...")
    states = ha_api.get_states()
    
    if states:
        logger.info(f"Found {len(states)} entities")
        
        # If we have monitored entities in config, show their states
        if monitored_entities:
            logger.info(f"Monitoring {len(monitored_entities)} configured entities:")
            for entity_config in monitored_entities:
                entity_id = entity_config.get('entity_id')
                friendly_name = entity_config.get('friendly_name', entity_id)
                
                entity_state = ha_api.get_entity_state(entity_id)
                if entity_state:
                    logger.info(f"  {friendly_name}: {entity_state['state']}")
                else:
                    logger.warning(f"  {friendly_name}: Not found")
        else:
            # Show first 5 entities as example
            logger.info("Showing first 5 entities (configure monitored entities in config.yaml):")
            for state in states[:5]:
                logger.info(f"  {state['entity_id']} = {state['state']}")
    
    # Main loop
    logger.info(f"Entering main loop (polling every {poll_interval} seconds)...")
    try:
        while True:
            # Your add-on logic goes here
            # Example: Monitor specific entities and react to changes
            
            # Check custom settings from config
            if config.get('custom', {}).get('enable_notifications', False):
                # Do something with notifications
                pass
            
            if config.get('custom', {}).get('enable_automation', False):
                # Do something with automation
                pass
            
            # Sleep for configured interval
            sleep(poll_interval)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
