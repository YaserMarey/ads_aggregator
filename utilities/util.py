# coding=utf-8
import json
import os as os
import time
from random import randint
from time import sleep

import requests

from settings import settings


def download_file(url, data_folder_path):
    result = None
    if (settings['ENVIRONMENT'] == "Production"):
        read_from_cache = False
    else:
        read_from_cache = True

    local_filename = url.split('/')[-1]
    if len(local_filename) == 0: local_filename = url.split('/')[-2]

    if (read_from_cache):
        if not os.path.isfile(data_folder_path + local_filename):
            result = dowload(url, data_folder_path, local_filename)
        else:
            f = open(data_folder_path + local_filename, "r")
            result = f.read()
            f.close()
            loginfo("Page is read from cache");
    else:
        result = dowload(url, data_folder_path, local_filename)
    return result


def dowload(url, data_folder_path, local_filename):
    result = None
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        loginfo("Connection refused, sleeping for a while");
        # TODO make sleep time in case of conneciton refused part of the settings
        sleep(randint(5, 20))
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            loginfo("Connection refused again, returning an empty result");
            return result

    if response.status_code == 200:
        if pageIsDownloadedButNoData(response, url):
            loginfo("probably reaching end of pages, trying next page!");
            return result
        else:
            loginfo("Page is downloaded");
            if (settings['ENVIRONMENT'] == "Development"):
                f = open(data_folder_path + local_filename, 'w')
                f.write(response.content)
                f.close()
            result = response.content
            return result
    else:
        loginfo("Error, code : " + str(response.status_code) + " downaloading : " + url);

    return result


def pageIsDownloadedButNoData(response, url):
    # TODO hardcoding need to remove it
    if 'carmudi' in url:
        if (len(json.loads(response.content)['products']) == 0):
            return True
    return False


def save_list_as_csv(data, file_name, data_folder_path):
    import pandas as pd
    pd.DataFrame(data).to_csv(path_or_buf=data_folder_path + file_name, encoding='utf8')


def read_csv_as_list(file_name, data_folder_path):
    import pandas as pd
    return pd.read_csv(path_or_buf=data_folder_path + file_name, encoding='utf8')


def read_csv_as_list_(file_name, data_folder_path):
    import csv
    output = []
    with open(data_folder_path + file_name, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        output = [item for item in reader]
    return output


def save_list_as_excel(data, file_name, data_folder_path):
    import pandas as pd
    pd.DataFrame(data).to_excel(path_or_buf=data_folder_path + file_name, encoding='utf8')

    # keys = data[0].keys()
    # with open(file_name, 'wb') as output_file:
    #     dict_writer = csv.DictWriter(output_file, keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(data)


def logerr(msg):
    if settings['LOG_ERR'] == True:
        print
        time.strftime("%x") + " " + time.strftime("%X") + " :: " + u''.join(msg).encode('utf-8')


def loginfo(msg):
    if settings['LOG_INFO'] == True:
        print
        time.strftime("%x") + " " + time.strftime("%X") + " :: " + u''.join(msg).encode('utf-8')


def logdebug(msg):
    if settings['LOG_DEBUG'] == True:
        print
        time.strftime("%x") + " " + time.strftime("%X") + " :: " + u''.join(msg).encode('utf-8')


def logtofile(filename, msg):
    file = open(filename, "a+")
    file.write(time.strftime("%x") + " " + time.strftime("%X") + " :: " + msg + "\n")
    file.close()


def find_brand(brand_name, brands):
    for brand in brands:
        if brand_name.lower() in [n.lower() for n in brand.get('name_en')] \
                or brand_name in [n for n in brand.get('name_ar')]:
            logdebug("brand name is " + u''.join(brand_name) + " and it is found" + ", ref brand is " + str(brand))
            return brand
    return None


# TODO, return model instead of model name, ad should reference model by id not by name, concequently ads
# with unknown models won't be added
def find_model(model_name, models):
    for model in models:
        if model_name.lower() in [n.lower() for n in model.get('name_en')] \
                or model_name in [n for n in model.get('name_ar')]:
            logdebug(
                "model name is " + u''.join(model_name) + " and it is found" + ", ref model name is " + model['name'])
            return model['name'], True
    # TODO, we need to look into this furhter, ideally all brands should be coded
    # TODO, but for now if couldn't map the name to one of the coded names, return whatever is coming in the ad
    return model_name, False


# This method return model object to be used in case we need to access the attached names list
def find_model_(model_name, models):
    for model in models:
        if model_name.lower() in [n.lower() for n in model.get('name_en')] \
                or model_name in [n for n in model.get('name_ar')]:
            logdebug(
                "model name is " + u''.join(model_name) + " and it is found" + ", ref model name is " + model['name'])
            return model
    return None


def strip_nokat(str):
    return str.replace("أ", "ا").replace("ي", "ى").replace("ة", "ه").replace(" ", "").strip();


# TODO I should be able to pass key that is in unicode
def find_month(month_name):
    months = {u'يناير': '1', u'فبراير': '2', u'إبريل': '4', u'أبريل': '4', u'ابريل': '4', u'مارس': '3', u'مايو': '5',
              u'يونيو': '6', u'يوليو': '7',
              u'اغسطس': '8', u'أغسطس': '8', u'سبتمبر': '9', u'أكتوبر': '10', u'اكتوبر': '10', u'نوفمبر': '11',
              u'ديسمبر': '12'}

    try:
        return months[month_name]
    except:
        return None


def toArabicNumerals(str):
    s = []
    for c in str:
        if ord(c) >= 1632 and ord(c) <= 1741:
            s.append(chr(ord(c) - 1584))
        else:
            s.append(c)
    return ''.join(s)


def find_location(location):
    for location_list in settings['locations']:
        if location.lower() in [l.lower() for l in location_list]:
            return u' '.join(location_list)
    return location


def find_color(color):
    for color_list in settings['colors']:
        if color.lower() in [c.lower() for c in color_list]:
            return u' '.join(color_list)
    return color
