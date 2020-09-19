import sys
from datetime import date

from dataaccess import dao
from ml.classifier.ad_classifier import VoteClassifier
from readers import reader_carmudi
from readers import reader_haraj
from readers import reader_hatla2ee
from readers import reader_olx
from settings import settings
from utilities import util

SOURCE_CARMUDI = "carmudi.com.sa"
SOURCE_HATLA2EE = "ksa.hatla2ee.com"
SOURCE_OLX = "olx.sa.com"
SOURCE_HARAJ = "haraj.com.sa"

def main(number_of_pages, debug, source, brands, models, classifier):
    log_file_name = settings[settings['ENVIRONMENT']]['LOG_FOLDER_PATH']+str(date.today())
    util.loginfo("==============================================================")
    util.loginfo(" Reading from " + source + " .... # pages: " + str(number_of_pages) + " debug: " + str(debug))
    util.logtofile(log_file_name, "Reading from " + source + " .... # pages: " + str(number_of_pages) + " debug: " + str(debug))
    util.loginfo("==============================================================")
    # TODO we need to check if reading basic data without description is enough to spee up update

    if source==SOURCE_CARMUDI:
        reader = reader_carmudi
    elif source == SOURCE_HATLA2EE:
        reader = reader_hatla2ee
    elif source == SOURCE_OLX:
        reader = reader_olx
    elif source == SOURCE_HARAJ:
        reader = reader_haraj

    count_of_ads_added, count_of_ads_updated, skipped, counter_of_ads = reader.read(number_of_pages, debug, brands, models, classifier)

    util.loginfo( "For " + source + " number of ads to add: " + str(count_of_ads_added));
    util.logtofile(log_file_name, "For " + source + " number of ads to add: " + str(count_of_ads_added))
    util.loginfo( "For " + source + " number of ads to update: " + str (count_of_ads_updated));
    util.logtofile(log_file_name, "For " + source + " number of ads to update: " + str (count_of_ads_updated))
    util.logtofile(log_file_name, "For " + source + " number of ads to skipped: " + str(skipped))
    util.logtofile(log_file_name, "For " + source + " total number of ads : " + str(counter_of_ads))

    util.loginfo("======================== Done ===============================")

def save_as_csv(scrapped_data_to_add, scrapped_data_to_update, data_folder_path):
    util.save_list_as_csv(scrapped_data_to_add, 'data_add_' + str(date.today()) + '.csv', data_folder_path);
    util.save_list_as_csv(scrapped_data_to_update, 'data_update_' + str(date.today()) + '.csv', data_folder_path);

if __name__ == '__main__':
    if (len(sys.argv) > 2):
        number_of_pages = int(sys.argv[1])
        if (sys.argv[2] == "no_debug"):
            debug = False
        else:
            debug = True
        source = sys.argv[3]
    #TODO we need to fix numbers of pages so that it scans all pages once every two days
    #TODO and scan only most recent 10%-20% of the pages daily
    # main(number_of_pages=12, debug=False, source=SOURCE_CARMUDI)
    # main(number_of_pages=24, debug=False, source=SOURCE_HATLA2EE)
    # main(number_of_pages=95, debug=False, source=SOURCE_OLX)
    # main(number_of_pages=459, debug=False, source=SOURCE_HARAJ)

    # main(number_of_pages=2, debug=False, source=SOURCE_CARMUDI)
    # main(number_of_pages=4, debug=False, source=SOURCE_HATLA2EE)
    # main(number_of_pages=20, debug=False, source=SOURCE_OLX)
    # main(number_of_pages=5, debug=False, source=SOURCE_HARAJ)

    brands = dao.get_brands()
    models = dao.get_models()

    vote_classifier = VoteClassifier()

    main(number_of_pages=12, debug=False, source=SOURCE_CARMUDI,
         brands=brands, models=models, classifier=vote_classifier)

    main(number_of_pages=24, debug=False, source=SOURCE_HATLA2EE,
         brands=brands, models=models, classifier=vote_classifier)

    main(number_of_pages=95, debug=False, source=SOURCE_OLX,
         brands=brands, models=models, classifier=vote_classifier)

    main(number_of_pages=459, debug=False, source=SOURCE_HARAJ,
         brands=brands, models=models, classifier=vote_classifier)
