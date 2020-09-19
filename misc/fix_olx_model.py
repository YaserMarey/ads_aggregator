from utilities import util
from dataaccess import dao
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import settings
def dump_models():
    db = dao.get_db()
    models = db.models.find({})
    models_list = []
    for product in models:
        models_list.append(product)
    util.save_list_as_csv(models_list, 'models.csv', '/home/bebe/0yasser/shofle/source/shofle_reader/log/')
    print ("Done")

def update_models():
    db = dao.get_db()
    models = util.read_csv_as_list_('models.csv', '/home/bebe/0yasser/shofle/source/shofle_reader/log/')
    for model in models:
        model['active'] = bool('true')
        model['name'] = model['name'].strip()
        model['name_ar'] = model['name_ar'].strip()
        db.models.insert(model)
    print ("Done")


def fix_olx_model():
    db = dao.get_db()
    products = db.products.find({'source': 'olx.sa.com'})
    # npproducts =  np.array([product for product in products]) #np.array(products)
    # npproducts = []
    models = []
    nonrecognized = []
    NoneCounter = 0
    for product in products:
         # if len(product['model']['name']) >0 and models.find(product['model']['name']) == 0:
         # db.models.insert({'name':'', 'name_ar':product['model'], 'active':bool('true')})
         #  npproducts.append(product)
         if product['model'] == None:
             NoneCounter +=1


    #
    # unique, counts = np.unique(models, return_counts=True)
    # hist = np.array((unique, counts)).T
    # print hist
    # print nonrecognized
    # print str(NoneCounter)
    # util.save_list_as_csv(hist,'coutns', '/home/bebe/0yasser/shofle/source/shofle_reader/log/' )
    # plt.plot(unique, counts)
    # plt.xticks(unique, counts)
    # plt.show()
    print (str(NoneCounter))
    print ("Done")

    #     try:
    #         if detect(product['description']) == 'ar':
    #             language_override = 'arabic'  # langdetect returns ISO 639-1 codes,
    #         else:
    #             language_override = 'english'
    #         # where mongo expects ISO 639-3 codes for Arabic
    #     except:
    #         util.loginfo("Coudn't detect language falling back to English, ad_page_link" + product['ad_id']);
    #         language_override = 'english'
    #
    #     brands = dao.get_brands()
    #
    #     try:
    #         for brand in brands:
    #             if brand['_id'] == product['brand']:
    #                 if language_override == "arabic":
    #                     brand_name = brand.get("name_ar")
    #                     break;
    #                 else:
    #                     brand_name = brand.get("name")
    #     except:
    #         util.loginfo("Skipping one item, error parsing brand, ad_data_link" + product['ad_id']);
    #         continue
    #     if brand == None:
    #         util.loginfo("Skipping one item, brand is not found, ad_data_link" + product['ad_id']);
    #         continue
    #
    #     product['language_override'] = language_override
    #     product['tags'] = brand_name
    #
    #     db.get_collection('products').save(product)

if __name__ == '__main__':
    fix_olx_model()
    # dump_models()
    # update_models()
