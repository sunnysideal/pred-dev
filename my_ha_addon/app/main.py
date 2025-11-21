import os
import sys
import logging
import requests
import json
import yaml
import shutil
from time import sleep
from pathlib import Path

# Configuration loading
def load_config():
    """Load configuration from YAML file"""
    # Try add-on data directory first (persisted, editable location)
    config_path = Path("/data/neuralprophet.yaml")
    
    # Fall back to bundled config for first run
    if not config_path.exists():
        bundled_config = Path(__file__).parent.parent / "neuralprophet.yaml"
        if bundled_config.exists():
            print(f"Creating default config at {config_path}")
            try:
                # Ensure data directory exists
                config_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(bundled_config, config_path)
                print(f"Config file copied successfully")
            except Exception as e:
                print(f"Error copying config: {e}")
                # Fall back to bundled config
                config_path = bundled_config
    
    if config_path.exists():
        print(f"Loading config from {config_path}")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        print(f"Config file not found, using defaults")
        return {}

# Load configuration
config = load_config()

# Set up logging
log_level = config.get('logging', {}).get('level', 'info').upper()
log_format = config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(
    level=getattr(logging, log_level),
    format=log_format
)
logger = logging.getLogger(__name__)

class HomeAssistantAPI:
    """Client for interacting with Home Assistant API"""
    
    def __init__(self):
        # Get the supervisor token from environment
        self.token = os.environ.get('SUPERVISOR_TOKEN')
        
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
    logger.info(f"App name: {config.get('app_name', 'Unknown')}")
    logger.info(f"Version: {config.get('version', 'Unknown')}")
    
    # Initialize Home Assistant API client
    ha_api = HomeAssistantAPI()
    
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
