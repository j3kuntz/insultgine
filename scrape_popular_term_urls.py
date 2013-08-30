from lxml import html,etree
import itertools
import requests
import argparse

def url2html(url):
    request = requests.get(url)
    return html.fromstring(request.content)

def main():
    letters  = "abcdefghijklmnopqrstuvwxyz"
    BASE_URL = "http://www.urbandictionary.com/popular.php?character=%s"

    with open("popular_definition_urls.txt", "w") as out:
        for letter in letters:
            letter       = letter.upper()
            html         = url2html(BASE_URL % letter)
            terms_li_els = html.xpath(
                '//div[@id="columnist"]//li//a')
            for term_li_el in terms_li_els:
                url = term_li_el.get("href")
                if not url:
                    continue
                out.write(
                    "http://www.urbandictionary.com%s\n" % url)

if __name__ == "__main__":
    main()
