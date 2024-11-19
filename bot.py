import os
import glob
import subprocess
from atproto import Client, models
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Credentials from GitHub Secrets
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Initialize the Bluesky Client
client = Client()

LOG_FILE = "posted_images.log"  # Log file to track posted images

def get_next_image(directory="images/"):
    """Retrieve the next unposted image to post based on numerical order."""
    images = sorted(glob.glob(f"{directory}/*.jpg"))
    if not images:
        print("No images found in the directory.")
        return None

    for image in images:
        if not is_image_posted(image):
            return image

    print("All images in the directory have already been posted.")
    return None

def log_posted_image(image_path):
    """Log the posted image to the log file."""
    try:
        # Write the image path to the log file
        with open(LOG_FILE, "a") as log:
            log.write(f"{image_path}\n")
        print(f"Logged posted image: {image_path}")
    except Exception as e:
        print(f"Error logging posted image: {e}")

def is_image_posted(image_path):
    """Check if the image has already been posted (exists in the log file)."""
    try:
        with open(LOG_FILE, "r") as log:
            logged_images = log.readlines()
        logged_images = [line.strip() for line in logged_images]
        return image_path in logged_images
    except FileNotFoundError:
        return False

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

        # Check if the image has already been posted
        if is_image_posted(image_path):
            print(f"Image {image_path} has already been posted.")
            return

        # Prepare the post text
        post_text = "#hrvatibezkonteksta"
        hashtag_length = len(post_text)

        # Create a hashtag facet
        facets = [
            {
                "index": {
                    "byteStart": 0,  # Start of the hashtag
                    "byteEnd": hashtag_length  # End of the hashtag
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#tag",
                        "tag": "hrvatibezkonteksta"
                    }
                ]
            }
        ]

        # Read image data
        with open(image_path, "rb") as img:
            image_data = img.read()

        # Upload the image
        upload = client.upload_blob(image_data)
        images = [models.AppBskyEmbedImages.Image(alt="@utjecajnik best of", image=upload.blob)]
        embed = models.AppBskyEmbedImages.Main(images=images)

        # Create the post with rich text facets
        client.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=client.me.did,
                collection=models.ids.AppBskyFeedPost,
                record=models.AppBskyFeedPost.Record(
                    text=post_text,
                    facets=facets,
                    embed=embed,
                    created_at=client.get_current_time_iso(),
                ),
            )
        )
        print(f"Successfully posted: {image_path} at {datetime.now()}")
        
        # Log the posted image
        log_posted_image(image_path)

    except Exception as e:
        print(f"Error while posting: {e}")

if __name__ == "__main__":
    post_to_bluesky()
