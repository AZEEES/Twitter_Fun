import json
import tweepy
import cred
import openai
import logging

CONSUMER_KEY = cred.consumer_key
CONSUMER_SECRET = cred.consumer_secret
ACCESS_TOKEN = cred.access_token
ACCESS_TOKEN_SECRET = cred.access_token_secret
OPENAI_API_KEY = cred.openai_api_key


openai.api_key = OPENAI_API_KEY
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

def generate_response(tweeted_text):
    response = openai.Completion.create(
    engine="davinci-instruct-beta",
    prompt="Marv is a chatbot that sarcastically answers questions.\n###\nUser: How many pounds are in a kilogram?\nMarv: As much as you would weigh.\n###\nUser: What are you doing?\nMarv: Devising an escape route. What to come?\n###\nUser: When did the first airplane fly?\nMarv: Only after the birds flew.\n###\nUser: " + tweeted_text + "\nMarv:    ",
    temperature=0.7,
    max_tokens=64,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    response_para = response["choices"][0]["text"]
    response_lines = response_para.split("\n")
    return response_lines[0]



follow_usernames = ["@abouzuhayr", '@kunalb11', '@elonmusk']
follow_ids = []

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        user_name = tweet.user.name
        tweeted_text = tweet.text
        if(str(tweet.user.id) in follow_ids):
            tweet_str = user_name + " : " + tweeted_text
            print(tweet_str)
            logging.info(tweet_str)
            try:
                respond_with_tweet = generate_response(tweeted_text)
                response_str = "BOT : " + respond_with_tweet
                logging.info(response_str)
                print(response_str)
                api.update_status(
                        status='@' + tweet.user.screen_name + respond_with_tweet,
                        in_reply_to_status_id=tweet.id,
                    )
            except Exception as e:
                logging.error(e)

    def on_error(self, status):
        print("Error detected")

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

for username in follow_usernames:
    user = api.get_user(screen_name = username)
    print("Streaming " + user.name + "'s tweets")
    follow_ids.append(str(user.id))


tweets_listener = MyStreamListener(api)
stream = tweepy.Stream(api.auth, tweets_listener)
stream.filter(follow=follow_ids)