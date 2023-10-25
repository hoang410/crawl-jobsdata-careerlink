# crawl-jobsdata-careerlink
# CÀO DỮ LIỆU VIỆC LÀM TỪ CAREERLINK, LƯU TRỮ VÀO MYSQL, LIÊN KẾT POWER BI

Xin chào mọi người!

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
 ### - Tạo sẵn database 'Careerlink_data' và bảng 'jobs_data' như bên dưới. Về nội dung các cột trong 'jobs_data' sẽ giải thích rõ hơn ở nội dung code.
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
