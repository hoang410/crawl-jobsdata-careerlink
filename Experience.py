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
table_name='experiences'
connection_str=f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine=create_engine(connection_str)

# Load data frame from mySQL
sql_query_experiences='SELECT * FROM experiences'
df_exp_sql=pd.read_sql_query(sql_query_experiences,engine)

# Collect experiences list, experience links
driver = webdriver.Chrome()
url='https://www.careerlink.vn/vieclam/list'
driver.get(url)
time.sleep(5)
experiences=driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[3]')
experiences.click()
experiences_list=[]
html=driver.page_source
soup=BeautifulSoup(html,'lxml')
result=soup.find_all('button',class_='dropdown-item cl-select--item')
for ex_grade in result:
    experiences_list.append(ex_grade.text)
experiences_link=[]
for time_click in range(0,len(experiences_list)):
    select=time_click+1
    experience_click_open=driver.find_element(By.XPATH,f'/html/body/div[3]/div/div/div/div[1]/div/div[3]/div/button[{select}]')
    driver.execute_script("arguments[0].click();", experience_click_open)
    time.sleep(2)
    experience_link=driver.current_url.replace('tim-kiem-viec-lam','list')
    experiences_link.append(experience_link)
    driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[3]/div/div/button').click()
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

# Create Experience table
experiences_dict={}
exp_jobs_list=[]
exp_companies=[]
for experience_link in experiences_link:
    exp_job_list=[]
    for page in range(1,total_page(experience_link+'&page=1')+1):#total_page(experience_link+'&page=1')
        url_experiences=f'{experience_link}&page={page}'
        response_exp=requests.get(url_experiences)
        html_exp=response_exp.text
        soup_exp=BeautifulSoup(html_exp,'lxml')
        exp_job_tag=soup_exp.find_all('a',class_='job-link clickable-outside')
        exp_company_tag=soup_exp.find_all('a',class_='text-dark job-company mb-1 d-inline-block line-clamp-1')
        for job,com in zip(exp_job_tag,exp_company_tag):
            jobs_title=job.get('title').replace('\n','').strip()
            company=com.text.replace('\n','').strip()
            exp_job_list.append(jobs_title)
            exp_companies.append(company)
    exp_jobs_list.append(exp_job_list)
for exp, job in zip(experiences_list,exp_jobs_list):
    experiences_dict[exp]=job
df_exp=pd.DataFrame([(value,key) for key, values in experiences_dict.items() for value in values],columns=['Jobs_title','Experience'])
df_exp['Company']=exp_companies
df_exp=df_exp.drop_duplicates(subset=['Jobs_title','Company'])
df_exp['Key']=df_exp['Jobs_title']+'#'+df_exp['Company']
df_exp=df_exp[['Experience','Key']]

# Compare 2 dataframe
df_new_exp=df_exp[~df_exp['Key'].isin(df_exp_sql['Key'])]
df_exp_sql=pd.concat([df_exp_sql,df_new_exp],axis=0)
df_exp_sql=df_exp_sql.drop_duplicates(subset=['Key'])

# Save to mySQL
df_exp_sql.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print('Experiences:',df_exp_sql.shape)