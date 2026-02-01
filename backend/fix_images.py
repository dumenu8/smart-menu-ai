import urllib.request
import json
import re

BASE_URL = "http://localhost:8000"

# List of files present in frontend/public/images (Observed by Antigravity)
AVAILABLE_FILES = [
    "banana_roti.png",
    "chicken_satay_1769850566774.png",
    "coconut_ice_cream_1769854261628.png",
    "crab_fried_rice.png",
    "crispy_pork_kale.png",
    "crying_tiger_beef.png",
    "fish_cakes_1769854277992.png",
    "fresh_summer_rolls.png",
    "garlic_pepper_prawns.png",
    "green_curry_1769850430708.png",
    "khao_soi.png",
    "lemongrass_juice.png",
    "mango_sticky_rice_1769850485510.png",
    "massaman_curry_1769850471132.png",
    "morning_glory_stir_fry.png",
    "pad_kra_pao_1769854216873.png",
    "pad_see_ew_1769850518648.png",
    "pad_thai_1769850416425.png",
    "panang_curry_1769854187087.png",
    "pineapple_fried_rice_1769854166650.png",
    "po_tak_soup.png",
    "red_curry_roast_duck.png",
    "singha_beer.png",
    "som_tum_1769850455998.png",
    "spicy_beef_salad_1769854201414.png",
    "spring_rolls_1769850550861.png",
    "steam_fish_lime.png",
    "thai_iced_tea_1769854235659.png",
    "tom_kha_gai_1769850536280.png",
    "tom_yum_goong_1769850401513.png"
]

def normalize(name):
    # Lowercase, remove numbers, remove file extensions, replace special chars with space or empty
    name = name.lower()
    name = re.sub(r'\.png$', '', name)
    name = re.sub(r'_\d+$', '', name) # Remove timestamp suffix if present in filename
    name = re.sub(r'[^a-z ]', ' ', name.replace('_', ' '))
    return name.strip()

def find_best_match(item_name):
    item_norm = normalize(item_name)
    best_file = None
    best_score = 0

    for filename in AVAILABLE_FILES:
        file_norm = normalize(filename)
        
        # Simple containment score
        score = 0
        file_parts = file_norm.split()
        item_parts = item_norm.split()
        
        matches = sum(1 for part in item_parts if part in file_norm)
        
        # Bonus for exact match of normalized strings
        if item_norm == file_norm:
            matches += 5
            
        if matches > best_score:
            best_score = matches
            best_file = filename
            
    # Threshold to avoid bad matches
    if best_score > 0:
        return best_file
    return None

def fix_images():
    print("Fetching menu items...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/menu/") as response:
            data = response.read()
            menu_items = json.loads(data)
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return

    print(f"Found {len(menu_items)} items. Checking images...")

    for item in menu_items:
        name = item.get("name")
        current_image = item.get("image_data") or ""
        
        # We want to force update if:
        # 1. No image
        # 2. Image path doesn't start with /images/ (e.g. is 'images/...' or base64)
        # 3. Image path points to something that isn't in our list (broken link)
        
        best_file = find_best_match(name)
        
        if not best_file:
            print(f"xx No matching file found for: {name}")
            continue

        desired_path = f"/images/{best_file}"
        
        if current_image == desired_path:
            # Already correct
            continue
            
        print(f"Updating {name}...")
        print(f"   Old: {current_image[:50]}...")
        print(f"   New: {desired_path}")
        
        payload = {
            "name": item.get("name"),
            "description": item.get("description"),
            "price": str(item.get("price")),
            "category": item.get("category"),
            "image_data": desired_path
        }
        
        item_id = item.get("id")
        json_payload = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(f"{BASE_URL}/menu/{item_id}?item_id={item_id}", data=json_payload, method='PUT')
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req) as update_res:
                print(f"   -> Success")
        except Exception as e:
            print(f"   -> Failed: {e}")

if __name__ == "__main__":
    fix_images()
