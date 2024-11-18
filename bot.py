import os
import glob
from atproto import Client  # Corrected import
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Credentials from GitHub Secrets
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Initialize the Bluesky Client
client = Client()

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
        client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)

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

        # Upload the image
        uploaded_image = client.upload_image(image_data)

        # Create the post
        client.post(text=post_text, embed=uploaded_image)  # Assuming `embed` is correct for adding images

        print(f"Posted: {image_path} at {datetime.now()}")

    except Exception as e:
        print(f"Error while posting: {e}")

if __name__ == "__main__":
    post_to_bluesky()
