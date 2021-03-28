# Je perd beaucoup de temps dans ma vie à scroll sur instagram. Je veux juste supporter et voir les posts des peersonnes qui m'intéresse vraiment

from coni_api import coni_instagram
import requests
import re
import os


def download_file(url, filename):
    response = web_browser.get(url)
    
    with open("%s" % filename, "wb") as fichier:
        fichier.write(response.content)


users = ["clairo","wavycolde"]
client = coni_instagram(cookie_file="ni.coni.coni")
web_browser = client.browser_session

for user in users:
    posts = client.get_every_post(user, layer=0)
    if user == "clairo":
        posts.pop(0)
    folder = "/sdcard/noinsta/%s/" % user

    temp = ""
    for path in folder.split("/"):
        temp += "%s/" % path
        if os.path.isdir(temp) is False:
            os.mkdir(temp)

    for post in posts:

        shortcode = post["shortcode"]
        if client.is_post_liked(shortcode) == False:
            client.like_post(post["id"])
            url = client.get_posts_media_link(post)
            if type(url) == list:
                for i in url:
                    filename = re.search(r"\/(.+)\/(?P<filename>(.+))\?",i).group("filename")
                    print(user)
                    download_file(i, folder + filename)
            else:
                filename = re.search(r"\/(.+)\/(?P<filename>(.+))\?",url).group("filename")
                print(user)
                download_file(url, folder + filename)

        else:
            print("%s done" % user)
            break

