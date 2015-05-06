from urllib2 import urlopen
import json
import requests
import re
import time

username_list = ('jakevdp','ivezic','davidwhogg','profjsb','dhuppenkothen','drphilmarshall','fperez','kbarbary','jonathansick','Waelthus','nell-byler','jradavenport','gully','bareid','ogtelford','sofiatti','karenyyng','adrn','kapadia','rbiswas4','rhiannonlynne','lvrzhn','jmankin','wilmatrick','RuthAngus','nhuntwalker','ryanmaas','patti','yoachim','yalsayyad')


github_credentials = json.loads(open("/home/ubuntu/.github").read())
github_token = github_credentials['access_token']

#ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

global api_url
api_url = 'https://api.github.com/'

element_pat = re.compile(r'<(.+?)>')
rel_pat = re.compile(r'rel=[\'"](\w+)[\'"]')

def parseLinkHeaders(headers):
    link_s = headers.get('link', '')
    urls = element_pat.findall(link_s)
    rels = rel_pat.findall(link_s)
    d = {}
    for rel,url in zip(rels, urls):
        d[rel] = url
    return d


def getPagedRequest(url):
    """get a full list, handling APIv3's paging"""
    results = []
    while url:
        print("fetching %s" % url)
        f = urlopen(url)
        results_json = json.load(f)
        if type(results_json) == list:
            results.extend(results_json)
        else:
            results.extend([results_json])
        
        links = parseLinkHeaders(f.headers)
        url = links.get('next')
        time.sleep(0.25)
    return results

def retrieveUserInfo(username):
    user_api_url = 'users/%s'%username
    url = api_url + user_api_url + "?access_token=%s"%github_token
    print url
    user_info = getPagedRequest(url)[0]
    
    time.sleep(1)
    #try:
    #events_api_url = user_info['events_url'][:-10] + "/public"
    #print events_api_url
    #user_events = getPagedRequest(events_api_url)
    return {"info" : user_info}


def retrieveAllUserInfo(username_list):

    dic = {}

    for u in username_list:
        dic[u] = retrieveUserInfo(u)

    return dic

if __name__ == '__main__':
    print "blah"
    #user_events = 'users/%s'%'jakevdp'
    #url = api_url + user_events + "?access_token=%s"%github_token
    #print url
    #test = getPagedRequest(url)
    
    #for i in range(len(test)):
    #    print test[i]['type'],test[i]['created_at'],test[i]['repo']['name']
    