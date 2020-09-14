
#card
'''
변수설명
- receipt_dttm : 날짜(yyyymmdd, 20200101 - 20200614)
- adstrd_code : 동네코드
- adstrd_nm : 동네명
- mrhst_induty_cl_code : 업종코드
- mrhst_induty_cl_nm : 업종명
- selng_cascnt : 판매수
- salamt : 판매가격

1. 날짜변경
2. 동 -> 구로 바꾸는 거 연구
3. 업종명 빈칸 없애기
4. 판매가격보다 갯수로 비교하는게 일단 좋을 듯
5. 업종코드 맨 앞 숫자에 따라 카테고리화 가능 할 듯
'''

import os
os.chdir("D:/DATA/covid")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager, style

import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


card =  pd.read_csv("card.csv")#, usecols=(['receipt_dttm','adstrd_code','mrhst_induty_cl_nm','selng_cascnt']))
adstrd = pd.read_csv('adstrd_master.csv')


#card.isnull().sum()
#card.describe().T
#card.info()


#구 맞추기...
adstrd['adstrd_code'] = adstrd['adstrd_code'].apply(lambda x : str(x)[0:6]).astype('int')
adstrd.drop(['adstrd_nm','brtc_nm'],axis=1,inplace=True)
card['adstrd_code'] = card['adstrd_code'].apply(lambda x : str(x)[0:6]).astype('int')
card = card.merge(adstrd, how='left', on='adstrd_code').drop(columns='adstrd_code')
card.drop(['adstrd_nm'],axis=1,inplace=True)


#주차별 분류
card['receipt_dttm'] = pd.to_datetime(card['receipt_dttm'], format = '%Y%m%d')
card['week'] = card['receipt_dttm'].dt.weekofyear


#데이터 이상한거 없애기    
b = card[card['selng_cascnt']=='석재'].index.tolist() + \
    card[card['selng_cascnt']=='커텐'].index.tolist() + \
        card[card['selng_cascnt']=='영상물'].index.tolist() + \
            card[card['selng_cascnt']=='복지매장'].index.tolist() + \
                card[card['selng_cascnt']=='축협직영매장'].index.tolist()    
card.drop(b,axis=0,inplace=True)
card = card.reset_index().drop(['index'],axis=1)


card['selng_cascnt'] = card['selng_cascnt'].apply(lambda x : int(x))
card['salamt'] = card['salamt'].apply(lambda x : int(x))

#
#card.info()


#마이너는 0으로
def minus(x):
    if x < 0:
        return 0
    else:
        return x
    
card['selng_cascnt'] = card['selng_cascnt'].apply(lambda x : minus(x))    


#업종명 빈칸 없애기
card['mrhst_induty_cl_nm'] = card['mrhst_induty_cl_nm'].apply(lambda x : x.replace(" ",""))
	

#업종 중분류
#mrhst_induty_cl_code 앞 두자리 
card['induty'] = card['mrhst_induty_cl_code'].apply(lambda x: str(x)[0:2]).astype('int')


induty_dict ={10 : '숙박',11 : '교통', 20 : '용품',21 : '장소' ,22 : '취미기타'
,30 : '가구',31 : '가전제품',32 : '주방용품'
,33 : '연료',34 : '광품',40 : '유통업',41 : '매점',42 : '의류',43 : '직물',44 : '잡화'
,50 : '교육자재',51 : '교육기관',52 : '기타사무용품',60 : '자동차',61 : '차량서비스',62 : '보험'
,70 : '병원',71 : '대인서비스',80 : '식당분류',81 : '유흥주점',82 : '단란주점',83 : '기타'
,84 : '건강식',90 : '건축',91 : '통신',92 : '수리',93 : '회원제업종',95 : '통신판매'
,96 : '농업기타',99 : '기타'
}


card.head()
card['mrhst_induty_cl_code']
card['mrhst_induty_cl_nm']

a = card.groupby('mrhst_induty_cl_code')['mrhst_induty_cl_nm']



card['induty'] = card['induty'].apply(lambda x: induty_dict[x])


#모든 주차 기록이 없는 산업 삭제
def del_induty(df):
    answer = []
    for i in range(1,25):
        answer.append(i)
        
    delist = []
    for ind in df['induty'].unique().tolist():
        df2 = df[df['induty']==ind]
        if answer != df2.week.unique().tolist():
            delist.append(ind)
    didx = []
    for dl in delist:
        didx += df[df['induty']==dl].index.tolist()
        
    return df.drop(didx,axis=0)
    
card = del_induty(card)




def plot_card(df, ind):
  df = df.copy()  
  df = df.groupby(['induty','mrhst_induty_cl_code','week'])['selng_cascnt'].mean().reset_index()
  df = df[df.induty==ind]
  df['week'] = df['week'].apply(lambda x : '{0}주차'.format(x))

  plt.figure(figsize=(18, 6))
  pal = sns.color_palette("Greens_d", len(df))
  rank = df['selng_cascnt'].argsort().argsort()
  sns.barplot(x='week', y='selng_cascnt', data=df, palette=np.array(pal[::-1])[rank])
  
  plt.title('{0} 평균 판매수'.format(ind), size=20)
  plt.xticks(rotation=45, size=15, ha='right')
  plt.xlabel('주차별', size=15)
  plt.ylabel('판매수', size=15)
  plt.show()


for i in card['induty'].unique().tolist():
    
    plot_card(card,i)



#card_pivot[card_pivot['induty']=='가구'].groupby(['week','mrhst_induty_cl_code'])['selng_cascnt'].sum().reset_index()
  

def plot_card_ind(df, ind_m):
  df = df.copy()  
  
  df = df[df['induty']==ind_m].groupby(['week','mrhst_induty_cl_code'])['selng_cascnt'].sum().reset_index()
  for ind in df['mrhst_induty_cl_code'].unique().tolist():
      temp = df.loc[:,ind]
  
      plt.figure(figsize=(18, 6))
      #pal = sns.color_palette("Greens_d", len(df))
      #rank = temp['selng_cascnt'].argsort().argsort()
      sns.barplot(x='week', y='selng_cascnt', data=temp)#, palette=np.array(pal[::-1])[rank])
    
      plt.title('{0} 평균 판매수'.format, size=20)
      plt.xticks(rotation=45, size=15, ha='right')
      plt.xlabel('주차별', size=15)
      plt.ylabel('판매수', size=15)
      plt.show()





# 서울시 자치구별 유동인구 데이터

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import font_manager, rc, pyplot, style

# 한글폰트
font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/SCDream3.otf").get_name()
rc('font', family=font_name)
style.use('ggplot')

adstrd = pd.read_csv('adstrd_master.csv')
fpopl = pd.read_csv('fpopl.csv', usecols=['base_ymd', 'adstrd_code', 'popltn_cascnt'])


fpopl['base_ymd'] = pd.to_datetime(fpopl['base_ymd'], format='%Y%m%d')
fpopl = fpopl.merge(adstrd, how='left', on='adstrd_code').drop(columns='adstrd_code')
fpopl['week'] =fpopl['base_ymd'].dt.weekofyear

#서울 전체 주차별 유동인구 평균 변화

fpopl_seoul = fpopl.groupby('week')['popltn_cascnt'].sum().reset_index()
fpopl_seoul['week'] = fpopl_seoul['week'].apply(lambda x : '{0}주차'.format(x))


plt.figure(figsize=(18, 6))
pal = sns.color_palette("Greens_d", len(fpopl_seoul))
rank = fpopl_seoul['popltn_cascnt'].argsort().argsort()
sns.barplot(x='week', y='popltn_cascnt', data=fpopl_seoul,palette=np.array(pal)[::-1][rank])
plt.title('평균 유동인구', size=20)
plt.xticks(rotation=45, size=15, ha='right')
plt.xlabel('주차별', size=15)
plt.ylabel('유동인구수', size=15)
plt.show()


def plot_fpopl(df, region):
  
  df = df.copy()  
  df = df[df.signgu_nm==region]
  df['week'] = df['week'].apply(lambda x : '{0}주차'.format(x))

  plt.figure(figsize=(18, 6))
  pal = sns.color_palette("Greens_d", len(df))
  rank = df['popltn_cascnt'].argsort().argsort()
  sns.barplot(x='week', y='popltn_cascnt', data=df, palette=np.array(pal[::-1])[rank])
  
  plt.title('{0} 평균 유동인구'.format(region), size=20)
  plt.xticks(rotation=45, size=15, ha='right')
  plt.xlabel('주차별', size=15)
  plt.ylabel('유동인구수', size=15)
  plt.show()



for i in fpopl['signgu_nm'].unique().tolist():
    plot_fpopl(fpopl,i)


#코로나 직후 유동인구가 많이 줄어든 구 확인
#구마다 인구가 다르기 때문에 단순 차이가 아닌 직전



#서울시 구별 인구수
popl_dict = {"종로구" : 150383,
"중구":126092,
"용산구":229431,
"성동구":297397,
"광진구":349574,
"동대문구":345593,
"중랑구":394414,
"성북구":441812,
"강북구":311773,
"도봉구":329560,
"노원구":528887,
"은평구":479524,
"서대문구":312720,
"마포구":374390,
"양천구":457953,
"강서구":586936,
"구로구":405075,
"금천구":232250,
"영등포구":373349,
"동작구":395165,
"관악구":499740,
"서초구":428919,
"강남구":541233,
"송파구":671512,
"강동구":457164
            }
np.log()
popl_dict.values()
    
def localdiff(df,region):
    df = df.copy()
    df = df[df.signgu_nm==region]
    
    before = (df[(df.week==6)]['popltn_cascnt'].mean() + df[(df.week==7)]['popltn_cascnt'].mean() + df[(df.week==8)]['popltn_cascnt'].mean())/3
    after = (df[(df.week==9)]['popltn_cascnt'].mean() + df[(df.week==10)]['popltn_cascnt'].mean() + df[(df.week==11)]['popltn_cascnt'].mean())/3
    
    diff = (before - after) / popl_dict[region]
    
    return diff

localdiff(fpopl,'종로구')


def locadiff_folium(df):
    df = df.copy()
    r = []
    d = []
    
    for i in df.signgu_nm.unique().tolist():
        d.append(localdiff(df,i))
        r.append(i)
    a = pd.DataFrame(data=None,index=range(len(d)))
    a['adstrd'] = r
    a['diff'] = d

    
    #지도 찍어보기
    # json파일 로딩
    import json
    geo_path = 'seoul_municipalities_geo.json'
    geo_str = json.load(open(geo_path, encoding='utf-8'))


    import folium
    m = folium.Map(location=[37.562225, 126.978555], tiles="OpenStreetMap", zoom_start=11)

    m.choropleth(
        geo_data=geo_str,
        name='유동인구 변화율',
        data=a,
        columns=['adstrd', 'diff'],
        key_on='feature.properties.SIG_KOR_NM',
        fill_color='PuRd', #puRd, YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.3,
        color = 'gray',
        legend_name = '유동변화율'
        )


    m.save('kr_incode.html')








