from lxml import html,etree
import itertools
import requests
import argparse

def clean(txt):
    return txt.strip().replace("\n", "")

class UrbanDictionaryDefinitionStrategy(object):
    def __init__(self, tr_1, tr_2):
        self.tr_1 = tr_1
        self.tr_2 = tr_2

   
    def extract(self):
        return {
            'id'            : self.get_id(),
            'phrase'        : self.get_phrase(),
            'definition'    : self.get_definition(),
            'example'       : self.get_example(),
            'tags'          : self.get_tags(),
        }

    def get_id(self):
        td_els = self.tr_1.xpath('./td[@class="word"]')
        if not td_els:
            return None  
        return clean(td_els[0].get('data-defid'))
    
    def get_phrase(self):
        span_els = self.tr_1.xpath('./td[@class="word"]/span')
        if not span_els:
            return None
        return clean(span_els[0].text)

    def get_definition(self):
        div_els = self.tr_2.xpath('./td[@class="text"]/div[@class="definition"]')
        if not div_els:
            return None
        return clean(div_els[0].text)

    def get_example(self):
        div_els = self.tr_2.xpath('./td[@class="text"]/div[@class="example"]')
        if not div_els:
            return None
        return clean(div_els[0].text)

    def get_tags(self):
        a_els = self.tr_2.xpath('./td[@class="text"]/div[@class="greenery"]/span[@class="tags"]/a')
        if not a_els:
            return []
        return [clean(a.text) for a in a_els]

class UrbanDictionaryPhraseStrategy(object):
    def __init__(self, html_text):
        self.html_text = html_text
        self.parsed    = html.fromstring(html_text)
        html.etree.strip_elements(self.parsed, 'noscript')

    def extract(self):
        return {
            'definitions'       : self.get_definitions(),
            'see_also_links'    : self.get_see_also_links(),
        }

    def get_definitions(self):
        td_els         = self.parsed.xpath('//td[@class="word"]')
        definition_ids = [t.get('data-defid') for t in td_els]
        definitions    = []
        for def_id in definition_ids:
            td_1 = self.parsed.xpath('//td[@data-defid="%s"]' % def_id)
            td_2 = self.parsed.xpath('//td[@id="entry_%s"]' % def_id)
            if not td_1 or not td_2:
                continue
            tr_1 = td_1[0].xpath('..')[0]
            tr_2 = td_2[0].xpath('..')[0]
            strategy = UrbanDictionaryDefinitionStrategy(tr_1, tr_2)
            definitions.append(strategy.extract())
        return definitions

    def get_see_also_links(self):
        a_els = self.parsed.xpath('//div[@id="nearby_titles"]/ul[@class="tags"]/li/a')
        return [clean(a.text) for a in a_els]

    def get_next_page_link(self):
        next_els = self.parsed.xpath('//div[@class="pagination"]/li[@class="next"/a')
        if not next_els:
            return None
        return next_els[0].get('href')

class Crawler(object):
    @classmethod
    def scrape_page(cls, page_url):
        request         = requests.get(page_url)
        strategy        = UrbanDictionaryPhraseStrategy(request.content)
        extracted_data  = strategy.extract()
        return extracted_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    args = parser.parse_args()
    from pprint import pprint
    pprint(Crawler.scrape_page(args.url))

if __name__== "__main__":
    main()
