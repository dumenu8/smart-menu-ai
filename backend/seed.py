import asyncio
import sys
import os
from decimal import Decimal

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import AsyncSessionLocal
from models import MenuItem, MenuEmbedding
from services.rag_service import RAGService

MENU_ITEMS = [
    {
        "name": "Tom Yum Goong",
        "description": "World-famous Thai spicy prawn soup with lemongrass, galangal, kaffir lime leaves, and fresh chilies. Contains shellfish.",
        "price": "18.50",
        "category": "Soup",
        "image_data": "/images/tom_yum_goong.png"
    },
    {
        "name": "Pad Thai",
        "description": "Classic stir-fried rice noodles with egg, peanuts, bean sprouts, and tamarind sauce. Choice of chicken, tofu, or shrimp.",
        "price": "14.95",
        "category": "Noodles",
        "image_data": "/images/pad_thai.png"
    },
    {
        "name": "Green Curry",
        "description": "Spicy and aromatic green curry with coconut milk, bamboo shoots, Thai basil, and eggplant. Served with jasmine rice.",
        "price": "16.50",
        "category": "Curry",
        "image_data": "/images/green_curry.png"
    },
    {
        "name": "Som Tum (Papaya Salad)",
        "description": "Crispy shredded green papaya salad with cherry tomatoes, green beans, peanuts, lime, and chilies. Sweet, sour, and spicy.",
        "price": "11.00",
        "category": "Salad",
        "image_data": "/images/som_tum.png"
    },
    {
        "name": "Massaman Curry",
        "description": "Rich and mild curry with roasted spices, peanuts, potatoes, onions, and slow-cooked beef chunks.",
        "price": "19.00",
        "category": "Curry",
        "image_data": "/images/massaman_curry.png"
    },
    {
        "name": "Mango Sticky Rice",
        "description": "Sweet coconut sticky rice served with fresh ripe mango and topped with roasted mung beans. A perfect dessert.",
        "price": "9.50",
        "category": "Dessert",
        "image_data": "/images/mango_sticky_rice.png"
    },
    {
        "name": "Pad See Ew",
        "description": "Stir-fried flat rice noodles with soy sauce, egg, and Chinese kale. A savory non-spicy favorite.",
        "price": "14.50",
        "category": "Noodles",
        "image_data": "/images/pad_see_ew.png"
    },
    {
        "name": "Tom Kha Gai",
        "description": "Creamy coconut chicken soup with galangal, lemongrass, and mushrooms. Mildly spiced and sour.",
        "price": "15.50",
        "category": "Soup",
        "image_data": "/images/tom_kha_gai.png"
    },
    {
        "name": "Spring Rolls",
        "description": "Crispy fried vegetable spring rolls served with sweet chili plum sauce. Vegan friendly.",
        "price": "8.00",
        "category": "Appetizer",
        "image_data": "/images/spring_rolls.png"
    },
    {
        "name": "Chicken Satay",
        "description": "Grilled marinated chicken skewers served with peanut sauce and cucumber relish.",
        "price": "10.50",
        "category": "Appetizer",
        "image_data": "/images/chicken_satay.png"
    },
    {
        "name": "Pineapple Fried Rice",
        "description": "Fried rice with pineapple chunks, egg, cashews, raisins, and curry powder. Served in a pineapple half.",
        "price": "17.00",
        "category": "Rice",
        "image_data": "/images/pineapple_fried_rice.png"
    },
    {
        "name": "Panang Curry",
        "description": "Thick, salty, and sweet red curry with kaffir lime leaves and peanuts. Creamier than red curry.",
        "price": "16.50",
        "category": "Curry",
        "image_data": "/images/panang_curry.png"
    },
    {
        "name": "Largo Spicy Beef Salad",
        "description": "Grilled sliced beef tossed with lime juice, chili flakes, mint, and toasted rice powder. Very spicy.",
        "price": "18.00",
        "category": "Salad",
        "image_data": "/images/spicy_beef_salad.png"
    },
    {
        "name": "Basil Stir Fry (Pad Kra Pao)",
        "description": "Spicy minced pork or chicken stir-fried with holy basil, garlic, and chilies. Topped with a fried egg.",
        "price": "15.00",
        "category": "Main",
        "image_data": "/images/pad_kra_pao.png"
    },
    {
        "name": "Thai Iced Tea",
        "description": "Sweet Ceylon tea brewed with spices and topped with evaporated milk. Iconic orange drink.",
        "price": "5.00",
        "category": "Drink",
        "image_data": "/images/thai_iced_tea.png"
    },
    {
        "name": "Coconut Ice Cream",
        "description": "Homemade coconut milk ice cream served with roasted peanuts and chocolate syrup.",
        "price": "7.50",
        "category": "Dessert",
        "image_data": "/images/coconut_ice_cream.png"
    },
    {
        "name": "Fish Cakes (Tod Mun Pla)",
        "description": "Fried fish paste mixed with red curry paste and long beans. Chewy and spicy, served with cucumber dip.",
        "price": "11.50",
        "category": "Appetizer",
        "image_data": "/images/fish_cakes.png"
    },
    {
        "name": "Khao Soi",
        "description": "Northern Thai curry noodle soup with egg noodles, pickled mustard greens, and crispy noodles on top.",
        "price": "16.00",
        "category": "Noodles",
        "image_data": "/images/khao_soi.png"
    },
    {
        "name": "Crab Fried Rice",
        "description": "Premium fried rice with chunks of real crab meat, egg, and spring onions.",
        "price": "22.00",
        "category": "Rice",
        "image_data": "/images/crab_fried_rice.png"
    },
    {
        "name": "Crispy Pork Belly with Kale",
        "description": "Stir-fried Chinese kale with crunchy deep-fried pork belly in oyster sauce and garlic.",
        "price": "17.50",
        "category": "Main",
        "image_data": "/images/crispy_pork_belly.png"
    },
    {
        "name": "Garlic Pepper Prawns",
        "description": "Deep-fried large prawns topped with crispy garlic and black pepper sauce.",
        "price": "24.00",
        "category": "Main",
        "image_data": "/images/garlic_pepper_prawns.png"
    },
    {
        "name": "Fresh Summer Rolls",
        "description": "Rice paper rolls filled with shrimp, lettuce, mint, and vermicelli. Served with Hoisin peanut dip.",
        "price": "9.00",
        "category": "Appetizer",
        "image_data": "/images/fresh_summer_rolls.png"
    },
    {
        "name": "Red Curry Roast Duck",
        "description": "Special red curry with roasted duck breast, pineapple, lychee, and tomatoes.",
        "price": "21.00",
        "category": "Curry",
        "image_data": "/images/red_curry_roast_duck.png"
    },
    {
        "name": "Steam Fish with Lime",
        "description": "Whole sea bass steamed with fresh garlic, chili, and lime juice dressing. Very spicy and sour.",
        "price": "28.00",
        "category": "Main",
        "image_data": "/images/steam_fish_with_lime.png"
    },
    {
        "name": "Morning Glory Stir Fry",
        "description": "Water spinach stir-fried with soybean paste, garlic, and chilies on high flame.",
        "price": "12.00",
        "category": "Side",
        "image_data": "/images/morning_glory_stir_fry.png"
    },
    {
        "name": "Singha Beer",
        "description": "Premium Thai lager beer.",
        "price": "6.00",
        "category": "Drink",
        "image_data": "/images/singha_beer.png"
    },
    {
        "name": "Lemongrass Juice",
        "description": "Refreshing herbal drink made from mild lemongrass syrup.",
        "price": "4.50",
        "category": "Drink",
        "image_data": "/images/lemongrass_juice.png"
    },
    {
        "name": "Banana Roti",
        "description": "Fried crispy pancake filled with banana slices and drizzled with condensed milk.",
        "price": "8.50",
        "category": "Dessert",
        "image_data": "/images/banana_roti.png"
    },
    {
        "name": "Hot & Sour Seafood Soup (Po Tak)",
        "description": "Clear spicy soup with mixed seafood (shrimp, squid, mussels) and holy basil.",
        "price": "20.00",
        "category": "Soup",
        "image_data": "/images/hot_sour_seafood_soup.png"
    },
    {
        "name": "Crying Tiger Beef",
        "description": "Grilled marinated sirloin steak served with spicy tamarind dipping sauce (Nam Jim Jaew).",
        "price": "23.00",
        "category": "Main",
        "image_data": "/images/crying_tiger_beef.png"
    }
]

async def seed():
    print("Starting database seed...")
    async with AsyncSessionLocal() as db:
        for i, item_data in enumerate(MENU_ITEMS):
            print(f"Adding item {i+1}/{len(MENU_ITEMS)}: {item_data['name']}")
            
            # 1. Create Menu Item
            new_item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                price=Decimal(item_data["price"]),
                category=item_data["category"],
                image_data=item_data.get("image_data")
            )
            db.add(new_item)
            await db.flush() # Get ID

            # 2. Generate Embedding
            # Create a rich representation for the vector search
            content_chunk = f"Name: {item_data['name']}. Category: {item_data['category']}. Description: {item_data['description']}."
            embedding_vector = RAGService.generate_embedding(content_chunk)

            # 3. Save Embedding
            new_embedding = MenuEmbedding(
                item_id=new_item.id,
                embedding=embedding_vector,
                content_chunk=content_chunk
            )
            db.add(new_embedding)
        
        await db.commit()
    print("Database seed completed successfully!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())
