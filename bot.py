import os
import glob
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

def get_next_image(directory="images/"):
    """Retrieve the next image to post based on numerical order."""
    images = sorted(glob.glob(f"{directory}/*.jpg"))
    if not images:
        print("No images found in the directory.")
        return None
    return images[0]

def delete_posted_image(image_path):
    """Delete the posted image from the 'images' folder and commit the change to GitHub."""
    try:
        # Delete the image locally
        os.remove(image_path)
        print(f"Deleted {image_path}")
        
        # Commit the change to GitHub (delete the image from repo)
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", "-A"], check=True)  # Add changes (deleted file)
        subprocess.run(["git", "commit", "-m", f"Delete posted image {os.path.basename(image_path)}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Committed and pushed the change to GitHub.")
    except Exception as e:
        print(f"Error deleting the image: {e}")

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

    except Exception as e:
        print(f"Error while posting: {e}")

if __name__ == "__main__":
    post_to_bluesky()
