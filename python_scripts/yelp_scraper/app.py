# Setting up Dependencies
from flask import Flask, render_template, url_for, request, redirect
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

# Global Variables
df = ""
business_name = ""
business_rating = ""

# Yelp Scraper Function
def scraper_function(user_location,user_search):
    try:
        global df
        global business_name
        global business_rating
        # Get URL For Top Hit in Search
        search_url = "https://www.yelp.com/search?find_desc=" + user_search + "&find_loc=" + user_location
        print(f"search url: {search_url}")
        response = requests.get(search_url)
        search_soup = bs(response.text,"lxml")

        # Get Page Source For Business Page
        raw_links = search_soup.find_all("a", class_="link-color--blue-dark__373c0__1mhJo")
        all_links = []
        [all_links.append(link.get("href")) for link in raw_links]
        processed_links = []
        [processed_links.append(link) for link in all_links if "/biz" in link]

        business_page = "https://www.yelp.com" + processed_links[0]

        response = requests.get(business_page)
        business_soup = bs(response.text,"lxml")

        business_name_raw = business_soup.find_all("h1",class_="biz-page-title")
        business_name_list = []

        [business_name_list.append(biz.text) for biz in business_name_raw]
        business_name = " ".join(business_name_list)
        print(f"business name: {business_name}")

        comments = []
        published_dates = []
        ratings = []

        # Iterate Through Pages
        for i in range(3):
            next_page = business_page + f"?start={i*20}"
            response = requests.get(next_page)
            business_soup = bs(response.text,"lxml")
            raw_comments = business_soup.find_all("p",itemprop="description")

            [comments.append(comment.text) for comment in raw_comments]

            raw_published_dates = business_soup.find_all("meta",itemprop="datePublished")

            [published_dates.append(comment.get("content")) for comment in raw_published_dates]

            raw_ratings = business_soup.find_all("meta",itemprop="ratingValue")
            
            business_rating = raw_ratings[0].get("content")
            
            raw_ratings = raw_ratings[1:len(raw_ratings)]
            
            [ratings.append(rating.get("content")) for rating in raw_ratings]

        print(f"business overall rating: {business_rating}")

        # Create Final DataFrame
        df = pd.DataFrame({"Published Date":published_dates,
                        "Comment": comments,
                        "Rating" : ratings})

    except:
        df = pd.Series({"Published Date":"ERROR",
                        "Comment": "ERROR",
                        "Rating" : "ERROR"})
        business_name = "ERROR"
        business_rating = "ERROR"


# Initialize Flask
app = Flask(__name__)

# Home Page
@app.route("/")
def home():

    return render_template("index.html")


@app.route("/scrape")
def scrape():

    user_location = request.args["location"]

    user_search = request.args["search"]

    scraper_function(user_location, user_search)

    # Results are in df
    df.head()

    # Run df results through Model HERE
    sentiment = "positive"

    final_df = pd.Series({"BUSINESS_NAME" : business_name,
                             "BUSINESS_RATING":business_rating,
                             "SENTIMENT":sentiment})

    final_json = final_df.to_json(orient="index")

    return final_json

if __name__ == "__main__":
	app.run(debug=True)

