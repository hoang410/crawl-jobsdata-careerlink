from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from sqlalchemy import create_engine

# Connect mySQL
db_user = 'root'
db_password = 'Hoang410'
db_host = '127.0.0.1'
db_port = 3306
db_name = 'Careerlink_data'
table_name = 'careers'
connection_str = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_str)

# Load data frame from mySQL
sql_query_careers = 'SELECT * FROM careers'
df_careers_sql = pd.read_sql_query(sql_query_careers,engine)

# Collect careers list, careers link
driver = webdriver.Chrome()
url='https://www.careerlink.vn/vieclam/list'
driver.get(url)
time.sleep(2)
careers=driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[1]')
careers.click()
careers_list=[]
html=driver.page_source
soup=BeautifulSoup(html,'lxml')
result=soup.find_all('button',class_='dropdown-item cl-select--item')

#
for career in result:
    careers_list.append(career.text)
careers_link=[]
for time_click in range(0,len(careers_list)):
    select=time_click+1
    career_click_open=driver.find_element(By.XPATH,f'/html/body/div[3]/div/div/div/div[1]/div/div[1]/div/button[{select}]')
    driver.execute_script("arguments[0].click();", career_click_open)
    time.sleep(2)
    career_link=driver.current_url
    careers_link.append(career_link)
    career_click_close=driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[1]/div/div[2]/button').click()
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

# Create Career table
career_dict={}
jobs_list=[]
companies=[]
for career_link in careers_link:
    job_list=[]
    for page in range(1,total_page(career_link)+1):
        url_careers=f'{career_link}?page={page}'
        response_careers=requests.get(url_careers)
        html_careers=response_careers.text
        soup_careers=BeautifulSoup(html_careers,'lxml')
        jobs_tag=soup_careers.find_all('a',class_='job-link clickable-outside')
        companies_tag=soup_careers.find_all('a',class_='text-dark job-company mb-1 d-inline-block line-clamp-1')
        for job,com in zip(jobs_tag,companies_tag):
            jobs_title=job.get('title').replace('\n','').strip()
            company=com.text.replace('\n','').strip()
            companies.append(company)
            job_list.append(jobs_title)
    jobs_list.append(job_list)
for career, job in zip(careers_list,jobs_list):
    career_dict[career]=job

# Save careers into dataframe
df_careers= pd.DataFrame([(value,key) for key, values in career_dict.items() for value in values],columns=['Jobs_title','Career'])
df_careers['Company']=companies
df_careers=df_careers.drop_duplicates(subset=['Jobs_title','Company'])
df_careers['Key']=df_careers['Jobs_title']+'#'+df_careers['Company']
df_careers=df_careers[['Career','Key']]

# Compare 2 dataframe
df_new_careers=df_careers[~df_careers['Key'].isin(df_careers_sql['Key'])]
df_careers_sql=pd.concat([df_careers_sql,df_new_careers],axis=0)
df_careers_sql=df_careers_sql.drop_duplicates(subset=['Key'])

# Save to mySQL
df_careers_sql.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print('Careers: ',df_careers_sql.shape)