# coding=utf-8
settings={
    #Development
    'Development':{
        'Mongo':{
            'DbClient':'localhost:27017',
            'DbName':'materialshop-dev'
        },
        'carmudi.com.sa': {
                'DATA_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/data/carmudi/',
        },
        'ksa.hatla2ee.com': {
                'DATA_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/data/hatla2ee/',
        },
        'olx.sa.com': {
                'DATA_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/data/olx/',
        },
        'haraj.com.sa': {
                'DATA_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/data/haraj/',
        },
        'LOG_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/log/',
        'ML_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/ml/'
    },
    #Production
    'Production':{
        'Mongo': {
            # 'DbClient': 'mongodb://shofle_usr:password@35.176.3.59:27017/shofle_db',
            'DbClient': 'mongodb://shofle_usr:password@localhost/shofle_db',
            'DbName': 'shofle_db'
        },

        'carmudi.com.sa': {
                'DATA_FOLDER_PATH': '/home/ubuntu/source/shofle_reader/data/carmudi/',
        },
        'ksa.hatla2ee.com': {
                'DATA_FOLDER_PATH': '/home/ubuntu/source/shofle_reader/data/hatla2ee/',
        },
        'olx.sa.com': {
                'DATA_FOLDER_PATH': '/home/ubuntu/source/shofle_reader/data/olx/',
        },
        'haraj.com.sa': {
            'DATA_FOLDER_PATH': '/home/bebe/0yasser/shofle/source/shofle_reader/data/haraj/',
        },
        'LOG_FOLDER_PATH': '/home/ubuntu/source/shofle_reader/log/',
        'ML_FOLDER_PATH': '/home/ubuntu/source/shofle_reader/ml/'
    },
    #Carmudi
    'carmudi.com.sa':{
            'base_url': "https://carmudi.com.sa"
    },
    #Hatla2ee
    'ksa.hatla2ee.com': {
            'base_url': "https://ksa.hatla2ee.com"
    },
    #Olx
    'olx.sa.com': {
            'base_url': "https://olx.sa.com"
    },
    #Haraj
    'haraj.com.sa':{
            'base_url': "https://haraj.com.sa"
    },

    'modes':{
        'power': '210'

    },

    "ad_cats" : {'SAL':['Sale','للبيع'],'PRT':['Parts','قطع غيار','تشليح'], 'TRN':['Transfer','للتنازل','تنازل'],
                 'SVC':['Services','خدمات'],'EXP':['Exhiption','معارض'], 'REQ':['Requests','مطلوب'],
                 'ACC':['Accorices','كماليات'],'EXC':['Exchange','للبدل'],'OTH':['Other','أخرى','لوحة','شيول','دباب']},

    "colors": [['White', 'ابيض','أبيض'], ['Red', 'احمر', 'أحمر'],['Blue', 'ازرق', 'أزرق'],
               ['Silver / Grey','Silver','فضي','فضى'], ['Grey','Gray','رمادي','رمادى'],['Gold','ذهبي','ذهبى'],
               ['Beige','بيج'],['Black','اسود','أسود'],['Dark Red','أحمر داكن','احمر داكن'],['Brown','بنى','بني']],

    "locations": [['Riyadh', 'الرياض'], ['Jeddah', 'جده', 'جدة'],['Dammam', 'الدمام'], ['Najran', 'نجران'],
                  ['Yanbu','ينبع'], ['Abha','ابها','أبها'],
                  ['Medina','Madina','Al Madinah','Al Madina','Al-Madina','Al-Madinah','AlMadina','AlMadinah','المدينه'
                      ,'المدينه المنوره','المدينة','المدينة المنورة','المدينه المنورة','المدينة المنوره'],
                  ['AlKhobar','Al-Khobar','Al Khobar','الخبر'],['Jizan','جيزان'],['Taif','الطائف','الطايف'],['Mecca','مكة','مكه']
                  ,['Eastern-Province', 'الشرقية','المنطقة الشرقية','الشرقيه','المنطقه الشرقيه']],

    #Change this to False in Produciton
    'LOG_INFO': True,
    #Keep this True in Production
    'LOG_ERR': True,
    # Change this to False in Produciton
    'LOG_DEBUG': True,
    #Environment Switch
    'ENVIRONMENT': 'Development'

}