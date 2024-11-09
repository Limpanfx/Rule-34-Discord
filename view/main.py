import requests
import json
import os

SENT_IMAGES_FILE = 'sent_images.json'

def load_sent_images():
    if os.path.exists(SENT_IMAGES_FILE):
        with open(SENT_IMAGES_FILE, 'r') as file:
            return set(json.load(file))
    else:
        return set()

def save_sent_images(sent_images):
    with open(SENT_IMAGES_FILE, 'w') as file:
        json.dump(list(sent_images), file)

def fetch_images_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def send_image_to_discord(image_url, webhook_url):
    data = {
        "content": "Here's an image from Rule34!",
        "embeds": [
            {
                "image": {
                    "url": image_url
                }
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        print(f"Image sent to Discord: {image_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending image to Discord: {e}")

def extract_tags_from_posts(xml_data):
    from xml.etree import ElementTree as ET
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()

    tags_set = set()
    for post in root.findall('post'):
        tags = post.attrib.get('tags', "")
        tags_set.update(tags.split(' '))
    
    return tags_set

def main():
    webhook_url = input("Enter your Discord webhook URL: ").strip()

    sent_images = load_sent_images()

    api_url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=10"
    xml_data = fetch_images_from_api(api_url)

    if xml_data:
        tags_set = extract_tags_from_posts(xml_data)
        tags_list = sorted(tags_set)

        print("\nAvailable categories/tags:")
        for idx, tag in enumerate(tags_list, start=1):
            print(f"{idx}. {tag}")
        
        user_choice = input("\nEnter the number of the tag you'd like to use or type a tag: ").strip()

        if user_choice.isdigit():
            choice_idx = int(user_choice) - 1
            if 0 <= choice_idx < len(tags_list):
                user_input = tags_list[choice_idx]
                print(f"Chosen tag: {user_input}")
            else:
                print("Invalid choice, using 'safe' as default.")
                user_input = "safe"
        else:
            user_input = user_choice
            print(f"Chosen tag: {user_input}")

        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags={user_input}"

        print(f"\nFetching images for the tag: {user_input}...")

        xml_data = fetch_images_from_api(api_url)
        
        if xml_data:
            from xml.etree import ElementTree as ET
            tree = ET.ElementTree(ET.fromstring(xml_data))
            root = tree.getroot()
            
            for post in root.findall('post'):
                image_url = post.attrib.get('file_url')
                image_id = post.attrib.get('id')
                
                if image_url and image_id not in sent_images:
                    send_image_to_discord(image_url, webhook_url)
                    sent_images.add(image_id)

            save_sent_images(sent_images)

if __name__ == "__main__":
    main()
