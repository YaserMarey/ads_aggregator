# coding=utf-8
from pymongo import MongoClient
import random
db = MongoClient()['materialshop-dev']
list_of_products = list(db.products_training.find({'ad_cat':{'$exists':False}}))
# list_of_products =  list(db.products_training.find({'$and':[ { 'ad_cat': { '$exists': 'False' } }, { 'source':'olx.sa.com'} ]}))
# list_of_products = [w for w in list_of_products if w['descriptoin'].find(u'مطلوب') != -1]

# a = u'/.*مطلوب.*/'
# list_of_products =  db.products_training.find({"description": a})
# list_of_products = list(db.products_training.find({'source':'olx.sa.com'}))
# list_of_products = list(db.products_all.find({'ad_cat':{'$exists':True}}))
for i in range(0,350):
        index = random.randint(1,len(list_of_products))
        print ("ID: ",str(list_of_products[index]['_id']) + "\n", "Title: ",list_of_products[index]['title'] + "\n" + \
        "Description: ", u''.join(list_of_products[index]['description']) + "\n", "Model: ", list_of_products[index]['model'] +"\n" + \
        "Year: ", str(list_of_products[index]['year']) + "\n" + \
        "Link: ", list_of_products[index]['ad_page_link'] + "\n" + \
        "Source: ", list_of_products[index]['source'])

        ad_cat = ""
        # while ad_cat not in ['SAL','PRT', 'TRN', 'SVC', 'EXP', 'REQ', 'ACC','EXC','OTH', 'INV','X']:
        # while ad_cat not in ['PRT', 'NPRT','TRN', 'NTRN', 'SVC', 'NSVC', 'EXP', 'NEXP',
        #                      'REQ', 'NREQ', 'ACC', 'NACC','EXC','NEXC','OTH','NOTH', 'X']:
        while ad_cat not in ['SAL','PRT', 'TRN', 'SVC', 'EXP', 'REQ', 'ACC','EXC','OTH', 'INV','X']:
            ad_cat = raw_input()
        if ad_cat !='X':
                list_of_products[index]['ad_cat'] = ad_cat
                db.products_training.save(list_of_products[index])
        print("=============================================")
