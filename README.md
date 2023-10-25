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
 #### + Trước hết sẽ tạo 1 dataframe rỗng, tạo các list rỗng để lưu trữ nội dung sau khi crawl
 ```
# Create jobs dataframe, empty list
df_jobs = pd.DataFrame(columns=['Jobs_title','Company','City','Salary','Position','Update_time','Key'])
jobs_title, job_companies, job_cities, job_salaries, update_times, jobs_position = [], [], [], [], [], []
 ```
