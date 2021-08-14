from collections import namedtuple


UrlData = namedtuple('UrlData',
                     ['title', 'url', 'domen', 'is_ads', 'tag'])

TacticModule = namedtuple('TacticModule',
                          ['title', 'desc', 'obj'])
