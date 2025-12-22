import os
import time
import json
import logging
import click
from dotenv import load_dotenv
from ..utils.generator import TemplateGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@click.command()
@click.option('--topic', multiple=True, help='Specific topic to generate (can be used multiple times).')
@click.option('--count', default=0, help='Number of random templates to generate if no topics provided.')
@click.option('--output-dir', default='generic_chat/templates', help='Directory to save generated templates.')
def main(topic, count, output_dir):
    """
    Auto-generates A2UI templates using an LLM.
    """
    generator = TemplateGenerator()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    topics_to_process = list(topic)
    
    if not topics_to_process and count > 0:
        # Default interesting topics if none provided
        candidates = [
            "Music Player", "Recipe Card", "Fitness Tracker", "Investment Portfolio", 
            "Task Manager", "Event Ticket", "Product Detail Page", "User Profile",
            "Chat Interface", "Notification Center"
        ]
        topics_to_process = candidates[:count]

    if not topics_to_process:
        click.echo("Please provide --topic or --count > 0.")
        return

    logger.info(f"Starting generation for {len(topics_to_process)} topics...")

    for t in topics_to_process:
        logger.info(f"Generating: {t}")
        result = generator.generate(t)
        
        if result:
            filename = f"{result['id'].lower()}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2)
                
            logger.info(f"Saved {result['id']} to {filepath}")
        else:
            logger.error(f"Failed to generate {t}")
            
        # Modest sleep to respect rate limits (e.g. 15 RPM = one every 4s, but safer to do 10s)
        logger.info("Sleeping for 10s to respect Rate Limits...")
        time.sleep(10)

if __name__ == '__main__':
    main()
