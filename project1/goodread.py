import requests

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VV7lwfoxGUDEu41SlNnJA", "isbns": "9781632168146"})

print(res.json())
