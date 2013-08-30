from lxml import html,etree
import itertools
import requests
import argparse

def url2html(url):
    request = requests.get(url)
    return html.fromstring(request.content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str)
    args = parser.parse_args()

    urls = []
    with open(args.file, "r") as in_f:
        for line in in_f:
            url = line.replace("\n", "").strip()
            urls.append(url)

    with open("all_definition_urls.txt", "w") as out:
        for i, url in enumerate(urls):
            html         = url2html(url)
            terms_li_els = html.xpath(
                '//div[@id="columnist"]//li//a')
            print "%s = > %s" % (url, len(terms_li_els))
            for term_li_el in terms_li_els:
                url = term_li_el.get("href")
                if not url:
                    continue
                out.write(
                    "http://www.urbandictionary.com%s\n" % url)


if __name__ == "__main__":
    main()
