import os
import requests
import string


from bs4 import BeautifulSoup


class WebScraper:
    """
    A web scraper that retrieves articles from the Nature website.

    Attributes:
        _pages (int): The number of pages of articles to scrape.
        _folder_name_tmpl (str): The template for folder names to store articles in.
        _article_type (str): The type of articles to retrieve.
        _url (str): The URL to scrape articles from.

    Methods:
        start(): Starts the web scraper.
    """

    def __init__(self):
        self._pages = None
        self._folder_name_tmpl = "Page_"
        self._article_type = None
        self._url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"

    def start(self):
        self._pages, self._article_type = self._init_scraper()
        print(f"page: {self._pages}, type: {self._article_type}")

        for n in range(1, self._pages + 1):
            folder_name = f"{self._folder_name_tmpl}{n}"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            url = f"{self._url}&page={n}"

            res = self._recieve_response(url)
            if not res:
                print(f"The URL {url} returned {res.status_code}")

            article_ref_list = self._get_news_list(res, self._article_type)

            for link in article_ref_list:
                article = self._get_article(link)
                save_path = f"{folder_name}/{article['title']}.txt"
                self._save_to_file(save_path, article["body"].encode())

        print("Saved all articles.")

    def _init_scraper(self):
        while True:
            try:
                pages = int(input())
                if pages < 1:
                    continue
                article_type = input()
                return pages, article_type
            except ValueError:
                continue

    def _create_title(self, text):
        title = []
        for i in text:
            if i in string.punctuation:
                continue
            elif i.isspace():
                title.append("_")
            else:
                title.append(i)
        return "".join(title)

    def _get_article(self, link):
        r = self._recieve_response(link)
        s = BeautifulSoup(r.content, 'html.parser')
        title = self._create_title(s.find("title").text)
        body = s.find("div", {"class": "c-article-teaser-text"}).text.strip()
        return {"title": title,
                "body": body}

    def _save_to_file(self, name, content):
        with open(name, "wb") as f:
            f.write(content)

    def _get_news_list(self, r, article_type):
        soup = BeautifulSoup(r.content, 'html.parser')
        article_list = soup.find_all("article", {'class': 'c-card'})
        news_links = []
        for art in article_list:
            text = art.find("span", {"data-test": "article.type"}).text.strip()
            if text == article_type:
                path = art.find("a", {"class": "c-card__link"}).get("href")
                news_links.append("https://www.nature.com" + path)
        return news_links

    def _recieve_response(self, url):
        try:
            res = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.5'})
            return res
        except requests.exceptions.RequestException:
            print(f"ERROR: Bad url: {url}")
            return None


def main():
    web_scraper = WebScraper()
    web_scraper.start()


if __name__ == "__main__":
    main()
