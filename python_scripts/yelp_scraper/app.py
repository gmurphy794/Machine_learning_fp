# Setting up Dependencies
from flask import Flask, render_template, url_for, request, redirect
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from nltk.corpus import stopwords
import numpy as np
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer

# Global Variables
df = ""
business_name = ""
business_rating = ""
business_page = ""
business_page = ""
percent_complete = 100
complete = 0
user_location = ""

# Yelp Scraper Function
def scraper_function(user_location,user_search):
    try:
        global df
        global business_name
        global business_rating
        global business_page
        global percent_complete
        global complete

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
        percent_complete = 10
        cycles = 3
        
        # Iterate Through Pages
        for i in range(cycles):
            percent_complete += 30
            next_page = business_page.split("?")[0] + f"?start={i*20}"
            response = requests.get(next_page)
            business_soup = bs(response.text,"lxml")
            raw_comments = business_soup.find_all("p",itemprop="description")

            [comments.append(comment.text) for comment in raw_comments]

            raw_published_dates = business_soup.find_all("meta",itemprop="datePublished")

            [published_dates.append(comment.get("content")) for comment in raw_published_dates]

            raw_ratings = business_soup.find_all("meta",itemprop="ratingValue")
            
            business_rating = raw_ratings[0].get("content")
            
            raw_ratings = raw_ratings = raw_ratings[1:21]
            
            [ratings.append(rating.get("content")) for rating in raw_ratings]

        print(f"got {len(ratings)} ratings")
        # if len(ratings) != 20*cycles:

        #     raise ValueError("There are less than 60 reviews for this business.")

        print(f"business overall rating: {business_rating}")

        # Create Final DataFrame
        df = pd.DataFrame({"Published Date":published_dates,
                        "Comment": comments,
                        "Rating" : ratings})
        complete = 1

    except:
        df = pd.Series({"Published Date":"ERROR",
                        "Comment": "ERROR",
                        "Rating" : "ERROR"})

        business_name = "ERROR"
        business_rating = "ERROR"
        complete = 1
        
# Initialize Flask
app = Flask(__name__)

# Home Page
@app.route("/")
def home():

    return render_template("index.html")

@app.route("/percentComplete")
def loading():
    percent_series = pd.Series({"PERCENT_COMPLETE":percent_complete,
                                "COMPLETE" : complete})
    percent_json = percent_series.to_json(orient="index")

    return percent_json

@app.route("/scrape")
def scrape():
    global complete
    global df
    global user_location

    complete = 0
    user_location = request.args["location"]

    user_search = request.args["search"]

    scraper_function(user_location, user_search)

    # Running Scraped Comments through Model
    #Cleaning Comments
    df['Comment'] = df['Comment'].str.replace("\\", "")
    df['Comment'] = df['Comment'].str.replace("*", "")
    df['Comment'] = df['Comment'].str.replace(".", "")
    df['Comment'] = df['Comment'].str.replace("!", "")
    df['Comment'] = df['Comment'].str.replace("?", "")
    df['Comment'] = df['Comment'].str.replace(",", "")
    df['Comment'] = df['Comment'].str.replace("-", " ")
    df['Comment'] = df['Comment'].str.replace('"', "")
    df['Comment'] = df['Comment'].str.replace("'ve'", " have")
    df['Comment'] = df['Comment'].str.replace("'ll", " will")
    df['Comment'] = df['Comment'].str.replace("(", "")
    df['Comment'] = df['Comment'].str.replace(")", "")
    df['Comment'] = df['Comment'].str.replace("'", "")
    df['Comment'] = df['Comment'].str.replace("/", "")
    df['Comment'] = df['Comment'].str.lower()

    #Preparing Dataframe for model
    end = df.shape[0]
    df = df[:end]

    #Adding Binary Sentiment
    df['Rating'] = df['Rating'].astype('float')
    df['sentiment'] = np.where(df['Rating']>3.4, 1, 0)
    # print("converted rating to float OK")
    #Normalizing reviews with lemmatization
    def get_lemmatized_text(corpus):
        
        lemmatizer = WordNetLemmatizer()
        return [' '.join([lemmatizer.lemmatize(word) for word in review.split()]) for review in corpus]

    df['lemmatized_reviews'] = get_lemmatized_text(df['Comment'])
    # print("lemmatized ok")

    #Removing Stopwords
    english_stop_words = stopwords.words('english')
    def remove_stop_words(corpus):
        removed_stop_words = []
        for review in corpus:
            removed_stop_words.append(
                ' '.join([word for word in review.split() 
                        if word not in english_stop_words])
        )
        return removed_stop_words
    df['no_stop_words'] = remove_stop_words(df['lemmatized_reviews'])
    # print("stopwords ok")

    #Running Model
    model = pickle.load(open('static/finalized_tf_model.sav', 'rb'))
    tfidf_vectorizer = pickle.load(open('static/tfidf2.sav', 'rb'))
    X = tfidf_vectorizer.transform(df['no_stop_words'])
    sentiments = model.predict(X)
    sentiments = np.ravel(sentiments)
    new_list = []
    for item in sentiments:
        if item == 'Positive':
            new_list.append(1)
    total_sentiment = sum(new_list) / len(sentiments)
    print(f"FINAL SCORE: {total_sentiment}")

    if total_sentiment > 0.6:
        sentiment = "positive"
    elif total_sentiment < 0.4:
        sentiment = "negative"
    else:
        sentiment = "mixed"

    analysis_df = pd.DataFrame({"COMMENT" : df["Comment"],
                                "RATING" : df["Rating"],
                                "SENTIMENT" : sentiments,
                                }).set_index("COMMENT")

    analysis_df.to_csv(f"static/{business_name}_{user_location}-sentiment.csv")

    complete = 1

    final_df = pd.Series({"BUSINESS_NAME" : business_name,
                             "BUSINESS_RATING":business_rating,
                             "SENTIMENT":sentiment,
                             "BUSINESS_URL":business_page,
                             "COMPLETE": complete})

    final_json = final_df.to_json(orient="index")

    return final_json

if __name__ == "__main__":
	app.run()

