
import twitter    #Twitter dan verilerimizi çekmemizi sağlar
import json       #verileri json formatında çekeriz.


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import Birch                             # makine öğrenmesini kullandığımız kütüphane


import numpy as np                          #rakamlarla ilgili işlemler yapmamızı sağlar



#Twitter Baglantıları

CONSUMER_KEY = "xxxxxxxxxxxxxxxxx"                                  #twitter keyleri
CONSUMER_SECRET = "xxxxxxxxxxxxxxx"
OAUTH_TOKEN = "xxxxxxxxxxxxxxxxxxxx"
OAUTH_TOKEN_SECRET = "xxxxxxxxxxxxxxxxxxxx"

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)

#Adres tanımlayıcılar
                                #flickr sitesinden
WORLD_WOE_ID = 1    # Tum dunya icin yahoo verileri alırken 1 kullanılır. #dünyadan verileri çekmek için konum belirler
TR_WOE_ID = 23424969        # turkiyekonum=23424969  US_WOE_ID = 23424977

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
tr_trends = twitter_api.trends.place(_id=TR_WOE_ID)


"""
print (json.dumps(world_trends, indent=1))

print (json.dumps(us_trends, indent=1))

"""
world_trends_set = set([trend['name']                        # atayacagımız trend listelerini oluşturuyoruz.
                        for trend in world_trends[0]['trends']])

tr_trends_set = set([trend['name']
                     for trend in tr_trends[0]['trends']])

common_trends = world_trends_set.intersection(tr_trends_set)

# print common_trends


from urllib.parse import unquote  # url ile işlem yapmamızı sağlıyorr

anahtar_kelime = '#ekim'          #ornek konu verilir  --  #///////////////////////////////

count = 200

search_results = twitter_api.search.tweets(q=anahtar_kelime, count=count)  #twitter trendleri içinde anahtar kelimeyi arıyor.

statuses = search_results['statuses']     #anahtar kelimenin bulunduğu tweetleri duruma atıyor.

for _ in range(5):

    try:
        next_results = search_results['search_metadata']['next_results']
    except (KeyError):
        break

kwargs = dict([kv.split('=') for kv in unquote(next_results[1:]).split("&")])
search_results = twitter_api.search.tweets(**kwargs)
statuses += search_results['statuses']


#print(json.dumps(statuses[0], indent=1))


status_texts = [ status['text']
                 for status in statuses ]

screen_names = [ user_mention['screen_name']     #çekilen twxtler içindeki kullanıcı adı,hashtag adı gibi özellikler atanıyor.
                 for status in statuses
                     for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text']
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]

words = [ w
          for t in status_texts
              for w in t.split() ]    #kelimeyi parçaladığımız yer


#//////////////////////////////////////////ekle2
urls = [urls['url']
        for status in statuses
        for urls in status['entities']['urls']]

texts = [status['text']
         for status in statuses
         ]

created_ats = [status['created_at']
               for status in statuses
               ]



#/////////////////////////////////////////////////

"""
print(json.dumps(status_texts[0:5], indent=1))
print(json.dumps(screen_names[0:5], indent=1) )
print(json.dumps(hashtags[0:5], indent=1))
print(json.dumps(words[0:5], indent=1))
"""

from collections import Counter     # sayac kullanmamızı sağladı

for item in [words, screen_names, hashtags]:
    c = Counter(item)
   # print(c.most_common()[:20])

from prettytable import PrettyTable   #Tablo olusturmak icin

                                            #İcinde gündem bulunan en cok birlikte tekrar eden kelimeler (RT edilenler)
for label, data in (('Kelimeler', words),
                        ('Kullanıcı Adı', screen_names),  #İcinde q(anahtar hashtag kelime) kullanan kullanıcılar
                        ('Hashtags /Trendler', hashtags)):         #Baglantılı diğer hashtagler
        tablo_degerler = PrettyTable(field_names=[label, 'Sayi'])       #Tablo icine yazıldı.
        c = Counter(data)
        [tablo_degerler.add_row(kv) for kv in c.most_common()[:20]]  # 20 adet listelenecek.
        tablo_degerler.align[label], tablo_degerler.align['Sayi'] = 'l', 'r'
        print(tablo_degerler)

#bitti

 #/////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////////////////////////////////////////////////////////////
#devamm

retweets = [

    (status['retweet_count'],
     status['retweeted_status']['user']['screen_name'],
     status['text'])


    for status in statuses

        if  'retweeted_status' in status
]

rt_tablo = PrettyTable(field_names=['RT_Sayisi', 'Kullanıcı Adı', 'Tweet'])
[ rt_tablo.add_row(row) for row in sorted(retweets, reverse=True)[:5] ]
rt_tablo.max_width['Text'] = 50
rt_tablo.align= 'l'
#print(rt_tablo)  #tabloya yazdırılabilir.

#///////////////////////////////////////////////////////////////////////////////////////////
#matlab da grafikler

word_counts = sorted(Counter(words).values(), reverse=True)

import matplotlib.pylab as plt            #grafikleri kullanmak için matlab kütüphanesi tanımladık

"""
plt.loglog(word_counts)
plt.ylabel("Frekansı/ Sıklık")
plt.xlabel(" ") """
#plt.show();

for label, data in ( ('Kelimeler', words),
                    ('Kullanıcı Adı', screen_names),
                    ('Hashtags /Trendler', hashtags)):


    c = Counter(data)
    plt.hist(c.values())

    plt.title(label)
    plt.ylabel("Kaç öge olduğu (kelime,hashtag,kullanıcı sayısı)") #ögelerin sayılarının toplamı
    plt.xlabel(" O ögenin(kelime,hashtag,kullacısı adı) sayısı")   #örn o ögenin değeri hangi değer aralığında

    plt.show();

#///////////////////////////////////////////////////////////////////////////////////matlabbitis


vectorizer = CountVectorizer(analyzer="word", \
                             tokenizer=None, \
                             preprocessor=None, \
                             stop_words='english', \
                             max_features=5000)  #5000 di

train_data_features = vectorizer.fit_transform(texts)      #metindeki kelimeler eğitim verisi özellikleri atanır

train_data_features = train_data_features.toarray()                    #eğitim verileri diziye alınır.

#print(train_data_features.shape) #

#print(train_data_features)      #

vocab = vectorizer.get_feature_names()           #vektörerdeki veri özelliklerini ayrı kelimeler olarak atarız.
#print(vocab)  #

dist = np.sum(train_data_features, axis=0)     #küme özelliklerini topladık

"""
for tag, count in zip(vocab, dist):       
    print(count, tag)               
                                              
"""

LatentDirichletAllocation = Birch(branching_factor=50, n_clusters=6, threshold=0.5, compute_labels=True)
LatentDirichletAllocation.fit(train_data_features)

clustering_result = LatentDirichletAllocation.predict(train_data_features)   #eğitilen verilere göre gelen tweetler kümelenir
#print("\nGruplama:\n")   #
#print(clustering_result)   #



"""
# Outputting some data
print(json.dumps(hashtags[0:50], indent=1))
print(json.dumps(urls[0:50], indent=1))
print(json.dumps(texts[0:50], indent=1))
print(json.dumps(created_ats[0:50], indent=1))



with open("data.txt", "a") as myfile:
    for w in hashtags:
        myfile.write(str(w.encode('ascii', 'ignore')))
        myfile.write("\n")
"""


# kelime sıklığı
wordcounts = {}
for term in hashtags:
    wordcounts[term] = wordcounts.get(term, 0) + 1

items = [(v, k) for k, v in wordcounts.items()]

#print(len(items))  #

xnum = [i for i in range(len(items))]
#for count, word in sorted(items, reverse=True): #
 # print("%5d %s" % (count, word))   #


plt.figure()
plt.title("Trend Analizi")

myarray = np.array(sorted(items, reverse=True))  #trendleri sıralarız.

#print(myarray[:, 0])  #

#print(myarray[:, 1])   #

plt.xticks(xnum, myarray[:, 1], rotation='vertical')                       #matlab grafiği
plt.plot(xnum, myarray[:, 0])                                            #matlab gösteririz.
plt.show()



#////////////////////////////////////////////////////////////////////////////////


 # örnek konu üzerinde trendleri belirliyoruz.



