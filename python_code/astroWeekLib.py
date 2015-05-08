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


def pwlaw_fit_cont(dataset,threshold):
    # Maximum Likelihood Hill Estimator 
    # Use this method only for continuous distributions or if your threshold is superior to btw. 7 to 10
    
    
    data = np.asarray(dataset)
    data = data[data>=threshold]
    n = len(data)
    x = data/threshold
    mu = n/sum(np.log(x))
    
    confidence = 2/np.sqrt(n)
    
    return mu,confidence,n


def pwlaw_fit_disc(dataset,threshold=1,Newton_Iterations=20):
    # For detailed Method please refer to the long version Paper:
    # T.Maillart et al. Empirical Tests of Zipf's law Mechanism In Open Source Linux Distribution
        
    data = dataset[dataset>=threshold]
    data = np.asarray(data)
    
    
    I = np.asarray(range(threshold,250*threshold))/threshold
    mu =0.    
    
    rhs = 1/float(len(data))*sum(np.log(data/threshold))
    
    #print 'sum log data', sum(N.log(data/threshold))
    #print 'rhs',rhs
    
    for i in range(Newton_Iterations):
        #print i
        f = sum(np.log(I)/(I**(1+mu)))/sum(1/I**(1+mu))
     
        a = - sum((np.log(I)**2)/I**(1+mu))
        b = sum(1/I**(1+mu))
        c = sum(np.log(I)/I**(1+mu))
        d = sum(1/I**(1+mu))
        
        fprime = (a*b-c**2)/(d**2)        
        mu = mu + (rhs-f)/fprime
        error = (rhs-f)/fprime
        
    #    mui = N.append(mui,mu)
    #    eri = N.append(eri,2)
       
    return mu,error


if __name__ == '__main__':
    print "blah"
    #user_events = 'users/%s'%'jakevdp'
    #url = api_url + user_events + "?access_token=%s"%github_token
    #print url
    #test = getPagedRequest(url)
    
    #for i in range(len(test)):
    #    print test[i]['type'],test[i]['created_at'],test[i]['repo']['name']
    