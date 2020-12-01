import uuid, hashlib, hmac, random
import urllib.parse

import pickle, requests
import json
import re

class coni_instagram:

    def __init__(self,login=None,password=None,cookies_file=None):

        # initie une session requests pour la navigation
        self.headers = self.__default_headers()
        self.browser_session = requests.session()
        cookie_loaded = False

        username = login
        password = password
        self.device_id = self.__generate_deviceid()
        self.guid = self.__generate_uuid(False)
        self._uuid = self.guid
        self.adid = self.__generate_adid(username)
        self.phone_id = self.__phone_id(self.device_id)
        self._csrftoken = None
        login_attempt_count = str(0)

        # Charge le cookie ici
        if cookies_file != None:
            try:
                with open(cookies_file, 'rb') as f:
                    self.browser_session.cookies.update(pickle.load(f))
                cookie_loaded = True
                print("Utilisation du cookie..")
            except FileNotFoundError:
                pass

        if cookie_loaded is False:
            print("Utilisation des logins..")
            if login == None or password == None:    
                raise Exception("Wrong login/password or cookie file")
            else:
                req = self.make_get("https://instagram.com/",headers=self.headers)
                self._csrftoken = self.__extract_csrftoken(req.text)

                json_params = '{"device_id":"'+self.device_id+'","guid":"'+self.guid+'","adid":"'+self.adid+'","phone_id":"'+self.phone_id+'","_csrftoken":"'+self._csrftoken+'","username":"'+username+'","password":"'+password+'","login_attempt_count":"'+login_attempt_count+'"}'
                hash_sig = self.__generate_signature(json_params)

                post_params = {
                    'ig_sig_key_version': '4',
                    'signed_body': hash_sig + '.' + json_params
                }
                data_login = urllib.parse.urlencode(post_params).encode('ascii')
                url = "https://i.instagram.com/api/v1/accounts/login/"

                login_reponse = self.make_post(url,data=data_login,headers=self.headers)

                if login_reponse != 200:
                    raise Exception("Impossible to login")       
                else:
                    self.save_session(filename="bot_coni.cookie")
        
        if self._csrftoken == None:
            self._csrftoken = self.browser_session.cookies.get_dict()["csrftoken"]

        self._uid = self.browser_session.cookies.get_dict()["ds_user_id"]
                    
        

    def make_post(self,url,data,headers=None):
        if headers == None:
            headers = self.headers

        request = self.browser_session.post(url,data=data,headers=headers)
        return request.status_code

    def make_get(self,url,headers=None):
        self.query_hash = "003056d32c2554def87228bc3fd9668a"
        if headers == None:
            headers = self.headers

        requete = self.browser_session.get(url,headers=headers)

        csft_token = self.__extract_csrftoken(requete.text)
        if csft_token != None:
            self._csrftoken = csft_token
            
        return requete
        
# Generation d'un data correct ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __generate_uuid(self,return_hex=False, seed=None):
        if seed:
            m = hashlib.md5()
            m.update(seed.encode('utf-8'))
            new_uuid = uuid.UUID(m.hexdigest())
        else:
            # le plus interessant est quand il n'y a pas de seed
            new_uuid = uuid.uuid1()
        if return_hex:
            return new_uuid.hex

        return str(new_uuid)

    def __generate_deviceid(self,seed=None):
        return 'android-{0!s}'.format(self.__generate_uuid(True, seed)[:16])

    def __extract_csrftoken(self,text):
        csrf_token = re.search(r"[a-zA-Z0-9]{32}", text)
        if csrf_token != None:
            return csrf_token.group()
        else:
            return None

    def __generate_adid(self,username, seed=None):
            modified_seed = username
            if modified_seed:
                sha2 = hashlib.sha256()
                sha2.update(modified_seed.encode('utf-8'))
                modified_seed = sha2.hexdigest()
            return self.__generate_uuid(False, modified_seed)

    def __phone_id(self,device_id):
            return self.__generate_uuid(return_hex=False, seed=device_id)

    def __generate_signature(self,data):
            signature_key = "19ce5f445dbfd9d29c59dc2a78c616a7fc090a8e018b9267bc4240a30244c53b"
            return hmac.new(
                signature_key.encode('ascii'), data.encode('ascii'),
                digestmod=hashlib.sha256).hexdigest()

# Generation de Header par defaut ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __default_headers(self):
        return {
            'User-Agent': "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)",
            'Connection': 'close',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'X-IG-Capabilities': "3brTvw==",
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Connection-Speed': '{0:d}kbps'.format(random.randint(1000, 5000)),
            'X-IG-App-ID': "567067343352427",
            'X-IG-Bandwidth-Speed-KBPS': '-1.000',
            'X-IG-Bandwidth-TotalBytes-B': '0',
            'X-IG-Bandwidth-TotalTime-MS': '0',
            'X-FB-HTTP-Engine': "Liger",
            'Content-type':'application/x-www-form-urlencoded; charset=UTF-8'
        }

# Recuperer les informations d'un post
    def get_json_post(self,text):
        post = ""
        phase = 0
        count_1 = 0
        count_2 = 0
        posts = []

        for letter in text:
            post += letter
            # please someone teach me regex or something else like that
            if phase == 0:
                if "{\"__typename" in post:
                    count_1 += 1
                    post = post.split(":")[-1]
                    phase = 1

            if phase == 1:
                if letter == "{":
                    count_1 += 1
                if letter == "}":
                    count_2 += 1 

                if count_1 == count_2:
                    post = post.replace("\\u0026","&")
                    posts.append(json.loads(post))
                    count_1 = 0
                    count_2 = 0
                    phase = 0
                    post = ""
        return posts

    def jsoned(self,text):
        return json.loads(text)

    def get_query_hash(self,text):
        return re.search(r'byTagName.get\([a-zA-Z][)]{1,2}.pagination},queryId:"[a-zA-Z0-9]{32}"',text).group().split('"')[1]

    def get_every_post(self,username):

        posts = []
        requete = self.make_get("https://www.instagram.com/" + username)

        for i in self.get_json_post(requete.text):
            posts.append(i)

        user_information_requete = self.make_get("https://www.instagram.com/"+username+"/?__a=1")
        user_informations = json.loads(user_information_requete.text)

        loop_post = int(user_informations["graphql"]["user"]["edge_owner_to_timeline_media"]["count"] / 12)
        user_id = user_informations["graphql"]["user"]["id"]
        end_cursor = user_informations["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]

        for i in range(loop_post):
            next_post_url = "https://www.instagram.com/graphql/query/?query_hash="+self.query_hash+"&variables="+"{\"id\":\""+user_id+"\",\"first\":12,\"after\":\""+end_cursor+"\"}"
            next_post = self.make_get(next_post_url,headers=self.headers)

            for i in self.get_json_post(next_post.text):
                posts.append(i)

            post_information  = json.loads(next_post.text)
            try:
                end_cursor = post_information["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            except:
                print("ERREUR:",i)
                pass

        return posts

    def like_post(self,id_post):

        id_post = str(id_post)
        url = "https://i.instagram.com/api/v1/media/"+id_post+"/like/?d=1"

        json_params = '{"media_id":"'+id_post+'","module_name":"feed_timeline","radio_type":"wifi-none","_csrftoken":"'+self._csrftoken+'","_uuid":"'+self._uuid+'","_uid":"'+self._uid+'"}'
        hash_sig = self.__generate_signature(json_params)
        
        post_params = { 
            'ig_sig_key_version':'4',
            'signed_body': hash_sig + '.' + json_params
        }
        hash_sig = self.__generate_signature(json_params)
        data_like = urllib.parse.urlencode(post_params).encode('ascii')

        req = self.make_post(url=url,data=data_like)
        print(req)
        return True

    def is_private(self,username):
        requete = self.make_get("https://www.instagram.com/" + username + "/?__a=1")
        user_infomations = json.loads(requete.text)
        return user_infomations["graphql"]["user"]["is_private"]


# Sauvegarder les cookies ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def save_session(self,filename=None, session=None):
        if session == None:
            session = self.browser_session
        with open(filename, 'wb') as f:
            pickle.dump(session.cookies, f)
        return True



coni_api = coni_instagram(login="bot_coni",password="mot_de_passe",cookies_file="bot_coni.cookie")
posts = coni_api.get_every_post("bot_coni")