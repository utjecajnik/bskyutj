import os
import glob
from atproto import BskyAgent  # Replace with the correct Python Bluesky library
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Credentials from GitHub Secrets
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Initialize the Bluesky Agent
agent = BskyAgent(service="https://bsky.social")

def get_next_image(directory="images/"):
    """Retrieve the next image to post based on numerical order."""
    images = sorted(glob.glob(f"{directory}/*.jpg"))
    if not images:
        print("No images found in the directory.")
        return None
    return images[0]

def post_to_bluesky():
    """Logs in and posts an image with text to Bluesky."""
    try:
        # Log in to Bluesky
        agent.login(identifier=BLUESKY_USERNAME, password=BLUESKY_PASSWORD)

        # Find the next image
        image_path = get_next_image()
        if not image_path:
            print("No images to post. Exiting.")
            return

        # Prepare the post text
        post_text = "#hrvatibezkonteksta"

        # Read image data
        with open(image_path, "rb") as img:
            image_data = img.read()

        # Post to Bluesky (assuming the API has an upload method)
        agent.upload_image(image_data)  # Upload image
        agent.post({"text": post_text})  # Post with text

        print(f"Posted: {image_path} at {datetime.now()}")

    except Exception as e:
        print(f"Error while posting: {e}")

if __name__ == "__main__":
    post_to_bluesky()
