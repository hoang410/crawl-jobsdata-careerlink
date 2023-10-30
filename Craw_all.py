from multiprocessing import Process
import time

start_time = time.time()
def run_script(script_name):
    import subprocess
    subprocess.call(["python", script_name])

if __name__ == "__main__":
    script1 = Process(target=run_script, args=("Crawl_jobs_data_Careerlink.py",))
    script2 = Process(target=run_script, args=("Careers.py",))
    script3 = Process(target=run_script, args=("Experience.py",))
    script4 = Process(target=run_script, args=("Education.py",))
    script5 = Process(target=run_script, args=("Jobs_type.py",))

    script1.start()
    script2.start()
    script3.start()
    script4.start()
    script5.start()

    script1.join()
    script2.join()
    script3.join()
    script4.join()
    script5.join()


end_time = time.time()
execution_time = end_time - start_time
print('Thời gian thực hiện:',execution_time/60)