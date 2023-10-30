# crawl-jobsdata-careerlink
# CÀO DỮ LIỆU VIỆC LÀM TỪ CAREERLINK, LƯU TRỮ VÀO MYSQL, LIÊN KẾT POWER BI

Xin chào!

Nhân dịp vừa học xong các khoá về DE, DA, DS nên mình tự build 1 project nho nhỏ về các kỹ năng mình đã học được từ các khoá học vừa rồi.

Sơ lược qua nội dung có thể tóm tắt như sau: mình sẽ crawl toàn bộ các thông tin về tuyển dụng trên web careerlink. Sau đó đẩy vào mySQL. Tiếp tục lấy dữ liệu từ mySQL vào Power BI để phân tích.

Cơ bản là khá đơn giản! Bắt đầu vào việc thôi!

## 1. Crawl tất cả các tin tuyển dụng từ trang tìm kiếm:
###  - Đầu tiên, import các thư viện cần thiết
  
```
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
```
 ### - Tạo sẵn database 'Careerlink_data' và bảng 'jobs_data' như bên dưới. Về nội dung các cột trong 'jobs_data' sẽ giải thích rõ hơn ở các phần tiếp theo.
   ![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/8ba5d0aa-5bbf-46ae-9412-eec4a97b0b17) 
   ![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/827207b4-d5e4-4420-bd01-9fbbf66123b5)
 ### - Kết nối với CSDL mySQL vừa tạo
```
# Connect mySQL
db_user = 'root'
db_password = '******' # Enter your password here
db_host = '127.0.0.1'
db_port = 3306
db_name = 'Careerlink_data'
table_name = 'jobs_data'
connection_str = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_str)
```
 ###  - Lấy data từ mySQL
```
# Load dataframe from mySQL
sql_query_jobs_data = 'SELECT * FROM jobs_data'
df_jobs_sql = pd.read_sql_query(sql_query_jobs_data,engine)
```
 ###  - Đếm tổng số trang của link các công việc để scan hết các tin tuyển dụng.
```
# Counting total page
url_page1 = 'https://www.careerlink.vn/vieclam/list'
reponse_count = requests.get(url_page1)
html_count = reponse_count.text
soup_count = BeautifulSoup(html_count,'lxml')
pages_total = soup_count.find_all('a',class_='page-link')
total_page = int(pages_total[4].text)
print(total_page)
```
 ###  - Phần này sẽ tạo dataframe để lưu dữ liệu
 ####   + Trước hết sẽ tạo 1 dataframe rỗng, tạo các list rỗng để lưu trữ nội dung sau khi crawl
 ```
# Create jobs dataframe, empty list
df_jobs = pd.DataFrame(columns=['Jobs_title','Company','City','Salary','Position','Update_time','Key'])
jobs_title, job_companies, job_cities, job_salaries, update_times, jobs_position = [], [], [], [], [], []
 ```
####    + Chúng ta sẽ duyệt qua lần lượt cho từng trang để lấy các nội dung trong trang, xác định các thẻ chưa nội dung cần lấy để trích xuất ra và thêm vào list trống đã tạo bên trên. Các list tương ứng là 'jobs_title': Tiêu đề công việc, 'job_companies': Tên công ty, 'job_salaries': Mức thu nhập,'jobs_position': Vị trí, 'update_times': Thời gian đăng bài. Sau khi xác định được các thẻ, lấy nội dung cần thiết thì sẽ thêm vào các list rỗng.

```
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
```
####    + Gán các list vừa rồi vào các cột trong dataframe tương ứng. Trong đó cột 'Key' được tạo từ cột 'Jobs_title' và 'Company' để làm key kết nối với các bảng khác nhau.
```
# Save jobs information into jobs dataframe
df_jobs['Jobs_title']=jobs_title
df_jobs['Company']=job_companies
df_jobs['City']=job_cities
df_jobs['Salary']=job_salaries
df_jobs['Position']=jobs_position
df_jobs['Update_time']=update_times
df_jobs['Update_time']=pd.to_datetime(df_jobs['Update_time'],format='%Y-%m-%d %H:%M:%S')
df_jobs['Key']=df_jobs['Jobs_title']+'#'+df_jobs['Company']
```
###  - So sánh data mới crawl và data cũ từ database và cập nhật data phát sinh mới.
```
# Compare 2 data frame, append new data
df_jobs_new=df_jobs[~(df_jobs['Key'].isin(df_jobs_sql['Key']) & df_jobs['Update_time'].isin(df_jobs_sql['Update_time']))]
df_jobs_sql=pd.concat([df_jobs_sql,df_jobs_new],axis=0)
df_jobs_sql=df_jobs_sql.drop_duplicates(subset=['Key','Update_time']).reset_index(drop=True)
```
###  - Lưu data vào lại database
```
# Save table in mySQL
df_jobs_sql.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print('Jobs_data: ',df_jobs_sql.shape)
```
## 2. Crawl các thông tin liên quan như phân loại nhóm công việc, kinh nghiệm, học vấn, loại công việc:
Mình crawl thêm phần này để thuận tiện cho việc phân tich theo dõi cho từng nhóm phân loại.
Phần này mình sẽ xử lý với phân loại theo kinh nghiệm.
###  - Vẫn là import các thư viện, thiết lập kết nối với database, load dataframe cũ ra để xử lý. Table sẽ có 2 cột gồm cột Experience và Key (để kết nối với Table Jobs_data vừa tạo bên trên).
```
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
```
###  - Phần này sẽ lấy các thông tin về phân loại theo kinh nghiệm làm việc, lưu vào 1 list
```
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
```
###  - Tiếp theo sẽ lưu lại các đường link theo từng phân loại để phục vụ cho việc thu thập thông tin công việc phân chia theo kinh nghiệm
```
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
```
###   - Viết 1 function đếm số trang để duyệt qua các trang và lấy thông tin việc làm
```
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
```
###   - Phần này tạo bảng Experience với cột Key bằng 2 cột Company và Jobs_title ghép lại, cũng tương tự như cột Key ở mục bên trên, các cột Key này sẽ có mối quan hệ với nhau
```
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
```
###  - Cuối cùng so sánh 2 dataframe, thêm các mục mới vào dữ liệu và lưu lại
```
# Compare 2 dataframe
df_new_exp=df_exp[~df_exp['Key'].isin(df_exp_sql['Key'])]
df_exp_sql=pd.concat([df_exp_sql,df_new_exp],axis=0)
df_exp_sql=df_exp_sql.drop_duplicates(subset=['Key'])

# Save to mySQL
df_exp_sql.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print('Experiences:',df_exp_sql.shape)
```
### Các nội dung phân loại khác, cách làm cũng tương tự.
### Triển khai crawl song song các file.
### Thiết lập mối quan hệ giữa các bảng thông qua cột Key.
![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/2eeccce8-8fad-4c2a-92b5-038a3c4cb88a)

## 3. Cuối cùng load dữ liệu qua Power BI và tạo dashboard:
![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/cbc6976b-e501-46b8-9907-f99a6d2e5fa5)

![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/bef54f11-77a7-4fe2-875e-b96c3805dec0)

Nhập UserID và Password. Load các tables cần thiết cho thống kê phân tích

![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/b5a1813f-f06a-46f2-9177-008c815f37cb)

Tạo các dashboard cơ bản:

![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/35cfa662-9e5d-4cf5-b89a-f10b005b528d)

![image](https://github.com/hoang410/crawl-jobsdata-careerlink/assets/119757225/2055ff41-00bc-47e9-ab6f-dae40b6cf81a)






