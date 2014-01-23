from lxml import html,etree
import itertools
import requests
import argparse
import contextlib
import ujson

def clean(txt):
    if txt is None:
        return ""
    return txt.strip().replace("\n", "")

class UrbanDictionaryDefinitionStrategy(object):
    def __init__(self, word_el):
        self.word_el = word_el
   
    def extract(self):
        return {
            'id'            : self.get_id(),
            'phrase'        : self.get_phrase(),
            'definition'    : self.get_definition(),
            'example'       : self.get_example(),
            'likes'         : self.get_up_count(),
            'dislikes'      : self.get_down_count(),
            'author'        : self.get_author_name(),
            'author_link'   : self.get_author_link(),
        }

    def get_id(self):
        return clean(self.word_el.get('data-defid'))
    
    def get_phrase(self):
        span_els = self.word_el.xpath('.//div[@class="word"]/a')
        return clean(span_els[0].text_content())

    def get_definition(self):
        div_els = self.word_el.xpath('.//div[@class="definition"]')
        if not div_els:
            return None
        return clean(div_els[0].text_content())

    def get_example(self):
        div_els = self.word_el.xpath('.//div[@class="example"]')
        if not div_els:
            return None
        return clean(div_els[0].text_content())

    def get_up_count(self):
        count_els = self.word_el.xpath('.//span[@class="up"]/span[@class="count"]')
        if not count_els:
            return None
        return clean(count_els[0].text_content())

    def get_down_count(self):
        count_els = self.word_el.xpath('.//span[@class="down"]/span[@class="count"]')
        if not count_els:
            return None
        return clean(count_els[0].text_content())

    def get_author_name(self):
        author_els = self.word_el.xpath('.//a[@class="author"]')
        if not author_els:
            return None
        return clean(author_els[0].text_content())

    def get_author_link(self):
        author_els = self.word_el.xpath('.//a[@class="author"]')
        if not author_els:
            return None
        return clean(author_els[0].get('href'))

class UrbanDictionaryPhraseStrategy(object):
    def __init__(self, html_text):
        self.html_text = html_text
        self.parsed    = html.fromstring(html_text)
        html.etree.strip_elements(self.parsed, 'noscript')

    def extract(self):
        return {
            'definitions'       : self.get_definitions(),
            'next_page_link'    : self.get_next_page_link(),
        }

    def get_definitions(self):
        box_els         = self.parsed.xpath('//div[@class="box"]')
        definition_ids = [b.get('data-defid') for b in box_els]
        definitions    = []
        for def_id in definition_ids:
            word = self.parsed.xpath('//div[@data-defid="%s"]' % def_id)
            if not word:
                continue
            word = word[0]
            strategy = UrbanDictionaryDefinitionStrategy(word)
            definitions.append(strategy.extract())
        return definitions

    def get_next_page_link(self):
        next_els = self.parsed.xpath('//div[@class="pagination"]//li[@class="next"]/a')
        if not next_els:
            return None
        rel_link = next_els[0].get('href').strip()
        return "http://www.urbandictionary.com%s" % rel_link

class Crawler(object):
    @classmethod
    def scrape_page(cls, page_url):
        print page_url
        request         = requests.get(page_url)
        strategy        = UrbanDictionaryPhraseStrategy(request.content)
        extracted_data  = strategy.extract()
        return extracted_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url_file', type=str)
    parser.add_argument('--out_file', type=str)
    args= parser.parse_args()
    url_file_handle = args.url_file

    seed_def_urls = []
    with open(args.url_file, "r") as in_file:
        for line in in_file:
            url = line.strip().replace("\n","")
            seed_def_urls.append(url)
    
    with open(args.out_file, "w") as outf_handle:
        for def_url in seed_def_urls:
            urls = [def_url]
            definitions = []
            while urls:
                cur_url = urls[0]
                extracted_data = Crawler.scrape_page(cur_url)
                _defs = extracted_data['definitions']
                next_link = extracted_data['next_page_link']
                del urls[0]
                if next_link:
                    urls.append(next_link)
                definitions.extend(_defs)

                for definition in definitions:
                    outf_handle.write(ujson.dumps(definition))
                    outf_handle.write("\n")

if __name__== "__main__":
    main()
