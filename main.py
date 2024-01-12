from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import cloudscraper
import time
import random
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.firefox.options import Options

app = Flask(__name__)


def scrape_quizlet(url):
    start_time = time.time()
    options = Options()
    options.add_argument("--headless")
    print("Starting browser...")
    driver = webdriver.Firefox(options=options)
    print("Started browser...\nWebsite loading...")
    t = time.time()
    driver.set_page_load_timeout(20)
    try:
        driver.get(url)
    except:
        driver.execute_script("window.stop();")
    print('Time consuming:', time.time() - t)
    print("Loaded Website...\nsleeping :)")
    time.sleep(1)
    print("slept :zzz:")

    print("Getting page source...")
    imfallsodaten = driver.page_source
    print("quitting driver...")
    driver.quit()
    print("Driver quit...")
    soup = BeautifulSoup(imfallsodaten, "html.parser")

    result_array = []

    for i, (question, answer) in enumerate(
        zip(
            soup.select("a.SetPageTerm-wordText"),
            soup.select("a.SetPageTerm-definitionText"),
        ),
        1,
    ):
        result_array.append([question.text, answer.text])

    set_name_element = soup.find("div", class_="SetPage-breadcrumbTitleWrapper").find(
        "h1"
    )
    set_name = set_name_element.text if set_name_element else None
    end_time = time.time()

    elapsed_time = end_time - start_time
    cache_lookup_time = -1
    cachehit = False
    cacheage = 0
    now = datetime.now()
    #if elapsed_time < 0.8:
    #    cachehit = True
    #    cache_lookup_time = 0
    #    cacheage = 300

    result_json = {
        "result": {"name": set_name, "pairs": result_array},
        "cache_lookup_time": cache_lookup_time,
        "processing_time": elapsed_time,
        "cache_hit": cachehit,
        "age": cacheage,
        "stale": False,
        "enqueued": False,
    }

    return result_json


@app.route("/scrape", methods=["GET"])
def get_quizlet_data():
    quizlet_id = request.args.get("id")

    if not quizlet_id:
        return jsonify({"error": "Missing 'id' parameter in the request"}), 400

    result = scrape_quizlet("https://quizlet.com/"+quizlet_id)
    return jsonify(result)


@app.route("/forceQueue/<id>", methods=["GET"])
def forceQueueClearCache(id):
    result_json = {
        "success" : True,
        "result": f"cache {id} cleared successfully if present"
    }
    return jsonify(result_json)


@app.errorhandler(404)
def not_found(e):
    return "File not found."


if __name__ == "__main__":
    app.run(debug=False)
