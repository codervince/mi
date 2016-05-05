from html.parser import HTMLParser

class MyHTMLLinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'href' in attrs:
            print("Link:", attrs['href'])
            return attrs['href']