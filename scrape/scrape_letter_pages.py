from lxml import html,etree
import itertools
import requests
import argparse

def get_max_pages(parsed_html):
    li_els = parsed_html.xpath(
        '//div[@class="pagination"]//li')
    return int(li_els[-2].text_content().strip())

def url2html(url):
    request = requests.get(url)
    return html.fromstring(request.content)

def main():
    letters  = "abcdefghijklmnopqrstuvwxyz"
    BASE_URL = "http://www.urbandictionary.com/browse.php?character=%s"

    with open("letter_urls.txt", "w") as out:
        for letter in letters:
            letter    = letter.upper()
            html      = url2html(BASE_URL % letter)
            max_pages = get_max_pages(html)
            for i in xrange(1, max_pages+1):
                out.write(
                    BASE_URL % letter + "&page=%s" % i + "\n")

if __name__ == "__main__":
    main()
