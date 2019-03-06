import requests
from tqdm import tqdm
import time

class CheckNet(object):
    net_cnt = 0
        ##__
    def update_progress(self,progress):
        for i in tqdm(range(progress)):
            time.sleep(1)
    ##__
    def check_connection(self,url):
        try:
            response = requests.get(url)
            self.status = True
        except Exception as e:
            # print("Something went wrong:")
            self.status = False
            # print(e)
        finally:
            if self.status == False:
                self.net_cnt += 1
                # print('off count.//...>> {}'.format(self.net_cnt))
                # time.sleep(5)
                self.update_progress(5)
                self.check_connection(url)
            else:
                pass
                # print('connected...   ',self.status)
        return self.status
