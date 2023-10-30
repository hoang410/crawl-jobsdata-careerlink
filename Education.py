from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
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
table_name='education'
connection_str=f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine=create_engine(connection_str)

# Load data frame from mySQL
sql_query_education='SELECT * FROM education'
df_edu_sql=pd.read_sql_query(sql_query_education,engine)

# Collect education level list, education level link
driver = webdriver.Chrome()
url='https://www.careerlink.vn/vieclam/list'
driver.get(url)
time.sleep(2)
education_button=driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[5]')
education_button.click()
education_levels_list=[]
html=driver.page_source
soup=BeautifulSoup(html,'lxml')
result=soup.find_all('button',class_='dropdown-item cl-select--item')
for edu_level in result:
    education_levels_list.append(edu_level.text)
education_levels_link=[]
for time_click in range(0,len(education_levels_list)):
    select=time_click+1
    education_click_open=driver.find_element(By.XPATH,f'/html/body/div[3]/div/div/div/div[1]/div/div[5]/div/button[{select}]')
    driver.execute_script("arguments[0].click();", education_click_open)
    time.sleep(2)
    education_link=driver.current_url.replace('tim-kiem-viec-lam','list')
    education_levels_link.append(education_link)
    driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/div[1]/div/div[5]/div/div/button').click()
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

# Create Education table
educations_dict={}
edu_jobs_list=[]
edu_companies=[]
for edu_link in education_levels_link:
    edu_job_list=[]
    for page in range(1,total_page(edu_link+'&page=1')+1): #total_page(edu_link+'&page=1')
        url_education=f'{edu_link}&page={page}'
        response_edu=requests.get(url_education)
        html_edu=response_edu.text
        soup_edu=BeautifulSoup(html_edu,'lxml')
        edu_job_tag=soup_edu.find_all('a',class_='job-link clickable-outside')
        edu_company_tag=soup_edu.find_all('a',class_='text-dark job-company mb-1 d-inline-block line-clamp-1')
        for job,com in zip(edu_job_tag,edu_company_tag):
            jobs_title=job.get('title').replace('\n','').strip()
            company=com.text.replace('\n','').strip()
            edu_job_list.append(jobs_title)
            edu_companies.append(company)
    edu_jobs_list.append(edu_job_list)
for edu, job in zip(education_levels_list,edu_jobs_list):
    educations_dict[edu]=job
df_edu=pd.DataFrame([(value,key) for key, values in educations_dict.items() for value in values],columns=['Jobs_title','Education'])
df_edu['Company']=edu_companies
df_edu=df_edu.drop_duplicates(subset=['Jobs_title','Company'])
df_edu['Key']=df_edu['Jobs_title']+'#'+df_edu['Company']
df_edu=df_edu[['Education','Key']]

# Compare 2 dataframe
df_edu_new=df_edu[~df_edu['Key'].isin(df_edu_sql['Key'])]
df_edu_sql=pd.concat([df_edu_sql,df_edu_new],axis=0)
df_edu_sql=df_edu_sql.drop_duplicates(subset=['Key'])

# Save to mySQL
df_edu_sql.to_sql(name=table_name,con=engine,if_exists='replace',index=False)
print('Educations:',df_edu_sql.shape)