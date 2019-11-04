import json, os, requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np

os.chdir('/Users/adroesch/Desktop/private/hvorvor')
sources = json.load(open('projects/hvor_mye_warmere/data/sources_mean_air_p1y_clean.json','r'))

d=[]
p = pd.DataFrame(columns=['source','year','mean_temp'])
# k,v = list(sources.items())[2]
for k,v in sources.items():
    params={
        'sources':k,
        'elements': 'mean(air_temperature P1Y)',
        'referencetime':'1900-01-01T00:00:00Z/2019-01-01T00:00:00Z'
    }
    r = requests.get('https://frost.met.no/observations/v0.jsonld', params,
            auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
    )
    responseData = r.json()['data']
    responseDF = pd.DataFrame([
        {
            'year': int(i['referenceTime'][:4]),
            'source': k,
            'mean_temp':i['observations'][0]['value']
        } for i in responseData
    ])
    d = d + responseData
    p = p.append(responseDF,sort=False)

json.dump(d,open('projects/hvor_mye_warmere/data/cache/all_mean_temp.json','w'))
p.to_csv('projects/hvor_mye_warmere/data/cache/all_mean_temp.csv',index=False)

# inspect
p = pd.read_csv('projects/hvor_mye_warmere/data/cache/all_mean_temp.csv')
p = p.loc[~p[['source','year']].duplicated()]
p = p.sort_values(['source','year'])
p['year_rank']= p.groupby('source')['year'].rank().astype(int)
p['lastyear_rank'] = p['year_rank']-1
p.loc[p.lastyear_rank==0,'lastyear_rank']=np.nan
p.head(100)
p = pd.merge(p,p[['year_rank','source','year']],
    left_on=['source','lastyear_rank'],
    right_on=['source','year_rank'],how='outer')
p = p.rename(columns={'year_x':'year','year_y':'lastyear'})
p = p.drop(['year_rank_y'],axis=1)
p['yeargap'] = p['year']-p['lastyear']
p['mean_temp_rol10y'] = p.groupby('source').rolling(10)['mean_temp'].mean().reset_index(drop=True)
p['yeargap'].value_counts()
p.to_csv('projects/hvor_mye_warmere/data/cache/all_mean_temp_clean.csv')
p2 = p.groupby('source').agg({'yeargap':'max','year':['min','max']})
p2.to_csv('projects/hvor_mye_warmere/data/cache/mean_sources_quality.csv')
p3 = p2.loc[(p2['year']['max']>=2017) & (p2['yeargap']['max']<4)]

sources2 = {k:v for k,v in sources.items() if k in p3.index.values}
json.dump(sources2,open('projects/hvor_mye_warmere/data/sources_mean_air_p1y_clean_b.json','w'))
# from plotnine import *
# (ggplot(p.loc[p.source.isin(p3.index)],aes(
#     x='year',
#     y='mean_temp_rol10y',
#     color='source'
# ))+geom_line()+theme(legend_position='none'))
