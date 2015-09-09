import numpy as np
import pylab as pl
import json
import pandas
import scipy.stats as S
from datetime import datetime
import sys

sys.path.append("/home/ubuntu/finlib_bin/modules/pymodules/")
import finlib.statistics.pwlaw as pwlaw

sys.path.append("/home/ubuntu/github/AstroWeekStudy/python_code/")

try:
    reload(astroWeekLib)
except:
    import astroWeekLib

from astroWeekLib import *

dir = "/home/ubuntu/github/AstroWeekStudy/python_code/data/"

repos = ["https://github.com/AstroHackWeek",
         "https://github.com/bareid/xi",
         "https://github.com/BIDS/xi",
         "https://github.com/gully/HETDEXtoy",
         "https://github.com/drphilmarshall/Bananas",
         "https://github.com/karenyyng/clustering",
         "https://github.com/dfm/george/",
         "https://github.com/jonathansick/sedbot/",
         "https://github.com/yoachim/HackWeek2014",
         "https://github.com/kbarbary/nestle",
         "https://github.com/jradavenport/FlareTests_AstroHackWeek",
         "https://github.com/adrn/macro-cell",
         "https://github.com/dhuppenkothen/ClassicalStatsPython",
         "https://github.com/jradavenport/cubehelix",
         "https://github.com/LSST-nonproject/sims_maf_contrib",
         "https://github.com/sofiatti/colormag_sncosmo",
         "https://github.com/patti/FHD_PyPE","https://github.com/dfm/kpsf"]


repo_created_during_astroweek = ["https://github.com/dhuppenkothen/BayesPSD",
                                 "https://github.com/dhuppenkothen/UTools",
                                 "https://github.com/nhuntwalker/data_science",
                                 "https://github.com/nhuntwalker/datahack_projects",
                                 "https://github.com/yoachim/HackWeek2014",
                                 "https://github.com/Waelthus/X-Ray-Time-Series",
                                 "https://github.com/adrn/tilt-shift",
                                 "https://github.com/adrn/blind-dating",
                                 "https://github.com/jakevdp/BombScargle",
                                 "https://github.com/jakevdp/noisyLS",
                                 "https://github.com/gully/HETDEXtoy",
                                 "https://github.com/BIDS/xi",
                                 "https://github.com/jmankin/test",
                                 "https://github.com/fperez/test",
                                 "https://github.com/wilmatrick/test",
                                 "https://github.com/RuthAngus/BlackHoleGP",
                                 "https://github.com/alex-parker/ADR4Movie",
                                 "https://github.com/jradavenport/FlareTests_AstroHackWeek",
                                 "https://github.com/rbiswas4/interactivesncosmo",
                                 "https://github.com/drphilmarshall/Bananas",
                                 "https://github.com/Waelthus/RTFig",
                                 "https://github.com/adrn/macro-cell",
                                 "https://github.com/dhuppenkothen/ClassicalStatsPython",
                                 "https://github.com/RuthAngus/nestle",
                                 "https://github.com/sofiatti/SNClassification",
                                 "https://github.com/ogtelford/SNClassification",
                                 "https://github.com/jradavenport/random-forest-timeseries",
                                 "https://github.com/sofiatti/sncosmo",
                                 "https://github.com/drphilmarshall/AstroData",
                                 "https://github.com/karenyyng/Bananas",
                                 "https://github.com/adrn/Gaia-zero-day-exploit",
                                 "https://github.com/drphilmarshall/SciAmBlogPost",
                                 "https://github.com/bareid/xi",
                                 "https://github.com/AstroHackWeek/astrohackweek.github.io",
                                 "https://github.com/AstroHackWeek/website_source",
                                 "https://github.com/brittafiore/DataScience",
                                 "https://github.com/Waelthus/astroMLfigs",
                                 "https://github.com/sofiatti/colormag_sncosmo"]


'''Configuring plot for nice display'''
fig_width_pt = 420.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0 / 72.27  # Convert pt to inch
golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
fig_width = fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width  # *golden_mean      # height in inches
fig_size = [fig_width, fig_height]

params = {'backend': 'ps',
          'axes.labelsize': 22,
          'text.fontsize': 28,
          'legend.fontsize': 12,
          'xtick.labelsize': 18,
          'ytick.labelsize': 18,
          'text.usetex': False,
          'figure.figsize': fig_size}
pl.rcParams.update(params)



'''Some useful time boundaries'''
time_boundaries = ['2014-05-31 00:00:00','2015-04-15 00:00:00']
timestamp_boundaries = [datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") for dt in time_boundaries]
astroweek = ['2014-09-15 00:00:00','2014-09-20 00:00:00']
timestamp_astroweek = [datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") for dt in astroweek]

arbitrary_tBoundaries = ['2014-04-15 00:00:00','2015-02-20 00:00:00']
timestamp_atB = [datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") for dt in arbitrary_tBoundaries]



def countUnique(array):
    return len(set(array))


def build_main_df(sampling_resol="1D"):
    '''
    Main DataFrame (df): 
    This pandas dataframe contains all timestamped events related to users 
    identified as having taken part to AstroWeek 2014. Repositories related 
    to events are also provided
    '''
    
    
    #Parse .csv files and create a timestamp column to merge 2014 and 2015 datasets
    df2014 = pandas.io.parsers.read_csv(dir+"events_2014_2.csv")
    df2014['timestamp'] = np.array([datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") for dt in df2014['created_at']])
    
    df2014.rename(columns={'actor_attributes_login':'actor'}, inplace=True)
    df2014.rename(columns={'repository_name':'repo'}, inplace=True)
    df2014.rename(columns={'repository_url':'repo_url'}, inplace=True)
    df2014.rename(columns={'repository_created_at':'repo_created_at'}, inplace=True)
    
    df2015 = pandas.io.parsers.read_csv(dir+"events_2015_2.csv")
    df2015['timestamp'] = map(datetime.fromtimestamp,df2015['created_at'])
    
    df2015.rename(columns={'actor_login':'actor'}, inplace=True)
    df2015.rename(columns={'repo_name':'repo'}, inplace=True)
    
    df = pandas.concat([df2014,df2015])
    
    df.index = df['timestamp']
    
    df2014['repo_created_at'] = np.array([datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") for dt in df2014['repo_created_at']])
    
    t_resol = sampling_resol
    
    event_types = np.unique(df.type.values)
    event_dic = {}
    event_dic['all'] = df.type.resample(t_resol,how='count')
    event_count = df.type.resample(t_resol,how='count')
    
    for e in event_types:
        event_dic[e] = df[df['type']==e].type.resample(t_resol,how='count')
    
        if len(event_dic[e]) < len(event_count):
            event_dic[e] = fill_ommitted_resample(event_dic[e],event_count)
        
        #print e,len(event_dic[e])
    
    
    resampled = {"activity" : 
                    {'events' : event_count,
                     'actors' : df.actor.resample(t_resol,how=countUnique),
                     'repos' : df.repo.resample(t_resol,how=countUnique)
                     },
                 'event_types' : event_dic
                }


    return df,df2014,df2015,resampled

def fill_ommitted_resample(df,ref_df):
    
    i=0
    while ref_df.index[i] < df.index[0]:
        #print i , ref_df.index[i],df.index[0] , ref_df.index[i] < df.index[0]
        df = df.set_value(ref_df.index[i], 0)
        i+=1
    
    df = df.sort_index()


    i=-1
    while ref_df.index[i] > df.index[i]:
        #print i,ref_df.index[-i] > df.index[-1]
        df = df.set_value(ref_df.index[i], 0)
        i-=1
    
    df = df.sort_index()
    
    return df
    
    



def build_df_repos_created(df2014):
    '''DataFrame to handle creation dates of repos in df'''
    voila = df2014[['repo_created_at','repo_url']]
    voila.sort(columns=["repo_created_at"],inplace=True)
    repo_date = np.array(zip(*voila.values)[0])
    repo_url = np.array(zip(*voila.values)[1])
    u_repo_url = np.unique(repo_url)
    
    u_created_at = []
    for r in u_repo_url:
        index = np.argwhere(r==repo_url)[0]
        u_created_at.append(repo_date[index][0])
        
    df_repos_created = pandas.DataFrame(data={'repo_url':u_repo_url,'repo_created_at' :u_created_at},index=u_created_at)
    
    return df_repos_created



'''Routines to build DataFrames'''
def prepareUserDf(df):
    dicCreatedAt = json.loads(open(dir + "dicCreatedAt.json",'rb').read())
    user_dic = {}
    for u in dicCreatedAt.keys():
        #print u,dicCreatedAt[u],len(df[(df['actor']==u) & (df['timestamp'] < timestamp_astroweek[0])])    
        user_dic[u] = {"created_at" : datetime.strptime(dicCreatedAt[u],"%Y-%m-%dT%H:%M:%SZ"),
                       "event_count_before" : len(df[(df['actor']==u) & (df['timestamp'] > timestamp_atB[0]) & (df['timestamp'] < timestamp_astroweek[0])]),
                       "event_count_during" : len(df[(df['actor']==u) & (df['timestamp'] >= timestamp_astroweek[0]) & (df['timestamp'] < timestamp_astroweek[1])]),
                       "event_count_after" : len(df[(df['actor']==u) & (df['timestamp'] >= timestamp_astroweek[1]) & (df['timestamp'] < timestamp_atB[1])])
                       }    
    
    user_df = pandas.DataFrame.from_dict(user_dic,orient='index').sort(columns=["event_count_before"],ascending=False)
    return user_df


def PrepareRepoDf(df):
    u_repo_url = np.unique(df.repo_url.values)
    repo_dic = {}
    for repo_url in u_repo_url[:]:
        #print repo_url
        created_at = df[df['repo_url']==repo_url]['repo_created_at'][0]
        event_count = len(df[df['repo_url']==repo_url])
        user_count = len(np.unique(df[df['repo_url']==repo_url]['actor'].values))
        type_freq = dict(zip(*np.unique(df[df['repo_url']==repo_url]['type'].values, return_counts=True)))
        repo_dic[repo_url] = {"event_count": event_count, "user_count" : user_count,'created_at':created_at,'type_freq':type_freq}

    return repo_dic


def exportTables(df):
    '''This function is a copy paste from notebook. I have not tested yet, since I don't need it for now'''
    dfAstroWeek = df[(df['timestamp'] >= timestamp_astroweek[0]) & (df['timestamp'] < timestamp_astroweek[1])]
    
    '''Count Events per Repo (from Jan. 2014 until and Apr. 2015  & during AstroWeek)'''
    # Jan. 2014 - Apr. 2015
    groupCols = ["repo","repo_url","repo_created_at"]
    path = "exports/count_events_per_repo_all.csv"
    df.groupby(groupCols).count().sort(column='type',ascending=False).to_csv(dir + path)
    # During AstroWeek
    path = "exports/count_events_per_repo_astroweek.csv"
    dfAstroWeek.groupby(groupCols).count().sort(column='type',ascending=False).to_csv(dir + path)
    # Both tables were exported to Google Drive for manual coding
    
    '''Count Events by Type (from Jan. 2014 until and Apr. 2015  & during AstroWeek)'''
    # Jan. 2014 - Apr. 2015
    df.groupby(["type"]).count().sort(column='type',ascending=False).to_csv(dir + "exports/count_events_by_type_all.csv")
    # During AstroWeek
    dfAstroWeek.groupby(["type"]).count().sort(column='type',ascending=False).to_csv(dir + "exports/count_events_by_type_astroweek.csv")
    # Both tables were exported to Google Drive for manual coding
    
    '''Count Events by Actor and Type (from Jan. 2014 until and Apr. 2015  & during AstroWeek)'''
    # Jan. 2014 - Apr. 2015
    df.groupby(["actor","type"]).count().sort(column='type',ascending=False).to_csv(dir + "exports/count_events_by_actor_and_type_all.csv")
    # During AstroWeek
    dfAstroWeek.groupby(["actor","type"]).count().sort(column='type',ascending=False).to_csv(dir + "exports/count_events_by_actor_and_type_astroweek.csv")
    # Both tables were exported to Google Drive for manual coding   
    
    '''Count Events by Actor, Repo, and Type (from Jan. 2014 until and Apr. 2015  & during AstroWeek)'''
    # Jan. 2014 - Apr. 2015
    groupCols = ["actor","repo","type","repo_url","repo_created_at"]
    path = "exports/count_events_by_actor_repo_and_type_all.csv"
    df.groupby(groupCols).count().sort(column='type',ascending=False).to_csv(dir + path)
    # During AstroWeek
    path = "exports/count_events_by_actor_repo_and_type_astroweek.csv"
    dfAstroWeek.groupby(groupCols).count().sort(column='type',ascending=False).to_csv(dir + path)
    # Both tables were exported to Google Drive for manual coding
    
