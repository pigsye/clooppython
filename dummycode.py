import shelve
import os

# Define the database path
DB_FOLDER = os.path.join(os.path.dirname(__file__), "db")
DB_PATH_PRODUCTS = os.path.join(DB_FOLDER, "products")

def read_products_db():
    """Read and print all entries in products.db"""
    try:
        with shelve.open(DB_PATH_PRODUCTS) as db:
            if not db:
                print("⚠️ No products found in the database.")
                return
            
            print("📦 All Products in Database:\n")
            for product_id, product_data in db.items():
                print(f"🆔 Product ID: {product_id}")
                print(f"📌 Name: {product_data.get('name', 'N/A')}")
                print(f"👤 Customer ID: {product_data.get('customer_id', 'N/A')}")
                print(f"🏷️ Tags: {', '.join(product_data.get('tags', []))}")
                print(f"❤️ Wishlisted Users: {product_data.get('wishlisted_users', {})}")
                print(f"🖼️ Image URL: {product_data.get('image_url', 'No image provided')}")
                print("=" * 40)
    
    except Exception as e:
        print(f"❌ Error reading products.db: {e}")

# Run the function
if __name__ == "__main__":
    read_products_db()