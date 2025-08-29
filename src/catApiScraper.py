import requests
import json
import os

API_URL = "https://api.thecatapi.com/v1/breeds"
IMAGE_SEARCH_URL = "https://api.thecatapi.com/v1/images/search"
IMAGE_DIR = "cat_images"
API_KEY = os.getenv("CAT_API_KEY")
os.makedirs(IMAGE_DIR, exist_ok=True)

headers = {"x-api-key": API_KEY} if API_KEY else {}

response = requests.get(API_URL)
response.raise_for_status()
breeds = response.json()
breed_data = []

for breed in breeds:
    breed_id = breed["id"]
    print(f"Processing {breed['name']} (ID: {breed_id})...")
    image_url = None
    image_filename = ""

    # Fetch image using breed_id
    params = {
        "limit": 1,
        "breed_ids": breed_id,
        "api_key": API_KEY
    }
    img_response = requests.get(IMAGE_SEARCH_URL, params=params, headers=headers)
    if img_response.ok:
        img_results = img_response.json()
        if img_results and "url" in img_results[0]:
            image_url = img_results[0]["url"]
            print(f"Image URL: {image_url}")
            image_filename = os.path.join(IMAGE_DIR, f"{breed_id}_cat.jpg")
            try:
                img_data = requests.get(image_url).content
                with open(image_filename, "wb") as img_file:
                    img_file.write(img_data)
            except Exception as e:
                print(f"Failed to download image for {breed['name']}: {e}")
                image_filename = ""
        else:
            print(f"No image found for breed {breed['name']}")
    else:
        print(f"Image API request failed for breed {breed['name']}")

    breed_data.append({
        "id": breed["id"]+"_cat",
        "name": breed["name"],
        "temperament": breed.get("temperament", ""),
        "origin": breed.get("origin", ""),
        "country_code": breed.get("country_code", ""),
        "life_span": breed.get("life_span", ""),
        "wikipedia_url": breed.get("wikipedia_url", ""),
        "image_filename": image_filename
    })

with open("cat_breeds.json", "w", encoding="utf-8") as f:
    json.dump(breed_data, f, ensure_ascii=False, indent=2)

print(f"Saved {len(breed_data)} breeds to cat_breeds.json and images to {IMAGE_DIR}/")