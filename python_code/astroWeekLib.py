from urllib2 import urlopen
import json
import requests
import re
import time
import numpy as np
import sys

sys.path.append("/Users/maithoma/work/python/")
from tm_python_lib import *
from fitting_tools import *

username_list = ('jakevdp','ivezic','davidwhogg','profjsb','dhuppenkothen','drphilmarshall','fperez','kbarbary','jonathansick','Waelthus','nell-byler','jradavenport','gully','bareid','ogtelford','sofiatti','karenyyng','adrn','kapadia','rbiswas4','rhiannonlynne','lvrzhn','jmankin','wilmatrick','RuthAngus','nhuntwalker','ryanmaas','patti','yoachim','yalsayyad')


#github_credentials = json.loads(open("/home/ubuntu/.github").read())
#github_token = github_credentials['access_token']

#ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

global api_url
api_url = 'https://api.github.com/'

element_pat = re.compile(r'<(.+?)>')
rel_pat = re.compile(r'rel=[\'"](\w+)[\'"]')

def binning(x,y,bins,log_10=False,confinter=5):
    '''makes a simple binning'''

    x = np.array(x);y = np.array(y)

    if isinstance(bins,int) or isinstance(bins,float):
        bins = np.linspace(np.min(x)*0.9,np.max(x)*1.1,bins)
    else:
        bins = np.array(bins)

    if log_10:
        bins = bins[bins>0]
        c = x > 0
        x = x[c]
        y = y[c]
        bins = np.log10(bins)
        x = np.log10(x)
        y = np.log10(y)

    Tbins = []
    Median = []
    Mean = []
    Sigma =[]
    Perc_Up = []
    Perc_Down = []
    Points=[]


    for i,ix in enumerate(bins):
        if i+2>len(bins):
            break

        c1 = x >= ix
        c2 = x < bins[i+1]
        c=c1*c2

        if len(y[c])>0:
            Tbins = np.append(Tbins,np.median(x[c]))
            Median =  np.append(Median,np.median(y[c]))
            Mean = np.append(Mean,np.mean(y[c]))
            Sigma = np.append(Sigma,np.std(y[c]))
            Perc_Down = np.append(Perc_Down,np.percentile(y[c],confinter))
            Perc_Up = np.append(Perc_Up,np.percentile(y[c],100 - confinter))
            Points = np.append(Points,len(y[c]))


    return {'bins' : Tbins,
            'median' : Median,
            'mean' : Mean,
            'stdDev' : Sigma,
            'percDown' :Perc_Down,
            'percUp' :Perc_Up,
            'nPoints' : Points}



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


def plotPowerLawFit(loss,xmin=1,continuousFit=True,addnoise=False,confint=.01,plot=False):
    '''General power law plotting method from
    continuous data or discrete data with noise added
    '''


    loss,rank = rankorder(loss)
    y = rank

    if addnoise:
        x = loss + np.random.rand(len(loss)) - 0.5
    else:
        x = loss

    '''Normalized plot of the empirical distribution'''
    rankNorm = rank/float(rank[-1])
    rankMin = rankNorm[loss <= loss][-1]


    '''Plot of the fitted distribution'''
    mu,confidence,nPoints = pwlaw_fit_cont(x,xmin)
    print mu,confidence,nPoints

    xFit = np.logspace(np.log10(xmin),np.log10(max(loss)))
    yFit = (rankMin-0.03)*1/(xFit/float(xmin))**mu

    if plot:
        pl.loglog(loss,rankNorm,'k.' ,alpha=0.5)
        pl.loglog(xFit,yFit,'k-.')

    '''Add confidence intervals'''

    if confint:
        m,L,U,pvalue = bootstrapping(x,xmin,confint=confint,numiter = -1)
        x,y = rankorder(L)
        yLowerNorm = y/float(y[-1])
        #pl.loglog(x,yMin*yLowerNorm,'m')
        x,y = rankorder(U)
        yUpperNorm = y/float(y[-1])


    return {'x':loss,'y':rankNorm,'xFit':xFit,'yFit':yFit}

def bootstrapping(data,xmin,confint=.05,numiter = -1,plot=False,plotconfint=False):
    '''Bootstrapping power law distribution'''
    data = np.array(data) # make sure the input is an array
    sample = data[data >= xmin]
    mu,confidence,nPoints = pwlaw_fit_cont(sample,xmin) #fit original power law

    f = 1/(sample/float(xmin))**mu
    ksInit = kstest(sample,f)
    #print ksInit

    if nPoints==0:
        print "no value larger than %s"%xmin
        return

    if numiter == -1:
        numiter = round(1./4*(confint)**-2)

    m = np.zeros([numiter,nPoints])
    i = 0
    k = 0
    while i < numiter:
        q2 = pwlaw(len(sample),xmin,mu)[0]
        m[i]=np.sort(q2)
        ks = kstest(q2,f)

        if ks > ksInit:
            k += 1

        i+=1

    pvalue = k/float(numiter)
    U = np.percentile(m,100-confint*100,0)
    L = np.percentile(m,confint,0)

    if plot:
        x,y = rankorder(data)
        yNorm = y/float(y[-1])
        yMin = yNorm[x <= xmin][0]

        pl.loglog(x,yNorm,'k.')

        xFit = np.logspace(np.log10(xmin),np.log10(max(sample)))
        yFit = yMin*1/(xFit/float(xmin))**mu

        pl.loglog(xFit,yFit,'r-')

        if plotconfint:
            x,y = rankorder(L)
            yLowerNorm = y/float(y[-1])
            pl.loglog(x,yMin*yLowerNorm,'m')
            x,y = rankorder(U)
            yUpperNorm = y/float(y[-1])
            pl.loglog(x,yMin*yUpperNorm,'b')

    return m,L,U,pvalue

def kstest(sample1,sample2):
    return np.max(np.abs(sample1 - sample2))



def countUnique(array):
    return len(set(array))

def rankorder(x):
    x1 = np.sort(x)[::-1]
    y1 = np.arange(1,len(x1)+1)
    return x1,y1

if __name__ == '__main__':
    print "blah"
    #user_events = 'users/%s'%'jakevdp'
    #url = api_url + user_events + "?access_token=%s"%github_token
    #print url
    #test = getPagedRequest(url)

    #for i in range(len(test)):
    #    print test[i]['type'],test[i]['created_at'],test[i]['repo']['name']
