# coding=utf-8
import json
import re
import string
import sys
from datetime import datetime
from random import randint
from time import sleep

from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from langdetect import detect

from dataaccess import dao
from settings import settings
from utilities import util

reload(sys)
sys.setdefaultencoding('utf-8')


# https://carmudi.com.sa/ar/api/web_listing?appliedFilter=%7B%22count%22:20,%22page%22:" + str(i)

# ad entry in the list of ads
# {"id": 6676, "user_id": 132018, "seller_type_id": 3, "make": "Toyota", "model": "Hiace", "temp_trim": "",
#  "trim": "Mid Roof Panel Van Super LWB", "price": "67000",
#  "year": "2013", "mileage": "156000", "engine": "2700", "location": "Jeddah", "fuel": "Petrol",
#  "shortlist": 0, "featured": 1},


# ad link
# example: https: // carmudi.com.sa / ar / api / product_details?lang = ar & product_id = 6676

# {"status": "success",
#  "products": {"user": [], "id": 6676, "seller_type_id": 3, "make": "Toyota", "model": "Hiace",
#               "mileage": "156000", "price": "67000", "trim": "Mid Roof Panel Van Super LWB",
#               "temp_trim": "", "year": "2013", "engine": "2700", "power": "149", "specs": "GCC",
#               "body_type": "Wagon", "location": "Jeddah", "transmission": "Manual", "fuel": "Petrol",
#               "doors": "4\/5", "condition": "Used", "color": "White",
#               "description": "\u062a\u0648\u064a\u0648\u062a\u0627 \u0647\u0627\u064a \u0627\u0633 \u0628\u0636\u0627\u0639\u0647 2013 \u0645\u0633\u062a\u0639\u0645\u0644\u0629 \u0644\u0644\u0628\u064a\u0639. \u0646\u0627\u0642\u0644 \u0627\u0644\u062d\u0631\u0643\u0629 \u0639\u0627\u062f\u064a \u0648\u0627\u0644\u0645\u0633\u0627\u0641\u0629 \u0627\u0644\u0645\u0642\u0637\u0648\u0639\u0629 \u0639\u0646\u062f \u0639\u0631\u0636 \u0627\u0644\u0633\u064a\u0627\u0631\u0629 \u0644\u0644\u0628\u064a\u0639 \u0647\u064a 156000 \u0644\u0648\u0646 \u0627\u0644\u0633\u064a\u0627\u0631\u0629 \u0627\u0644\u062e\u0627\u0631\u062c\u064a \u0623\u0628\u064a\u0636 \u0627\u0644\u0633\u064a\u0627\u0631\u0629 \u0645\u062a\u0648\u0627\u062c\u062f\u0629 \u062d\u0627\u0644\u064a\u0627 \u0641\u064a \u062c\u062f\u0629 \u0628\u0645\u0628\u0644\u063a 67,000",
#               "created_at": "24th Oct 2017", "featured": 1, "shortlist": false,
#               "images": ["d090d96847c846e6810980e8db3f65c7.jpeg", "ebdc05279cf736333099f6b0c8d9665d.jpeg",
#                          "fa223976232380ee1f483b65adc67413.jpeg", "5f5e0a387d60e978e3b4e7ea74f7b6ec.jpeg"],
#               "badges": [], "features": []}}


# ad image number 0
# https://s3-us-west-2.amazonaws.com/carmudi-site/products/360/2014-bmw-7-series-200000-6374-150712873535.png

def calculate_tags(brand, model, ad, models):
    tags = ""
    if brand != None:
        tags += ' ' + u' '.join(brand.get('name_ar'))
        tags += ' ' + u' '.join(brand.get('name_en'))

    if util.find_model_(model, models) != None:
        tags += ' ' + u' '.join(util.find_model_(model, models).get('name_ar'))
        tags += ' ' + u' '.join(util.find_model_(model, models).get('name_en'))
    if ad['year'] != 0:
        tags += ' ' + str(ad['year'])
    if ad['location'] != "":
        tags += ' ' + util.find_location(ad['location'])
    if ad['color'] != "":
        tags += ' ' + util.find_color(ad['color'])
    if ad['ad_cat'] != "":
        tags += ' ' + u' '.join(settings['ad_cats'][ad['ad_cat']])
    return tags


# TODO refactor this method
def read(number_of_pages, debug, brands, models, classifier):
    skipped = 0
    SOURCE = "carmudi.com.sa"
    count_of_ads_added = 0
    count_of_ads_updated = 0
    counter_of_ads = 0
    already_loaded_counter = 0
    for i in range(1, number_of_pages):
        util.loginfo(">>Page #" + str(i))
        page_data = util.download_file(settings[SOURCE]['base_url'] +
                                       "/ar/api/web_listing?appliedFilter=%7B%22count%22:20,%22page%22:" + str(
            i) + "%7D",
                                       settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])
        if (page_data == None):
            continue
        if (len(json.loads(page_data)['products']) == 0):
            continue
        # for item in catalog_items:
        for item in json.loads(page_data)['products']:
            counter_of_ads += 1
            util.loginfo(">Ad # " + str(counter_of_ads))

            # 1- ad_data_link, mandatory
            try:
                ad_data_link = "/ar/api/product_details?lang=ar&product_id=" + str(item['id']);
            except:
                util.loginfo("Skipping one item, error parsing ad_data_link")
                skipped += 1
                continue

            ad_data_content = util.download_file(settings[SOURCE]['base_url'] + ad_data_link,
                                                 settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])

            if ad_data_content == None:
                util.loginfo("Skipping one item, error downloading ad_page, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            ad_json = json.loads(ad_data_content)['products'];

            # 2- ad_update_date, mandatory
            try:
                for c in {'th', 'nd', 'st'}:
                    ad_json['created_at'] = ad_json['created_at'].replace(c, '')
                ad_update_date = datetime.strptime(ad_json['created_at'], "%d %b %Y")
            except:
                util.loginfo("Skipping one item, error parsing ad_update_date, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 3- ad_id, mandatory
            try:
                ad_id = ad_json['id']
            except:
                util.loginfo("Skipping one item, error parsing ad_id, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 4- title, mandatory
            try:
                title = ad_json['make'] + " " + ad_json['model'] + " " + ad_json['year']
            except:
                util.loginfo("Skipping one item, error parsing title, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 5- description, mandatory
            try:
                description = BeautifulSoup(ad_json['description'], 'html.parser').text  # remove all tags
            except:
                util.loginfo("Skipping one item, error parsing body, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 6- brand, mandatory because the ad page link depends on it
            try:
                brand = util.find_brand(ad_json['make'], brands)
            except:
                util.loginfo("Skipping one item, error parsing brand, ad_data_link" + ad_data_link);
                continue
            if brand == None:
                util.loginfo("Skipping one item, brand is not found, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 7- model, mandatory
            try:
                model, found = util.find_model(ad_json['model'].capitalize(), models);
            except:
                util.loginfo("Skipping one item, error parsing model, ad_data_link" + ad_data_link);
                skipped += 1
                continue
                # model = ""
            # if found == False: model = ""

            # 8- year, mandatory
            try:
                year = int(util.toArabicNumerals(ad_json['year']))
            except:
                util.loginfo("Skipping one item, error parsing year, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 9- body_type, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                body_type = ad_json['body_type']
            except:
                body_type = ""

            # 10- mileage, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                mileage = re.findall(r'\d+', ad_json['mileage'])[0]
            except:
                mileage = 0

            # 11- engine, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                engine = re.findall(r'\d+', ad_json['engine'])[0]
            except:
                engine = 0

            # 12- power, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                power = re.findall(r'\d+', ad_json['power'])[0]
            except:
                power = 0

            # 13- specs[GCC,EU..etc], optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                specs = ad_json['specs']
            except:
                specs = ""

            # 14- transmission, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                transmission = ad_json['transmission']
            except:
                transmission = ""

            # 15- fuel [Gasline/Disel], optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                fuel = ad_json['fuel']
            except:
                fuel = ""

            # 16- condition [Used/New], optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                condition = ad_json['condition']
            except:
                condition = ""

            # 17- color, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                color = ad_json['color']
            except:
                color = ""

            # 18- price, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                price = ad_json['price']
                price_numeric_value = int(
                    (filter(lambda x: x in set(string.printable), price)).strip('.. ').replace(',', ''))
            except:
                util.loginfo("Skipping one item, error parsing price, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 19- image_link, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                image_link = "https://s3-us-west-2.amazonaws.com/carmudi-site/products/360/" + ad_json['images'][0]
            except:
                util.loginfo("Skipping one item, error parsing image_link, ad_data_link" + ad_data_link);
                skipped += 1
                continue

            # 20- location, optional, here we chose to skip in case we couldn't parse to avoid courrpt data sneak to shofle_web
            try:
                location = ad_json['location'].capitalize()
            except:
                location = ""

            # 21- ad_page_link
            ad_page_link = "/ar/product-detail/" + str(year) + "-" + brand['name'].lower() + "-" + \
                           model.lower() + "-in-" + location.lower() + "-" + str(price) + "-" + str(ad_id)

            try:
                if detect(description) == 'ar':
                    language_override = 'arabic'  # langdetect returns ISO 639-1 codes,
                else:
                    language_override = 'english'
                # where mongo expects ISO 639-3 codes for Arabic
            except:
                util.loginfo("Coudn't detect language falling back to English, ad_page_link" + ad_page_link);
                language_override = 'english'

            brand_name = ""

            ad_to_save_or_update = {
                'source': SOURCE,
                'ad_id': ad_id,
                'language_override': language_override,
                'ad_page_link': settings[SOURCE]['base_url'] + ad_page_link,
                'last_update': ad_update_date,
                'title': title,
                'nameLower': title.lower(),
                'description': description,
                'brand': ObjectId(brand.get('_id')),
                'model': model,
                'year': year,
                'body_type': body_type,
                'mileage': mileage,
                'engine': engine,
                'power': power,
                'specs': specs,
                'transmission': transmission,
                'fuel': fuel,
                'condition': condition,
                'color': color,
                'price': price,
                'image_link': image_link,
                'location': location,
                'active': True,
                'keyFeatures': [],
                'features': [],
                'tags': brand_name,
                'variants': [{'image': image_link,
                              'price': price_numeric_value}]}

            # is_raw_ad = True indicates that ad need to be processed to extract features
            # ready ad for classification should be in the formate of: ([fet1,fet2....],cat)
            vote, confidence = classifier.classify(ad_to_save_or_update, is_raw_ad=True)
            # sleep(10)
            if vote != 'INV':
                if confidence >= 0.3:
                    if vote == 'SAL':
                        ad_to_save_or_update['ad_cat'] = vote
                    else:
                        if brand == "": del ad_to_save_or_update['brand']
                        ad_to_save_or_update['ad_cat'] = vote
                else:
                    util.loginfo("Skipping one item, not confident classification, ad_data_link" + ad_page_link);
                    skipped += 1
                    continue
            else:
                util.loginfo("Skipping one item, classified INVALID, ad_data_link" + ad_page_link);
                skipped += 1
                continue

            ad_to_save_or_update['tags'] = calculate_tags(brand, model, ad_to_save_or_update, models)

            # TODO rename all products to ads
            if dao.product_exists_in_db({'source': SOURCE, 'ad_id': ad_id}):
                if dao.product_exists_in_db(ad_to_save_or_update):
                    util.loginfo("source " + SOURCE + " ad_id " + str(ad_id) + " is already in the database!");
                else:
                    util.loginfo("updating " + SOURCE + ad_data_link);
                    dao.update([ad_to_save_or_update]);
                    count_of_ads_updated += 1
            else:
                util.loginfo("adding " + SOURCE + ad_data_link);
                dao.add_list_to_db([ad_to_save_or_update])
                count_of_ads_added += 1

            if (settings['ENVIRONMENT'] == "Production"):
                wait = randint(5, 20)
                util.loginfo("waiting for " + str(wait) + " before reading next item");
                sleep(wait)

    return count_of_ads_added, count_of_ads_updated, skipped, counter_of_ads
