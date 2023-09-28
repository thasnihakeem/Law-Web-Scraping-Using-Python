import time
import warnings
import pandas as pd
from lxml import etree as etree
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings('ignore')
driver = webdriver.Chrome(ChromeDriverManager().install())

def extract_content(url):
    driver.get(url)
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    dom = etree.HTML(str(product_soup))
    return dom

def perform_request_with_retry(driver, url):
    MAX_RETRIES = 5
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            return extract_content(url)
            time.sleep(10)
        except:
            retry_count += 1
            if retry_count == MAX_RETRIES:
                raise Exception("Request timed out")
            time.sleep(60)

def get_product_urls(driver):
    product_urls = []
    MAX_PAGES = 5
    current_page = 1
    while current_page <= MAX_PAGES:
        page_content = driver.page_source
        product_soup = BeautifulSoup(page_content, 'html.parser')
        dom = etree.HTML(str(product_soup))
        product_urls_xpath = dom.xpath("//div[@class='post hentry']//h3[@class='post-title entry-title']//a/@href")
        product_urls.extend(product_urls_xpath)
        next_button = driver.find_element_by_xpath("//span[@class='displaypageNum']/a[contains(text(), 'Next »')]")
        if next_button:
            next_button.click()
            current_page += 1
            time.sleep(10)
        else:
            break 
    return product_urls

def extract_title_and_content(dom):
    title_xpath = '//h3[@class="post-title entry-title"]/text()'
    title = dom.xpath(title_xpath)[0].strip()
    content_xpath = '//div[@class="post-body entry-content"]//p//text()'
    content = ' '.join(dom.xpath(content_xpath)).strip()
    return {'title': title, 'content': content}

def main():
    url = "https://www.lawweb.in/"
    dom = extract_content(url)
    product_urls = get_product_urls(driver)
    print(len(product_urls))
    
    data = []
    for i, url in enumerate(product_urls):
        dom = extract_content(url)
        result = extract_title_and_content(dom)
        print(url, result)
        data.append({'product_url': url, 'content':result})

        if i % 10 == 0 and i > 0:
            print(f"Processed {i} links.")

        if i == len(product_urls) - 1:
            print(f"All information for {i + 1} links has been scraped.")

    df = pd.DataFrame(data)
    df.to_csv('product_data.csv')
    print('CSV file has been written successfully.')
    driver.close()


if __name__ == '__main__':
    main()

