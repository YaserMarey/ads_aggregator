from utilities import util
from dataaccess import dao
from langdetect import detect
def update_lang():
    db = dao.get_db_production()
    products = db.products.find({'language_override': {'$exists': False}})
    for product in products:
        try:
            if detect(product['description']) == 'ar':
                language_override = 'arabic'  # langdetect returns ISO 639-1 codes,
            else:
                language_override = 'english'
            # where mongo expects ISO 639-3 codes for Arabic
        except:
            util.loginfo("Coudn't detect language falling back to English, ad_page_link" + product['ad_id']);
            language_override = 'english'

        brands = dao.get_brands()

        try:
            for brand in brands:
                if brand['_id'] == product['brand']:
                    if language_override == "arabic":
                        brand_name = brand.get("name_ar")
                        break;
                    else:
                        brand_name = brand.get("name")
        except:
            util.loginfo("Skipping one item, error parsing brand, ad_data_link" + product['ad_id']);
            continue
        if brand == None:
            util.loginfo("Skipping one item, brand is not found, ad_data_link" + product['ad_id']);
            continue

        product['language_override'] = language_override
        product['tags'] = brand_name

        db.get_collection('products').save(product)

if __name__ == '__main__':
    update_lang()
