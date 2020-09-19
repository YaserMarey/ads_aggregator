# coding=utf-8
import sys
from datetime import datetime, timedelta
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


def calculate_tags(brand, model, ad, models):
    tags = ""
    if type(brand) == ObjectId: brand = dao.get_brand(brand)
    if brand != None and brand != '':
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


def read(number_of_pages, debug, brands, models, classifier):
    skipped = 0
    SOURCE = "haraj.com.sa"
    count_of_ads_added = 0
    count_of_ads_updated = 0
    counter_of_ads = 0
    already_loaded_counter = 0
    for i in range(1, number_of_pages):
        util.loginfo("number of pages is" + str(number_of_pages))
        util.loginfo(">>Page #" + str(i))
        page_content = util.download_file(settings[SOURCE]['base_url'] +
                                          "/jsonGW/getadsx.php?link=tags/%D8%AD%D8%B1%D8%A7%D8%AC%20%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%B1%D8%A7%D8%AA/" + str(
            i) + "&_=1512689531762",
                                          settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])
        if (page_content == None):
            continue

        catalog_listing_items = BeautifulSoup(page_content, 'html.parser').find_all('div', class_="adx")

        # for item in catalog_items:
        for item in catalog_listing_items:
            counter_of_ads += 1
            util.loginfo(">Ad # " + str(counter_of_ads))
            try:
                ad_page_link = (item.find_all('a')[0].attrs['href']).strip();
            except:
                util.loginfo("Skipping one item, error parsing ad_page_link")
                skipped += 1
                continue

            ad_page_content = util.download_file(ad_page_link,
                                                 settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])

            if ad_page_content == None:
                skipped += 1
                continue

            try:
                ad_page_content = BeautifulSoup(ad_page_content, 'html.parser').find_all('div', class_="pageContent")[
                    0];
            except:
                util.loginfo("Skipping one item, error parsing ad_key_details, ad_page_content" + ad_page_link);
                skipped += 1
                continue

            try:
                time_text_ary = ad_page_content.find_all('div', class_="adxExtraInfoPart")[2].text.strip().split()
                if len(time_text_ary) == 3:
                    ad_update_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
                elif len(time_text_ary) == 5 or len(time_text_ary) == 6:
                    if time_text_ary[2].find(u'ساعه') != -1 \
                            or time_text_ary[1].find(u'ساعه') != -1 \
                            or time_text_ary[1].find(u'يوم') != -1:
                        ad_update_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
                    elif time_text_ary[2].find(u'يوم') != -1:
                        ad_update_date = datetime.today() - timedelta(days=int(time_text_ary[1]))
                        ad_update_date = datetime(ad_update_date.today().year, ad_update_date.today().month,
                                                  ad_update_date.today().day)
                    else:
                        ad_update_date = None
                else:
                    ad_update_date = None
                if ad_update_date == None:
                    util.loginfo("Skipping one item, error parsing ad_update_date, ad_page_link" + ad_page_link);
                    skipped += 1
                    continue
            except:
                util.loginfo("Skipping one item, error parsing ad_update_date, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                ad_id = ad_page_content.find_all('div', class_="adxExtraInfoPart")[3].text.strip().strip('#')
            except:
                util.loginfo("Skipping one item, error parsing ad_id, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                title = ad_page_content.find_all('h3')[0].text.strip().split()[1]
            except:
                util.loginfo("Skipping one item, error parsing title, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                # desc_items = strip_tags(ad_page_content.find_all('div', class_="adxBody")[0].next.strip("<br>").strip('»'))
                description = BeautifulSoup(ad_page_content.find_all('div', class_="adxBody")[0].text,
                                            'html.parser').text.strip()  # remove all tags
            except:
                util.loginfo("Skipping one item, error parsing body, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                title_desc_text_ary = (title + " " + description).split()
                for w in title_desc_text_ary:
                    brand = util.find_brand(w, brands)
                    if brand != None: break;
            except:
                brand = ""

            if brand == None: brand = ""

            try:
                for w in title_desc_text_ary:
                    model, found = util.find_model(w, models)
                    if found == True: break
            except:
                model = ""

            if found == False: model = ""

            try:
                year = int(ad_page_content.find_all('meta')[0].attrs['content'])
            except:
                year = 0

            try:
                body_type = "";
            except:
                body_type = ""

            try:
                mileage = 0;
            except:
                mileage = 0

            try:
                engine = 0;
            except:
                engine = 0

            try:
                power = 0
            except:
                power = 0

            try:
                specs = ""
            except:
                specs = ""

            try:
                transmission = "";
            except:
                transmission = ""

            try:
                fuel = "";
            except:
                fuel = ""

            try:
                condition = ad_page_content.find_all('meta')[1].attrs['content']
            except:
                condition = ""

            try:
                color = "";
            except:
                color = ""

            try:
                price = 0
                price_numeric_value = 0
            except:
                price = 0
                price_numeric_value = 0

            try:
                # $('.adxBody>img')[0]['src']
                image_link = ad_page_content.find('div', class_='adxBody').find_all('img')[0].attrs['src']
            except:
                util.loginfo("Skipping one item, error parsing image_link, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                location = ad_page_content.find_all('div', class_="adxExtraInfoPart")[0].text.strip()
            except:
                location = 0

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

            # TODO add tags field to the ads, this tags will take priority in search and will contian
            # TODO brand, model, color, engine ...etc all the features that I would to search with and I
            # TODO will need to categorize with as well, possibly I will make them lookups.

            ad_to_save_or_update = {
                'source': SOURCE,
                'ad_id': ad_id,
                'language_override': language_override,
                'ad_page_link': ad_page_link,
                'last_update': ad_update_date,
                'title': title,
                'nameLower': title.lower(),
                'description': description,
                'brand': brand if brand == "" else ObjectId(brand.get('_id')),
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
                'keyFeatures': [],  # TODO remove this, not used
                'features': [],  # TODO remove this, not used
                'tags': brand_name,
                'variants': [{'image': image_link,
                              'price': price_numeric_value}]
            }

            # is_raw_ad = True indicates that ad need to be processed to extract features
            # ready ad for classification should be in the formate of: ([fet1,fet2....],cat)
            vote, confidence = classifier.classify(ad_to_save_or_update, is_raw_ad=True)
            # sleep(5)
            # In Haraj and in all Readers, Brand is mandatory only in SAL, in Haraj, in SAL, if model is not found
            # the origianl text value from the ad is accepted, also "" is accpted as a model from Haraj
            # all this is due to large noise in data, TODO link brands to models, collect varaious ways of
            # writting models and brands in both arabic and english to enhance matching, and then reject
            # "" as a model, TODO add year as a mandatory attribute to SAL in Haraj and in all other readers
            if vote != 'INV':
                if confidence >= 0.6:  # Confidence is a little highr for Haraj due to high rate of noise
                    if vote == 'SAL':
                        # must have brand
                        if ad_to_save_or_update['brand'] == "":
                            if ad_to_save_or_update['model'] != "":
                                util.logdebug(
                                    "Brand is empty, and model is not, now trying to resolve brand using model")
                                brand = find_brand_by_model(ad_to_save_or_update['model'], models)
                                if brand != "":
                                    util.logdebug("------------- >>> Found brand by model ")
                                    ad_to_save_or_update['brand'] = brand
                                else:
                                    util.loginfo(
                                        "Skipping one item, SAL and brand is not found, ad_page_link" + ad_page_link);
                                    skipped += 1
                                    continue
                            else:
                                util.loginfo(
                                    "Skipping one item, SAL and brand is not found, ad_page_link" + ad_page_link);
                                skipped += 1
                                continue

                        # must have model
                        # if ad_to_save_or_update['model'] == "":
                        #     util.loginfo("Skipping one item, SAL and model is not found, ad_page_link" + ad_page_link);
                        #     skipped += 1
                        #     continue

                        if ad_to_save_or_update['brand'] != "":
                            if ad_to_save_or_update['model'] != "":
                                if (not brand_and_model_match(brand, model)):
                                    util.loginfo(
                                        "Skipping one item, error model and barnd don't match, ad_page_link" + ad_page_link);
                                    skipped += 1
                                    continue
                        else:
                            util.loginfo(
                                "Skipping one item, error model and barnd don't match, ad_page_link" + ad_page_link);
                            skipped += 1
                            continue

                            # engine = predicter.query_engin_prediction_model([ad_to_save_or_update])
                            # print "Predicted Engine value is ", str(engine)

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

                # must have year
                if ad_to_save_or_update['year'] == 0:
                    util.loginfo("Skipping one item, SAL and year is not found, ad_page_link" + ad_page_link);
                    skipped += 1
                    continue

            ad_to_save_or_update['tags'] = calculate_tags(brand, model, ad_to_save_or_update, models)

            # TODO rename all products to ads
            if dao.product_exists_in_db({'source': SOURCE, 'ad_id': ad_id}):
                if dao.product_exists_in_db(ad_to_save_or_update):
                    util.loginfo("source " + SOURCE + " ad_id " + str(ad_id) + " is already in the database!");
                else:
                    util.loginfo("updating " + SOURCE + ad_page_link);
                    dao.update([ad_to_save_or_update]);
                    count_of_ads_updated += 1

            else:
                util.loginfo("adding " + SOURCE + ad_page_link);
                dao.add_list_to_db([ad_to_save_or_update])
                count_of_ads_added += 1

            if (settings['ENVIRONMENT'] == "Production"):
                wait = randint(5, 20)
                util.loginfo("waiting for " + str(wait) + " before reading next item");
                sleep(wait)

    return count_of_ads_added, count_of_ads_updated, skipped, counter_of_ads


# TODO link models and brands directly in the database instead of using this
def brand_and_model_match(brand, model):
    if len(dao.get_ad_by_query({'model': model, 'brand': brand})) >= 1:
        return True
    else:
        return False


def find_brand_by_model(model_name, models):
    model, found = util.find_model(model_name, models)
    if found:
        if len(dao.get_ad_by_query({'model': model})) >= 1:
            if len(dao.get_ad_by_query({'$and': [{'model': model}, {'brand': {'$exists': 'True'}}]})) != 0:
                return dao.get_ad_by_query({'$and': [{'model': model}, {'brand': {'$exists': 'True'}}]})[0]['brand']
            else:
                return ""
        else:
            return ""
    else:
        return ""
