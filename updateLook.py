import base64
import requests
from dotenv import load_dotenv
import os
# Replace discord token with yours
load_dotenv()
TOKEN = os.getenv("TOKEN")
# Define URLs for profile picture and banner
PROFILE_IMAGE_URL = "https://media.discordapp.net/attachments/1235686662173102121/1235826842640973895/icon.gif?ex=6635c8ef&is=6634776f&hm=52e73811ac2fb75a8da9736372301bfaf909af39560e6583fd5f9dc42962592e&=&width=624&height=624"
BANNER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1235686662173102121/1235690554449203322/record_spin.gif?ex=66354a02&is=6633f882&hm=9181e714c4692922d9663119b05942ccb59a9f74ba4803e105c0baedfc19f3f9&"

# Download profile and banner images
profile_image_response = requests.get(PROFILE_IMAGE_URL)
banner_image_response = requests.get(BANNER_IMAGE_URL)

# Check if images were downloaded successfully
if profile_image_response.status_code == 200 and banner_image_response.status_code == 200:
    # Encode images to base64
    profile_image_base64 = base64.b64encode(profile_image_response.content).decode('utf-8')
    banner_image_base64 = base64.b64encode(banner_image_response.content).decode('utf-8')

    # Prepare JSON payload with base64-encoded images
    payload = {
        "avatar": f"data:image/gif;base64,{profile_image_base64}",
        "banner": f"data:image/gif;base64,{banner_image_base64}"
    }

    # Prepare headers with bot token
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }

    # Send HTTP PATCH request to update profile picture and banner
    response = requests.patch('https://discord.com/api/v10/users/@me', headers=headers, json=payload)

    # Check if the response indicates success
    if response.status_code == 200:
        print('Profile picture and banner changed successfully!')
    else:
        print('Failed to change profile picture and banner:', response.text)
else:
    print('Failed to download profile picture or banner')