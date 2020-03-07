from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def get_url(url):
    source = requests.get(url)
    return source


"""
Product ID = data-id
Seller ID = data-seller-product-id
Product title : data-title
Price = data-price
URL of the product image
"""


def get_next_page_url(soup, url):
    if soup == None:
        return None
    if url == None:
        return None
    page_links = soup.find(
        'div', class_='list-pager').ul.find('a', class_="next")
    if page_links != None:
        return url + page_links['href']
    else:
        return None


def get_prev_page_url(soup, url):
    if soup == None:
        return None
    if url == None:
        return None
    page_links = soup.find(
        'div', class_='list-pager').ul.find('a', class_="prev")
    if page_links != None:
        return url + page_links['href']
    else:
        return None


def get_product_from_soup(soup):
    products = soup.find_all('div', class_='product-item')
    product_ids = []
    seller_ids = []
    product_titles = []
    prices = []
    product_imgs = []

    for product in products:
        try:
            product_ids.append(product['data-id'])
            seller_ids.append(product['data-seller-product-id'])
            product_titles.append(product['data-title'])
            prices.append(product['data-price'])
            product_imgs.append(product.img['src'])

        except:
            pass

    product_df = pd.DataFrame({'product_id': product_ids,
                               'seller_id': seller_ids, 'title': product_titles,
                               'price': prices, 'image_url': product_imgs})
    return product_df


def scrape_from_url(url):
    response = get_url(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        link = re.search(
            r"(http|ftp|https)://([\w+?\.\w+])+([a-zA-Z0-9]*)?", url).group()
        df = get_product_from_soup(soup)
        list_page_df = [df]

        prev_page = get_prev_page_url(soup, url)
        next_page = get_next_page_url(soup, url)

        while (prev_page != None):
            print(f"prev page: {prev_page}")
            response = get_url(prev_page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                list_page_df.append(get_product_from_soup(soup))
                prev_page = get_prev_page_url(soup, link)
            else:
                prev_page = None

        while (next_page != None):
            print(f"next page: {next_page}")
            response = get_url(next_page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                list_page_df.append(get_product_from_soup(soup))
                next_page = get_next_page_url(soup, link)
            else:
                next_page = None

        products_df = pd.concat(list_page_df, ignore_index=True)
        return products_df
    else:
        return None

