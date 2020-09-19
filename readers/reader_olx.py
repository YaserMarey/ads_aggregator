# coding=utf-8
import string
from settings import settings
from random import randint
from time import sleep
from datetime import datetime
from bson.objectid import ObjectId
from langdetect import detect
from dataaccess import dao
from bs4 import BeautifulSoup


from utilities import util

def calculate_tags(brand, model, ad, models):
    tags = ""
    if brand != None:
        tags += ' ' + u' '.join(brand.get('name_ar'))
        tags += ' ' + u' '.join(brand.get('name_en'))

    if util.find_model_(model,models) != None:
        tags += ' ' + u' '.join(util.find_model_(model,models).get('name_ar'))
        tags += ' ' + u' '.join(util.find_model_(model,models).get('name_en'))
    if ad['year'] != 0:
        tags += ' ' + str(ad['year'])
    if ad['location'] !="":
        tags += ' ' + util.find_location(ad['location'])
    if ad['color'] != "":
        tags += ' ' + util.find_color(ad['color'])
    if ad['ad_cat'] != "":
        tags += ' ' + u' '.join(settings['ad_cats'][ad['ad_cat']])
    return tags

# TODO refactor this method
def read(number_of_pages, debug, brands, models, classifier):
    skipped = 0
    SOURCE = "olx.sa.com"
    count_of_ads_added=0
    count_of_ads_updated=0
    counter_of_ads = 0
    already_loaded_counter = 0
    for i in range(1, number_of_pages):
        util.loginfo(">>Page #" + str(i))
        page_content = util.download_file(settings[SOURCE]['base_url'] + "/vehicles/cars/?page=" + str(i) ,
                                          settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])
        if (page_content == None):
            continue

        catalog_listing_items = BeautifulSoup(page_content, 'html.parser').find_all('div', class_="ads__item")

        # TODO add ad title, ad link at its source, update date, make, model, year, location, millage, body type, seller type, options,
        # TODO add transmission, asked price, cash or installment, license validity, number of prev owners, main image, additional images, description
        # TODO decide which are mandatory and which are optional, in case it is optional decide about default data to fill input
        for item in catalog_listing_items:
            counter_of_ads+=1
            util.loginfo(">Ad # " + str(counter_of_ads))
            try:
                #TODO language should be configurable

                ad_page_link = item.find('a', class_="ads__item__title").attrs['href'];
            except:
                util.loginfo("Skipping one item, error parsing ad_page_link")
                skipped +=1
                continue

            ad_page_content = util.download_file(ad_page_link,
                                                 settings[settings['ENVIRONMENT']][SOURCE]['DATA_FOLDER_PATH'])

            if ad_page_content == None:
                continue

            try:
                ad_key_details = BeautifulSoup(ad_page_content, 'html.parser').find_all('div', class_="clr offerbody")[0];
            except:
                util.loginfo("Skipping one item, error parsing ad_key_details, ad_page_link"+ ad_page_link);
                skipped += 1
                continue
            try:
                ad_update_date = ad_key_details.find_all('span', class_="pdingleft10 brlefte5")[0].next.strip().split(" ")
                ad_update_date = datetime.strptime(ad_update_date[7][:-1] + "-" + util.find_month(ad_update_date[6]) + "-" + ad_update_date[5],"%Y-%m-%d")
            except:
                util.loginfo("Skipping one item, error parsing ad_update_date, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                ad_id = ad_key_details.find_all('span', class_="rel inlblk")[0].next.strip();
            except:
                util.loginfo("Skipping one item, error parsing ad_id, ad_page_link" + ad_page_link);
                skipped += 1
                continue

            try:
                title = BeautifulSoup((item.find_all('a', class_="ads__item__title")[0].text).strip(), 'html.parser').text
            except:
                util.loginfo("Skipping one item, error parsing title, ad_page_link"+ ad_page_link);
                skipped += 1
                continue

            try:
                description = BeautifulSoup(ad_key_details.find_all('p', class_="pding10 lheight20 large")[0].text.strip(), 'html.parser').text #remove all tags
            except:
                util.loginfo("Skipping one item, error parsing body, ad_page_link"+ ad_page_link);
                skipped += 1
                continue

            try:
                # <p class="ads__item__breadcrumbs">سيارات » هيونداي</p>
                # https: // olx.sa.com / ad / honda - civic - 2004 - ID6NhJW.html
                brand = util.find_brand(item.find_all('p', class_="ads__item__breadcrumbs")[0].text.strip().split(' ')[2], brands)
                # brand = util.find_brand(ad_page_link.strip().split('/')[4].split('-')[0], brands)
            except:
                brand = ""

            if brand== None:brand = ""

            # TODO create a lookup for this
            try:
                model, found = util.find_model(ad_key_details.find_all('td', class_="value")[0].text.strip(), models);
            except:
                model = ""

            if found == False: model = ""

            try:
                year = int(util.toArabicNumerals(ad_key_details.find_all('td', class_="value")[2].text.strip()));
            except:
                year = 0

            try:
                body_type = ""
            except:
                body_type = ""

            try:
                mileage = ad_key_details.find_all('td', class_="value")[3].text.strip();
            except:
                mileage = 0

            # TODO some features are not offered by hatla2ee, therefore we need to ml
            # TODO suggested algo: find similar brand, model, year instances with power values exist and then take mode
            # TODO I am returning zero for now, if we are showing this value on the website then we need to indicate that it is
            # TODO prdited value and does not exisit in the original ad

            try:
                engine = 0;
            except:
                engine = 0

            # TODO find similar instances, if three instances found then fetch power for this car otherwise return zero
            try:
                power = 0
            except:
                power = 0

            try:
                specs = ""
            except:
                specs = ""

            try:
                transmission = (ad_key_details.find_all('td', class_="value")[1].text).strip();
            except:
                transmission = ""

            try:
                fuel = "";
            except:
                fuel = ""

            try:
                condition = ""
            except:
                condition = ""

            try:
                color = "";
            except:
                color = ""

            try:
                price = item.find('p', class_="ads__item__price price ").text.strip()
                price_numeric_value = int((filter(lambda x: x in set(string.printable), price)).strip('.. ').replace(',', ''))
            except:
                price = 0
                price_numeric_value = 0

            try:
                image_link = item.find_all('img', class_="ads__item__photos")[0].attrs['src'].strip()
            except:
                util.loginfo("Skipping one item, error parsing image_link, ad_page_link"+ ad_page_link);
                skipped += 1
                continue

            try:
                location = item.find('p', class_='ads__item__location').text.strip()
            except:
                location = ""

            try:
                if detect(description) == 'ar': language_override = 'arabic' # langdetect returns ISO 639-1 codes,
                else: language_override = 'english' # where mongo expects ISO 639-3 codes for Arabic

            except:
                util.loginfo("Coudn't detect language falling back to English, ad_page_link"+ ad_page_link);
                language_override = 'english'

            brand_name = ""

            # TODO add tags field to the ads, this tags will take priority in search and will contian
            # TODO brand, model, color, engine ...etc all the features that I would to search with and I
            # TODO will need to categorize with as well, possibly I will make them lookups.


            ad_to_save_or_update =  {
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
                                    'keyFeatures': [], #TODO remove this, not used
                                    'features': [], #TODO remove this, not used
                                    'tags': brand_name,
                                    'variants': [{'image': image_link,
                                                  'price': price_numeric_value}]
                                    }

            #is_raw_ad = True indicates that ad need to be processed to extract features
            #ready ad for classification should be in the formate of: ([fet1,fet2....],cat)

            vote, confidence = classifier.classify(ad_to_save_or_update, True)
            # sleep(10)
            if vote != 'INV':
                if confidence >= 0.3:
                    if vote == 'SAL':
                        # must have brand
                        if ad_to_save_or_update['brand'] == "":
                            util.loginfo("Skipping one item, SAL and brand is not found, ad_page_link" + ad_page_link);
                            skipped += 1
                            continue
                        # must have model
                        if ad_to_save_or_update['model'] == "":
                            util.loginfo("Skipping one item, SAL and model is not found, ad_page_link" + ad_page_link);
                            skipped += 1
                            continue
                        # must have year
                        # if ad_to_save_or_update['year'] == 0:
                        #     util.loginfo("Skipping one item, SAL and year is not found, ad_page_link" + ad_page_link);
                        #     skipped += 1
                        #     continue
                    else:
                        if brand=="": del ad_to_save_or_update['brand']
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
                    util.loginfo("updating " + SOURCE + ad_page_link);
                    dao.update([ad_to_save_or_update]);
                    count_of_ads_updated +=1

            else:
                util.loginfo("adding " + SOURCE + ad_page_link);
                dao.add_list_to_db([ad_to_save_or_update])
                count_of_ads_added +=1

            if (settings['ENVIRONMENT'] == "Production"):
                wait = randint(5,20)
                util.loginfo("waiting for " +  str(wait) + " before reading next item");
                sleep(wait)

    return count_of_ads_added, count_of_ads_updated, skipped, counter_of_ads

