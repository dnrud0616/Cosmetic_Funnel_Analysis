# -*- coding: utf-8 -*-
"""홍우경_온라인 화장품 Funnel 분석.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wLTlEH5CuPlB3XsTjVielM2nrueS4HGc

**온라인 화장품 Funnel분석**
---
> **목차(Context)**

* 프로젝트 Summary
* 문제상황 Introduction

## **프로젝트 Summary**
---

> **프로젝트명**

```
▶ 온라인 화장품 Funnel분석
```  

> **프로젝트유형**

```
▶ 온라인 화장품 구매이력 데이터 활용 Funnel 분석

```

> **학습목표**

```
▶ 온라인 화장품 구매 과정에서의 사용자 행동 패턴 인식
▶ Funnel 단계별 dropout 지점 및 이유 파악
▶ 효과적인 마케팅 및 개선 전략 제안을 위한 데이터 분석 능력 향상
```

> **예상 결과물**

```
▶ Funnel 분석 리포트 (각 단계별 이탈률, 주요 이탈 원인 등)
▶ 화장품 구매 전환률 개선을 위한 전략 및 제안서
▶ 데이터 시각화 대시보드 (예: Tableau, Power BI 등을 사용한 대시보드)
```

> **데이터 살펴보기**


|Column|Description|
|:---|:---|
|event_time|이벤트가 발생한 시간|
|event_type|이벤트 유형: [view, cart, remove_from_cart, purchase] 중 하나|
|product_id|제품 ID|
|category_id|제품 카테고리 ID|
|category_code|의미 있는 카테고리 이름 (있는 경우)|
|brand|브랜드 이름 (소문자로, 있을 경우)|
|price|제품 가격|
|user_id|영구 사용자 ID|
|user_session|사용자 세션 ID|
"""

# ▶ Warnings 제거
import warnings
warnings.filterwarnings('ignore')

# ▶ Google drive mount or 폴더 클릭 후 구글드라이브 연결
from google.colab import drive
drive.mount('/content/drive')

# ▶ 경로 설정 (※강의자료가 위치에 있는 경로 확인)
import os
os.chdir('/content/drive/MyDrive/DA7/개인프로젝트/제출완료/02(11)화장품(중)')
os.getcwd()

# ▶ Data read
import pandas as pd
df = pd.read_csv('P_PJT11_DATA.csv')
df.head()

"""## **🔈Process01**  
**┗ Data Info Check**  
---

### · Data 전처리  
---
* 수집된 데이터의 기본 정보들을 확인  

  (1) Data shape(형태) 확인

  (2) Data type 확인

  (3) Null값 확인 (※ 빈 값의 Data)

  (4) Outlier 확인 (※ 정상적인 범주를 벗어난 Data)
"""

# ▶ Data 형태 확인
# ▶ 3,533,286 row, 9 col로 구성됨
print('df', df.shape)

# ▶ Data type 확인
df.info()

# ▶ Null 값 확인
print(df.isnull().sum())

# ▶ Null value 다른 값으로 치환
df['category_code'].fillna('None', inplace = True)
df['brand'].fillna('None', inplace = True)
df['user_session'].fillna('None', inplace = True)

# ▶ Outlier 확인
df.describe()

df = df[df['price'] >= 0]

# ▶ object type 이었던 event_time의 형식 변경
df['event_time'] = pd.to_datetime(df['event_time'])
type(df['event_time'][0])

df.info()

"""## **🔈Process02**  
### · 데이터 EDA
---
"""

import pandas as pd
import matplotlib.pyplot as plt

# event_time 컬럼을 datetime 형식으로 변환 (이미 변환되어 있지 않다면)
df['event_time'] = pd.to_datetime(df['event_time'])

# 날짜별 이벤트 발생 빈도 시각화
df['date'] = df['event_time'].dt.date


# 시간대별 이벤트 발생 빈도 시각화
df['hour'] = df['event_time'].dt.hour

import seaborn as sns

# event_type 별로 그룹화한 후 시간대별 빈도 계산
hourly_event_type_count = df.groupby(['hour', 'event_type']).size().unstack()

# Seaborn의 파스텔 색상 팔레트 사용
pastel_palette = sns.color_palette("pastel")

# 시간대별 이벤트 타입 분포 시각화 (파스텔 색상 적용)
hourly_event_type_count.plot(kind='bar', stacked=True, figsize=(12, 6), color=pastel_palette)
plt.title('Event Type By Time Range')
plt.xlabel('Time Range (0~23)')
plt.ylabel('Event Count')
plt.legend(title='event type')
plt.show()

df['price_range'] = pd.cut(df['price'], bins=[0, 1, 5, 10, 20, 50, 100, 200, 350],
                           labels=['0-1', '1-5', '5-10', '10-20', '20-50', '50-100', '100-200', '200-350'])

# 이상치의 개수 계산 (상한/하한을 넘는 값)
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1

outlier_mask = (df['price'] < (Q1 - 1.5 * IQR)) | (df['price'] > (Q3 + 1.5 * IQR))
outliers = df[outlier_mask]

# 이벤트 타입별 이상치 빈도
outliers_event_type_count = outliers['event_type'].value_counts()
print(outliers_event_type_count)

# 이벤트 타입별로 이상치 가격대 분석
sns.boxplot(x='event_type', y='price', data=outliers, palette='pastel')
plt.title('Outlier by Event Type')
plt.show()

# 세션별로 event_type을 그룹화하여 각 이벤트 발생 횟수 계산
session_event_counts = df.groupby(['user_session', 'event_type']).size().unstack(fill_value=0)

# 클릭에서 장바구니 추가로, 장바구니 추가에서 구매로 이어지는 전환율 계산
session_event_counts['view_to_cart'] = session_event_counts['cart'] / session_event_counts['view']
session_event_counts['cart_to_purchase'] = session_event_counts['purchase'] / session_event_counts['cart']

# 전환율이 0인 값은 제거
session_event_counts.replace([float('inf'), 0], 0, inplace=True)

# 평균 전환율 계산
click_to_cart_rate = session_event_counts['view_to_cart'].mean()
cart_to_purchase_rate = session_event_counts['cart_to_purchase'].mean()

# 전환율 시각화
labels = ['view → cart', 'cart → purchase']
conversion_rates = [click_to_cart_rate, cart_to_purchase_rate]

plt.figure(figsize=(8, 6))
plt.bar(labels, conversion_rates, color = pastel_palette)
plt.title('User session conv')
plt.ylabel('conversion')
plt.ylim(0, 1)
plt.show()

"""## **🔈Process03**   
### · 퍼널분석
---

#### 퍼널분석을 위해 생성해야 하는 지표

- dropout : 이벤트 타입에서 타입으로 넘어갈 때의 이탈률을 의미
- funnel stages : 설계된 유저경험 루트
본 보고서에서는 view - cart - purchase의 순서로 설계하였다.
"""

# ▶ 이벤트 타입 횟수
# ▶ 각 이벤트가 발생한 횟수를 count

event_counts = df['event_type'].value_counts()
event_counts

# ▶ 각 단계에서의 이탈률 계산

view_to_cart_dropout = (event_counts['view'] - event_counts['cart']) / event_counts['view'] * 100
cart_to_purchase_dropout = (event_counts['cart'] - event_counts['purchase']) / event_counts['cart'] * 100
cart_to_remove_dropout = (event_counts['remove_from_cart']) / event_counts['cart'] * 100

dropout_rates = {
    'View to Cart Dropout Rate (%)': view_to_cart_dropout,
    'Cart to Purchase Dropout Rate (%)': cart_to_purchase_dropout,
    'Cart to Remove Dropout Rate (%)': cart_to_remove_dropout
}

dropout_rates

# ▶ 상품별 조회, 장바구니 추가, 구매 데이터 계산
product_events = df.groupby(['product_id', 'event_type']).size().unstack().fillna(0)

# ▶ 구매 전환률 계산: 구매수 / 조회수
product_events['conversion_rate'] = product_events['purchase'] / product_events['view'] * 100

# ▶ 상품별 조회수가 10회 이상인 상품들만 필터링하여 전환률 TOP 10 확인
top_conversion_products = product_events[product_events['view'] >= 10].sort_values(by=['view', 'conversion_rate'], ascending=[False, True]).head(10)

top_conversion_products[['view', 'cart', 'purchase', 'conversion_rate']]

# ▶ 각 이벤트 타입별, 유저별 최초 접속 시기 구하기
# ▶ 시간에 대해 최초 접속을 기준으로 하기위해 min 사용

grouped = df.groupby(['event_type', 'user_session'])['event_time'].min()
grouped.head()

# ▶ funnel_stages 정의 후 dataframe화
funnel_stages = pd.DataFrame({'stages' : [1,2,3]}, index = ['view', 'cart', 'purchase'])
funnel_stages

# ▶ 이벤트 타입을 기준으로 funnel stages와 type별 유져, 최초 접속 시간 merge

grouped = pd.DataFrame(grouped).merge(funnel_stages, left_on = 'event_type', right_index=True)
grouped

# ▶피벗테이블 생성

funnel = grouped.reset_index().pivot(index = 'user_session', columns = 'stages', values = 'event_time')
funnel.columns = funnel_stages.index
funnel

# ▶ 각 stage의 개수 count
stage_values = [funnel[column].notnull().sum() for column in funnel.columns]
stage_values

# ▶ funnel 시각화
import plotly.express as px
data = dict (
  number = [794417, 165296, 28894],
  stage = ['View', 'Cart', 'Purchase'])
fig = px.funnel(data, x='number', y='stage')
fig.show()

"""---"""

import plotly.express as px

# 시간대를 추출하여 새로운 열 추가
df['hour'] = df['event_time'].dt.hour


# 시간대 범주 통합 (예: 0~5시, 6~11시, 12~17시, 18~23시)
bins = [0, 6, 12, 18, 24]
labels = ['0-6시', '6-12시', '12-18시', '18-24시']
df['hour_group'] = pd.cut(df['hour'], bins=bins, labels=labels, right=False)

# 시간대 그룹별 이벤트 발생 횟수 집계
time_funnel_data = df.groupby(['hour_group', 'event_type']).size().unstack(fill_value=0)

# 시각화를 위한 데이터 준비
funnel_data = pd.DataFrame({
    'hour_group': time_funnel_data.index,
    'View': time_funnel_data['view'],
    'Cart': time_funnel_data['cart'],
    'Purchase': time_funnel_data['purchase']
})


# 데이터를 melt하여 시각화에 적합한 형태로 변환
funnel_data_melted = pd.melt(funnel_data, id_vars=['hour_group'], value_vars=['View', 'Cart', 'Purchase'], var_name='stage', value_name='number')
# Funnel 차트 시각화
fig = px.funnel(funnel_data_melted, x='number', y='stage', color='hour_group', title="시간대 그룹별 전환 Funnel 분석")
fig.show()

# 가격대 구간 설정 (예: 0-50, 50-100, 100-200, 200-350)
bins = [0, 50, 100, 200, 350]
labels = ['0-50', '50-100', '100-200', '200-350']
df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels)

# 가격대별 이벤트 발생 횟수 집계
price_funnel_data = df.groupby(['price_range', 'event_type']).size().unstack(fill_value=0)

# 시각화를 위한 Funnel 데이터 준비
funnel_data = pd.DataFrame({
    'price_range': price_funnel_data.index,
    'View': price_funnel_data['view'],
    'Cart': price_funnel_data['cart'],
    'Purchase': price_funnel_data['purchase']
})

# 각 가격대별 데이터가 동일한 길이를 유지함을 보장
funnel_data_melted = pd.melt(funnel_data, id_vars=['price_range'], value_vars=['View', 'Cart', 'Purchase'], var_name='stage', value_name='number')

# Funnel 차트 시각화
fig = px.funnel(funnel_data_melted, x='number', y='stage', color='price_range', title="가격대별 전환 Funnel 분석")
fig.show()

"""---"""

# 시간대와 가격대 설정
bins_hour = [0, 6, 12, 18, 24]
labels_hour = ['0-6시', '6-12시', '12-18시', '18-24시']
df['hour_group'] = pd.cut(df['hour'], bins=bins_hour, labels=labels_hour, right=False)

bins_price = [0, 50, 100, 200, 350]
labels_price = ['0-50', '50-100', '100-200', '200-350']
df['price_range'] = pd.cut(df['price'], bins=bins_price, labels=labels_price)

# 이벤트별로 그룹화하여 크기 집계
grouped_price_time = df.groupby(['price_range', 'hour_group', 'event_type']).size().unstack(fill_value=0).reset_index()

# 결과 확인
print(grouped_price_time.head())

# price_range 및 hour_group 열을 object로 변환
grouped_price_time['price_range'] = grouped_price_time['price_range'].astype('object')
grouped_price_time['hour_group'] = grouped_price_time['hour_group'].astype('object')

# 기존 전환율 계산 (가격대 및 시간대별)
grouped_price_time['view_to_cart_rate'] = grouped_price_time['cart'] / grouped_price_time['view']
grouped_price_time['cart_to_purchase_rate'] = grouped_price_time['purchase'] / grouped_price_time['cart']

# NaN 값을 0으로 채우기 (전환율이 없는 경우)
grouped_price_time.fillna(0, inplace=True)

# 기존 전환율 출력
grouped_price_time[['price_range', 'hour_group', 'view_to_cart_rate', 'cart_to_purchase_rate']]

# 전략 도입 후 전환율 가정 (예시로 기존 전환율에서 10% 증가 가정)
grouped_price_time['new_view_to_cart_rate'] = grouped_price_time['view_to_cart_rate'] + 0.10  # 10% 증가 가정
grouped_price_time['new_cart_to_purchase_rate'] = grouped_price_time['cart_to_purchase_rate'] + 0.05  # 5% 증가 가정

# 각 가격대/시간대별 매출 계산 (기존 및 전략 도입 후)
average_purchase_value = 80  # 평균 구매 금액 가정

# 기존 매출 계산
grouped_price_time['original_sales'] = grouped_price_time['purchase'] * average_purchase_value

# 전략 도입 후 매출 계산 (가정된 전환율을 적용한 매출)
grouped_price_time['new_cart'] = grouped_price_time['view'] * grouped_price_time['new_view_to_cart_rate']
grouped_price_time['new_purchase'] = grouped_price_time['new_cart'] * grouped_price_time['new_cart_to_purchase_rate']
grouped_price_time['new_sales'] = grouped_price_time['new_purchase'] * average_purchase_value

# 결과 확인
grouped_price_time[['price_range', 'hour_group', 'original_sales', 'new_sales']]

import matplotlib.pyplot as plt

# 가격대별로 기존 매출과 새로운 매출을 비교
price_categories = grouped_price_time['price_range'].unique()

# 기존 매출과 새로운 매출의 합계 계산
original_sales = grouped_price_time.groupby('price_range')['original_sales'].sum()
new_sales = grouped_price_time.groupby('price_range')['new_sales'].sum()

import matplotlib.pyplot as plt

# 가격대별로 기존 매출과 새로운 매출의 합계 계산
grouped_by_price = grouped_price_time.groupby('price_range').agg({
    'original_sales': 'sum',
    'new_sales': 'sum'
}).reset_index()

# 가격대 50-100만 필터링
filtered_price = grouped_by_price[grouped_by_price['price_range'] == '50-100']

# 기존 매출과 새로운 매출
original_sales_price = filtered_price['original_sales']
new_sales_price = filtered_price['new_sales']
categories_price = filtered_price['price_range']

# 시각화
fig, ax = plt.subplots(figsize=(6, 4))
bar_width = 0.35
index = range(len(categories_price))

# 막대 그래프 그리기
bar1 = plt.bar(index, original_sales_price, bar_width, label='Original Sales_price', color='#ADD8E6')  # 하늘색
bar2 = plt.bar([i + bar_width for i in index], new_sales_price, bar_width, label='New_Sales_price', color='#FFB6C1')  # 핑크색

plt.xlabel('Price Range')
plt.ylabel('Sales')
plt.title('50-100 Sales Differences')
plt.xticks([i + bar_width / 2 for i in index], categories_price)
plt.legend()


# 막대 위에 매출 값 표시
for i, v in enumerate(original_sales_price):
    plt.text(i - 0.1, v + 1000, f"${v:.0f}", color='#4682B4', fontweight='bold')  # 하늘색 텍스트
for i, v in enumerate(new_sales_price):
    plt.text(i + bar_width - 0.1, v + 1000, f"${v:.0f}", color='#FF69B4', fontweight='bold')  # 핑크 텍스트


plt.show()

# 시간대별로 기존 매출과 새로운 매출의 합계 계산

grouped_by_time = grouped_price_time.groupby('hour_group').agg({
    'original_sales': 'sum',
    'new_sales': 'sum'
}).reset_index()

# 시간대 6-12시 및 12-18시만 필터링
filtered_time = grouped_by_time[grouped_by_time['hour_group'].isin(['6-12시', '12-18시'])]

# 기존 매출과 새로운 매출
original_sales_time = filtered_time['original_sales']
new_sales_time = filtered_time['new_sales']
categories_time = filtered_time['hour_group']

# 시각화
fig, ax = plt.subplots(figsize=(8, 5))
bar_width = 0.35
index = range(len(categories_time))

# 막대 그래프 그리기
bar1 = plt.bar(index, original_sales_time, bar_width, label='Original_Sales_time', color='#ADD8E6')  # 하늘색
bar2 = plt.bar([i + bar_width for i in index], new_sales_time, bar_width, label='New_Sales_time', color='#FFB6C1')  # 핑크색

plt.xlabel('Time Range')
plt.ylabel('Sales')
plt.title('6-12 / 12-18 Sales Difference')
plt.xticks([i + bar_width / 2 for i in index], categories_time)
plt.legend()

# 막대 위에 매출 값 표시
for i, v in enumerate(original_sales_time):
    plt.text(i - 0.1, v + 1000, f"${v:.0f}", color='#4682B4', fontweight='bold')  # 하늘색 텍스트
for i, v in enumerate(new_sales_time):
    plt.text(i + bar_width - 0.1, v + 1000, f"${v:.0f}", color='#FF69B4', fontweight='bold')  # 핑크 텍스트


plt.show()

"""---"""