#!/usr/bin/env python3

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import sys

# CSS Variables
titleClass = "h1"
titleName = "_1GTSsh _2Q73m9"
ratingClass = "span"
ratingName = "XqYSS8 AtzNiv"
synopsisClass = "div"
synopsisName = "_3qsVvm _1wxob_"
# genreClass = "_1NNx6V"  For future use

storeFrontURL = "https://www.amazon.com/gp/video/storefront/"
vidDownloadURL = "/gp/video/detail"

videoLinks, titles, ratings, synopsis = [], [], [], []


def scrapeText(lst, classType, className):
    findClass = soup.find_all(classType, class_=className)
    if len(findClass) == 0:
        lst.append(None)
    else:
        for n in findClass:
            if className == ratingName:
                lst.append(float(n.text[-3]))
            else:
                lst.append(n.text)


def initializeArgs():
    try:
        first, second = int(sys.argv[1]), int(sys.argv[2])
    except ValueError as v:
        print("Error:", v)
        print("Initializing default Values")
        first, second = 30, 5
    return first, second


try:
    # Initialize Browser
    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.get(storeFrontURL)

    no_of_records, ratings_above = initializeArgs()
    elements = driver.find_elements_by_xpath("//a[@href]")
    for element in elements:
        if vidDownloadURL in element.get_attribute("href"):
            videoLinks.append(element.get_attribute("href"))

    videoLinks = list(dict.fromkeys(videoLinks))

    # Get no_of_records of movies (default 30)
    for i in range(no_of_records):
        driver.get(videoLinks[i])
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')

        scrapeText(titles, titleClass, titleName)
        scrapeText(ratings, ratingClass, ratingName)
        scrapeText(synopsis, synopsisClass, synopsisName)

    data = {'Title': titles, 'Rating': ratings, 'Synopsis': synopsis}
    df = pd.DataFrame(data)
    df.to_csv('PrimeVideos.csv', index=False, encoding='utf-8')


    def wordCloudGenerator(dataframe, filename):
        if len(dataframe) > 1:
            text = ' '.join(dataframe.Synopsis)
            wc = WordCloud().generate(text)

            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")

            plt.savefig(filename + ".png")


    dfAbove = df.loc[(df['Rating'] >= ratings_above)]
    wordCloudGenerator(dfAbove, ("rating_above_" + str(ratings_above)))

    if ratings_above in ratings:
        print("Success - Word Cloud Generated !!!")
    else:
        print(f"Failure - No ratings are above or equal to {ratings_above}. Sorry, No Word Cloud Generated.")
except Exception as ex:
    print("Error:", ex)
finally:
    driver.quit()
