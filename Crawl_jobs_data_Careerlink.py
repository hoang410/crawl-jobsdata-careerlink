from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

# Connect mySQL
db_user = 'root'
db_password = 'Hoang410'
db_host = '127.0.0.1'
db_port = 3306
db_name = 'Careerlink_data'
table_name = 'jobs_data'
connection_str = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_str)

# Load dataframe from mySQL
sql_query_jobs_data = 'SELECT * FROM jobs_data'
df_jobs_sql = pd.read_sql_query(sql_query_jobs_data,engine)

# Counting total page
url_page1 = 'https://www.careerlink.vn/vieclam/list'
reponse_count = requests.get(url_page1)
html_count = reponse_count.text
soup_count = BeautifulSoup(html_count,'lxml')
pages_total = soup_count.find_all('a',class_='page-link')
total_page = int(pages_total[4].text)
print(total_page)

# Create jobs dataframe, request jobs information
df_jobs = pd.DataFrame(columns=['Jobs_title','Company','City','Salary','Position','Update_time','Key'])
jobs_title, job_companies, job_cities, job_salaries, update_times, jobs_position = [], [], [], [], [], []
for number in range(1,total_page+1):
    url=f'https://www.careerlink.vn/vieclam/list?page={number}'
    reponse=requests.get(url)
    if reponse.status_code == 200:
        print(f'Successfully to request page {number}')
    else:
        print(f'Error to request page {number}')
        pass
    html=reponse.text
    soup=BeautifulSoup(html,'lxml')
    #Listing
    jobs_title_tag=soup.find_all('a',class_='job-link clickable-outside')
    companies_tag=soup.find_all('a',class_='text-dark job-company mb-1 d-inline-block line-clamp-1')
    cities_tag=soup.find_all('a',class_='text-reset')
    salaries_tag=soup.find_all('span',class_='job-salary text-primary d-flex align-items-center')
    positions_tag=soup.find_all('a',class_='job-position text-secondary d-none d-lg-block')
    update_time_tag = soup.find_all('span',class_='cl-datetime')
    for jobs,companies,cities,salaries,positions,times in zip(jobs_title_tag,companies_tag,cities_tag,salaries_tag,positions_tag,update_time_tag):
        jobs_title.append(jobs.get('title').replace('\n','').strip())
        job_companies.append(companies.text.replace('\n','').strip())
        job_cities.append(cities.text.replace('\n','').strip())
        job_salaries.append(salaries.text.replace('\n','').strip())
        jobs_position.append(positions.text.replace('\n','').strip())
        time_n=datetime.fromtimestamp(int(times.get('data-datetime').replace('\n','').strip()))
        update_times.append(datetime.strftime(time_n,'%Y-%m-%d %H:%M:%S'))

# Save jobs information into jobs dataframe
df_jobs['Jobs_title']=jobs_title
df_jobs['Company']=job_companies
df_jobs['City']=job_cities
df_jobs['Salary']=job_salaries
df_jobs['Position']=jobs_position
df_jobs['Update_time']=update_times
df_jobs['Update_time']=pd.to_datetime(df_jobs['Update_time'],format='%Y-%m-%d %H:%M:%S')
df_jobs['Key']=df_jobs['Jobs_title']+'#'+df_jobs['Company']

# Compare 2 data frame, append new data
df_jobs_new=df_jobs[~(df_jobs['Key'].isin(df_jobs_sql['Key']) & df_jobs['Update_time'].isin(df_jobs_sql['Update_time']))]
df_jobs_sql=pd.concat([df_jobs_sql,df_jobs_new],axis=0)
df_jobs_sql=df_jobs_sql.drop_duplicates(subset=['Key','Update_time']).reset_index(drop=True)

# Save table in mySQL
df_jobs_sql.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print('Jobs_data: ',df_jobs_sql.shape)
