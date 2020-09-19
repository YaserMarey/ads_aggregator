# Classifieds Aggregator for Ads in Arabic

Ethically scrap car ads published on four major websites in Egypt and KSA:

- [Carmudi](https://carmudi.com.sa)
- [Hatla2ee](https://ksa.hatla2ee.com)
- [Olx](https://olx.sa.com)
- [Haraj](https://haraj.com.sa)

### Disclaimer
None of these websites has published API, and scrapping is the only way to collect the data however if you are going to reuse this code, please respect ethical web scrapping guidelines similar to what is 
published [here](https://www.empiricaldata.org/dataladyblog/a-guide-to-ethical-web-scraping#:~:text=Practice%20Ethical%20Web%20Scraping,how%20to%20do%20it%20right)

### How does it work
The aggregator cleans and interpolate data and classify it into one of the ads categories:
| Code | Caegorgy |
| ------ | ------ |
|SAL | Sale|
|PRT | Parts|
|TRN | Transfer|
|SVC | Services|
|EXP | Exhiption|
|REQ | Request to buy|
|ACC | Accessories|
|EXC | Exchange|
|OTH | Other|
|INV | Invalid ad|

The ./ml/classifier/ad_classifier.py contains an ensemble of classifiers trained on a bag of words extracted from ads and then each classifier vote for the type of the ad.


### Todos
 - Clean the code
 - Enhance classification results
 - Less hurestices

### License
----

MIT

**Free Software, Yeah!**

