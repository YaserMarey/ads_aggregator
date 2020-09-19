from collections import defaultdict

from nltk import ne_chunk
from polyglot.text import Text
from nltk.tag import StanfordNERTagger


def polyglot_entities(fileids=None, section = None, corpus=kddcorpus):
    """
    Extract entities from each file using polyglot
    """
    results = defaultdict(lambda: defaultdict(list))
    fileids = fileids or corpus.fileids()

    for fileid in fileids:
        if section is not None:
            text = Text((list(sectpull([fileid],section=section))[0][1]))
        else:
            text = Text(corpus.raw(fileid))



        for entity in text.entities:
            etext = " ".join(entity)

            if entity.tag == 'I-PER':
                key = 'persons'
            elif entity.tag == 'I-ORG':
                key = 'organizations'
            elif entity.tag == 'I-locations':
                key = 'locations'
            else:
                key = 'other'

            results[fileid][key].append(etext)

    return results

def stanford_entities(model, jar, fileids=None, corpus=kddcorpus, section = None):
    """
    Extract entities using the Stanford NER tagger.
    Must pass in the path to the tagging model and jar as downloaded from the
    Stanford Core NLP website.
    """
    results = defaultdict(lambda: defaultdict(list))
    fileids = fileids or corpus.fileids()
    tagger  = StanfordNERTagger(model, jar)
    section = section

    for fileid in fileids:
        if section is not None:
            text = nltk.word_tokenize(list(sectpull([fileid],section=section))[0][1])
        else:
            text  = corpus.words(fileid)

        chunk = []

        for token, tag in tagger.tag(text):
            if tag == 'O':
                if chunk:
                    # Flush the current chunk
                    etext =  " ".join([c[0] for c in chunk])
                    etag  = chunk[0][1]
                    chunk = []

                    if etag == 'PERSON':
                        key = 'persons'
                    elif etag == 'ORGANIZATION':
                        key = 'organizations'
                    elif etag == 'LOCATION':
                        key = 'locations'
                    else:
                        key = 'other'

                    results[fileid][key].append(etext)

            else:
                # Build chunk from tags
                chunk.append((token, tag))

    return results


def nltk_entities(fileids=None, section = None,corpus=kddcorpus):
    """
    Extract entities using the NLTK named entity chunker.
    """
    results = defaultdict(lambda: defaultdict(list))
    fileids = fileids or corpus.fileids()

    for fileid in fileids:
        if section is not None:
            text = nltk.pos_tag(nltk.word_tokenize(list(sectpull([fileid],section=section))[0][1]))
        else:
            text = nltk.pos_tag(corpus.words(fileid))



        for entity in nltk.ne_chunk(text):
            if isinstance(entity, nltk.tree.Tree):
                etext = " ".join([word for word, tag in entity.leaves()])
                label = entity.label()
            else:
                continue

            if label == 'PERSON':
                key = 'persons'
            elif label == 'ORGANIZATION':
                key = 'organizations'
            elif label == 'LOCATION':
                key = 'locations'
            elif label == 'GPE':
                key = 'other'
            else:
                key = None

            if key:
                results[fileid][key].append(etext)

    return results