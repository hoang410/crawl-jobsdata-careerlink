from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd
import time
import requests
from sqlalchemy import create_engine

# Connect mySQL
db_user='root'
db_password='Hoang410'
db_host='127.0.0.1'
db_port=3306
db_name='careerlink_data'
table_name='jobs_type'
connection_str=f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine=create_engine(connection_str)

# Load data frame from mySQL
sql_query_jobs_type='SELECT * FROM jobs_type'
df_type_sql=pd.read_sql_query(sql_query_jobs_type,engine)

# Collect job types list, job types link
driver = webdriver.Chrome()
url='https://www.careerlink.vn/vieclam/list'
driver.get(url)
time.sleep(2)
job_types_button=driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[6]')
job_types_button.click()
job_types_list=[]
html=driver.page_source
soup=BeautifulSoup(html,'lxml')
result=soup.find_all('button',class_='dropdown-item cl-select--item')
for job_type in result:
    job_types_list.append(job_type.text)
job_types_link=[]
for time_click in range(0,len(job_types_list)):
    select=time_click+1
    job_types_click_open=driver.find_element(By.XPATH,f'/html/body/div[3]/div/div/div/div[1]/div/div[6]/div/button[{select}]')
    driver.execute_script("arguments[0].click();", job_types_click_open)
    time.sleep(2)
    job_type_link=driver.current_url.replace('?','&').replace('tim-kiem-viec-lam','list?page={}')
    job_types_link.append(job_type_link)
    driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[6]/div/div/button').click()
    time.sleep(2)
driver.close()

# Function count total page with URL
def total_page(url):
    response=requests.get(url)
    html=response.text
    soup_count_page=BeautifulSoup(html,'lxml')
    pagination=soup_count_page.find_all('ul',class_='pagination')
    if pagination==[]:
        total_page=1
    else:
        for i in pagination:
            check_page=i.find('a',class_='page-link d-none d-md-block')
            total_page=int(check_page.parent.find_previous_sibling().text.strip())
    return(total_page)

# Create job types table
types_dict={}
type_jobs_list=[]
type_companies=[]
for type_link in job_types_link:
    type_job_list=[]
    for page in range(1,total_page(type_link.format(1))+1): #total_page(type_link.format(1))
        url_type=type_link.format(page)
        response_type=requests.get(url_type)
        html_type=response_type.text
        soup_type=BeautifulSoup(html_type,'lxml')
        type_job_tag=soup_type.find_all('a',class_='job-link clickable-outside')
        type_company_tag=soup_type.find_all('a',class_='text-dark job-company mb-1 d-inline-block line-clamp-1')
        for job,com in zip(type_job_tag,type_company_tag):
            jobs_title=job.get('title').replace('\n','').strip()
            company=com.text.replace('\n','').strip()
            type_job_list.append(jobs_title)
            type_companies.append(company)
    type_jobs_list.append(type_job_list)
for types, job in zip(job_types_list,type_jobs_list):
    types_dict[types]=job
df_type=pd.DataFrame([(value,key) for key, values in types_dict.items() for value in values],columns=['Jobs_title','Type'])
df_type['Company']=type_companies
df_type=df_type.drop_duplicates(subset=['Jobs_title','Company'])
df_type['Key']=df_type['Jobs_title']+'#'+df_type['Company']
df_type=df_type[['Type','Key']]

# Compare 2 dataframe
df_type_new=df_type[~df_type['Key'].isin(df_type_sql['Key'])]
df_type_sql=pd.concat([df_type_sql,df_type_new],axis=0)
df_type_sql=df_type_sql.drop_duplicates(subset=['Key'])

# Save to mySQL
df_type_sql.to_sql(name=table_name,con=engine,if_exists='replace',index=False)
print('Jobs_type:',df_type_sql.shape)