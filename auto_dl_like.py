from coni_api import coni_instagram
import requests
import re
import os


web_browser = requests.session()


def download_file(url, filename):
    response = web_browser.get(url)
    
    with open("%s" % filename, "wb") as fichier:
        fichier.write(response.content)


users = ["clairo","clairo98","wavycolde","mxmtoon","clairo98","clairoiscute","radvxz","charlie.caloy","yerin_the_genuine","sounditsme","themarias","n0tclairo","ph1boyyy","liso.exe","vuongdustin","wavyseoul","jenn_scale","ashleythejohnson","nakedbibi"]
client = coni_instagram(cookies_file="ni.coni.coni")

for user in users:
    count = 0
    print(user)
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
                    count += 1
                    download_file(i, folder + filename)
            else:
                filename = re.search(r"\/(.+)\/(?P<filename>(.+))\?",url).group("filename")
                count += 1
                download_file(url, folder + filename)

        else:
            if count != 0:

                print("%s new post(s) from %s " % (count,user))
            break

