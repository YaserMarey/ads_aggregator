# coding=utf-8

from utilities import util
from pymongo import MongoClient
from settings import settings
from bson.objectid import ObjectId
def get_db(env=settings['ENVIRONMENT']):
    db = None
    try:
        client = MongoClient(settings[env]['Mongo']['DbClient'])
        db = client.get_database(settings[env]['Mongo']['DbName'])
    except Exception as e:
        util.logerr('Error connecting to database or not reachable')
    return db

def add_ad_to_db(item):
    db = get_db()
    try:
        db.products.insert_one(item)
        util.loginfo('ad inserted successfully')
    except Exception as e:
        util.logerr(str(e))

def get_ad():
    db = get_db()
    try:
        ad = db.products.find_one()
        util.loginfo('ad retrived successfully')
    except Exception as e:
        util.logerr(str(e))
    return ad

def get_ad_by_query(q):
    db = get_db()
    try:
        ads = list(db.products.find(q))
        util.loginfo('ads retrived successfully')
    except Exception as e:
        util.logerr(str(e))
    return ads

def get_brands():
    db = get_db()
    try:
        brands = list(db.brands.find({'active': True}))
        util.loginfo('brands retrived successfully')
    except Exception as e:
        util.logerr(str(e))
    return brands

def get_brand(brand_id):
    db = get_db()
    try:
        if db.brands.find({'_id':ObjectId(brand_id),'active': True}).count() != 0:
            return db.brands.find({'_id': ObjectId(brand_id), 'active': True})[0]
    except Exception as e:
        util.logerr(str(e))
    return None

def get_models():
    db = get_db()
    try:
        models = list(db.models.find({'active': True}))
        util.loginfo('models retrived successfully')
    except Exception as e:
        util.logerr(str(e))
    return models

def add_list_to_db(item_list):
    db = get_db()
    try:
        db.products.insert(item_list)
        util.loginfo('ad(s) inserted successfully')
    except Exception as e:
        util.logerr(str(e))

def product_exists_in_db(item):
    db = get_db()
    if db.products.find(item).count() != 0:
        return True
    else:
        return False

def update(items):
    db = get_db()
    for item in items:
        try:
            db.products.update(
                {
                    'source': item.get('source'),
                    "ad_id": item.get('ad_id')
                },
                {
                    "$set": {
                            'language_override': item.get('language_override'),
                            'ad_page_link': item.get('ad_page_link'),
                            'last_update': item.get('last_update'),
                            'title': item.get('title'),
                            'description': item.get('description'),
                            'brand': item.get('brand'),
                            'model': item.get('model'),
                            'year': item.get('year'),
                            'body_type': item.get('body_type'),
                            'mileage': item.get('mileage'),
                            'engine': item.get('engine'),
                            'power': item.get('power'),
                            'specs': item.get('specs'),
                            'transmission': item.get('transmission'),
                            'fuel': item.get('fuel'),
                            'condition': item.get('condition'),
                            'color': item.get('color'),
                            'price': item.get('price'),
                            'image_link': item.get('image_link'),
                            'location': item.get('location'),
                            'active': item.get('active'),
                            'keyFeatures': item.get('keyFeatures'),
                            'features': item.get('features'),
                            'tags':item.get('tags'),
                            'variants': item.get('variants'),
                            'ad_cat': item.get('ad_cat')
                    }
                }
            )
            util.loginfo("ad(s) updated successfully")
        except Exception as e:
            util.logerr(str(e))

def delete(item):
    db = get_db()
    try:
        db.products.delete_many({'source': item.get('source'),"ad_id": item.get('ad_id')})
        util.loginfo('ad deleted successful')
    except Exception as e:
        util.logerr(str(e))

def deactivate(item):
    db = get_db()
    try:
        db.products.update({'source': item.get('source'),"ad_id": item.get('ad_id')}, {'$set': {'active': False}})
        util.loginfo('ad is deactivated successful')
    except Exception as e:
        util.logerr(str(e))