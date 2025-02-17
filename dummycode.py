import shelve
import os

# Path to the products database
DB_PATH_PRODUCTS = "db/products"

a = {
    "1": {
        "id": 1,
        "name": f"Y2K Camisole",
        "customer_id": "1",
        "tags": [f"Women"],
        "description": f"Its a top",
        "image_url": f"/uploads/1.jpeg",
        "wishlisted_users": {}
    },
    "2": {
        "id": 2,
        "name": f"Yoga Pants",
        "customer_id": "2",
        "tags": [f"Women"],
        "description": f"Its pants",
        "image_url": f"/uploads/2.jpeg",
        "wishlisted_users": {}
    },
    "3": {
        "id": 3,
        "name": f"Denim Skirt",
        "customer_id": "3",
        "tags": [f"Women"],
        "description": f"Its a skirt",
        "image_url": f"/uploads/3.jpeg",
        "wishlisted_users": {}
    },
    "4": {
        "id": 4,
        "name": f"Parka",
        "customer_id": "1",
        "tags": [f"Women"],
        "description": f"Its a parka",
        "image_url": f"/uploads/4.jpeg",
        "wishlisted_users": {}
    },
    "5": {
        "id": 5,
        "name": f"Navy Polo T",
        "customer_id": "1",
        "tags": [f"Women"],
        "description": f"Its a Polo T",
        "image_url": f"/uploads/5.jpeg",
        "wishlisted_users": {}
    },
    "6": {
        "id": 6,
        "name": f"Button Up Shirt",
        "customer_id": "1",
        "tags": [f"Women"],
        "description": f"Its a shirt",
        "image_url": f"/uploads/6.jpeg",
        "wishlisted_users": {}
    }
}

# Overwrite the products database with new data
with shelve.open(DB_PATH_PRODUCTS, writeback=True) as products_db:
    products_db.clear()  # Remove existing data
    products_db.update(a)  # Insert new data
    print("✅ Successfully replaced products.db with new data!")