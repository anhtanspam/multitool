import requests
import time
import pandas as pd
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Event
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import dataLoad
class ProfileManager:
    def __init__(self):
        self.fileExcelLoad = pd.read_excel(f'{dataLoad.fileExcelLoad}', sheet_name="Sheet2")
        self.linkNoteAccFail = dataLoad.fileAccFail
        self.linkNoteAccDie = dataLoad.fileAccDie
        self.accPerTurn = int(dataLoad.accPerTurn)
        self.ref_group_link = dataLoad.ref_group_link
        self.linkPicture = dataLoad.linkPicture
        self.scale_windows = dataLoad.scale_windows
        self.colour_in_rgb = str(dataLoad.colour_in_rgb)
        self.api_url = "http://127.0.0.1:19995/api/v3/profiles/{action}/{id}"
        time.sleep(1)
    def run(self, x, i):
        setData1 = int(i)
        setData2 = int(x)
        rowProfile = setData1 + setData2
        tenProfile1 = self.fileExcelLoad.iloc[rowProfile, 0]
        tenProfile = str(tenProfile1)
        idTab1 = self.fileExcelLoad.iloc[rowProfile, 1]  
        profile_id = idTab1.strip()
        for openChrome in range(6):
            try:
                win_pos_value = self.calculate_window_position(x)
                params = {
                    "win_scale": self.scale_windows,
                    "win_pos": win_pos_value,
                    "win_size": "500,700"
                }
                start_url = self.api_url.format(action="start", id=profile_id)
                response = requests.get(start_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    success_value = data.get('success')
                    driver_path = data['data']['driver_path']
                    remote_debugging_address = data['data']['remote_debugging_address']
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_experimental_option("debuggerAddress", remote_debugging_address)
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.close_extra_tabs(driver)
                    print(f"Profile {tenProfile} mở thành công, code:{success_value}...Delay 6s before loading...")
                    time.sleep(6)
                    break
            except Exception as e:
                print(f"Đã có lỗi xảy ra: {tenProfile}>>>Đang quay lại từ đầu.")
                time.sleep(5)
                continue
        self.fang_game_notpixel(driver, tenProfile, profile_id)
    def calculate_window_position(self, x):
        line1 = x * 505
        line2 = (x-10)*505
        line3 = (x-20)*505
        if x < 10:
            return f"{line1},5"
        elif 9 < x < 20:
            return f"{line2},700"
        else:
            return f"{line3},1400"
    def close_extra_tabs(self, driver):
        try:
            for tab in range(1, 3):
                driver.switch_to.window(driver.window_handles[tab])
                driver.close()
                time.sleep(0.3)
        except:
            time.sleep(0.5)
    def fang_game_notpixel(self, driver, tenProfile, profile_id):
        try:
            for checkAcc in range(8):
                driver.get("chrome://settings/")
                time.sleep(1)
                try:
                    print(f" Vào Check live acc tele in Profile {tenProfile}...") 
                    driver.get("https://web.telegram.org/k/")
                except:pass
                if checkAcc == 7:
                    print(f'{tenProfile}>>>acc DIE')
                    with open(self.linkNoteAccDie, 'a+') as noteAccDie:
                        noteAccDie.write(f'{tenProfile}|Die\n')
                    time.sleep(1)
                    self.close_profile(profile_id)
                else:pass
                try:
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h4[text()="Log in to Telegram by QR Code"]')))
                    print(f'{tenProfile}>>>acc DIE')
                    with open(self.linkNoteAccDie, 'a+') as noteAccDie:
                        noteAccDie.write(f'{tenProfile}|Die\n')
                    time.sleep(1)
                    self.close_profile(profile_id)
                except:pass
                try:
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="input-search"][1]')))
                    print(f"Profile {tenProfile}>>ACC tele vẫn ngonnn>>>Log to Claim...")  
                    break
                except:pass
            time.sleep(1)                   
            for logGam1e in range(6):
                if logGam1e == 5:
                    time.sleep(1)
                    self.close_profile(profile_id)
                else:pass
                try:
                    self.log_fang_game(tenProfile, driver)
                    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="root"]/div[1]/div[1]/div[1]/div[2]/div[2]/button[1]/*[1]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    time.sleep(3)
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[text()="Your balance"]')))                               
                except:pass                     
                try:
                    print(f">>>{tenProfile}>>> Claim pixel ")
                    time.sleep(1)
                    element = driver.find_element(By.XPATH, '//div[text()="Your balance"]')
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(2)

                    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Claim"]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                except:pass
                try:
                    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[text()="CLAIM IN "]')))
                    print(f">>>{tenProfile}>>> Đã claim xong>>>Vào vẽ tranh")
                    break
                except:pass      
            time.sleep(5)
            for logGamePaint in range(6):
                if logGamePaint == 5:
                    time.sleep(1)
                    self.close_profile(profile_id)
                else:pass
                try:
                    self.log_fang_game(tenProfile, driver)
                    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_buttons_container_srn55_18"]/button[2]//*[@src="https://fra1.digitaloceanspaces.com/notpix-user-content/templates/630028458.png"]')))
                    break
                except:pass
            print(f" >>>{tenProfile} >>> pick màu")
            canvas = driver.find_element(By.ID, 'canvasHolder')
            canvas_location = canvas.location
            canvas_size = canvas.size
            while True:
                time.sleep(1)
                try:
                    random_x = random.randint(-10, 11)
                    random_y = random.randint(-12, 16)
                    actions = ActionChains(driver)
                    actions.move_to_element_with_offset(canvas, random_x, random_y).click().perform()
                    print(f'{tenProfile} click at ({random_x},{random_y}) ')
                except:pass
                try:
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_order_panel_1ley0_1"]//div[@class="_info_1ley0_38"]/div[1]')))
                    break
                except:pass
            time.sleep(5)
            xpath_father = f'//div[@class="_order_panel_1ley0_1"]//div[@class="_info_1ley0_38"]/div[@style="background-color: rgb{self.colour_in_rgb};"]'
            xpath_son = f'//div[@class="_color_line_epppt_15"]//div[@style="background-color: rgb{self.colour_in_rgb};"]'
            while True:
                print(f"{tenProfile}>>>ĐANG PICK COLOUR")
                try:
                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_order_panel_1ley0_1"]//div[@class="_info_1ley0_38"]/div[1]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    try:
                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_color_line_epppt_15"]/div[17]')))
                        actions = ActionChains(driver)
                        actions.move_to_element(element).click().perform()
                    except:pass
                    try:
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_father)))
                    except:
                        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, xpath_son)))
                        actions = ActionChains(driver)
                        actions.move_to_element(element).click().perform()
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_father)))
                    break
                except:pass
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_order_panel_1ley0_1"]//div[@class="_info_1ley0_38"]/div[1]')))
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            print(f"{tenProfile}>>> Painting...")
            canvas = driver.find_element(By.ID, "canvasHolder")
            canvas_location = canvas.location
            canvas_size = canvas.size
            for painting in range(1,100,1):
                randomWait = random.randint(5,12)
                waitTime = randomWait / 10
                time.sleep(waitTime)
                try:
                    element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//button[@class="_button_1ley0_143"]//div[@class="_counter_oxfjd_32"]/span[2]')))
                    soLuot = element.text
                    if soLuot== "0":
                        print(f">>>@@@@@{tenProfile} >>> Hết lượt tô màu, Đóng profile sau 3 giây...")
                        time.sleep(1)
                        break
                    else:pass                
                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_buttons_container_srn55_18"]/button[2]//*[@src="https://fra1.digitaloceanspaces.com/notpix-user-content/templates/630028458.png"]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()                                
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_buttons_container_srn55_18"]//div[@class="_container_srbwq_1"]')))
                    while True:
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACABAMAAAAxEHz4AAAAFVBMVEVHcEz/3Jr/6ADjygD/AAC5AAAAAAB/sfDAAAAAAXRSTlMAQObYZgAAAJJJREFUeNrt2bEJBCEQQNFrYVqwhWnBFq6F338Jx4IiyIG76ez/iRjMiwyE+Zj9i0MC9QGA7yEAgarAGu6HJiJQHTgnICAgIFAbAHgGrARqAACZmROIiAC4zt573+8TaK01gWLA6O5DyswUqAVcMXoCzGGBCsBqAjGCVYz2D4ZAbWBP4EXA6AQACJQB3LEImO39AJS0GBsvGYIKAAAAAElFTkSuQmCC"]')))
                        actions = ActionChains(driver)
                        actions.move_to_element(element).click().perform()
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="_button_j77dp_27 _fast_type_button_j77dp_49 _shop_button_j77dp_44 _fast_mode_button_enabled_j77dp_72"]')))
                        break
                    while True:
                        element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//button[@class="_button_1ley0_143"]//div[@class="_counter_oxfjd_32"]/span[2]')))
                        soLuot1 = element.text
                        if soLuot1== "0":
                            time.sleep(1)
                            break
                        else:
                            soLanChamBi = int(soLuot1)
                            for clickPaint in range(soLanChamBi):
                                random_x = random.randint(-61, 58)
                                random_y = random.randint(-60, 15)                            
                                actions = ActionChains(driver)
                                actions.move_to_element_with_offset(canvas, random_x, random_y).click().perform()
                                valueWait = random.randint(2,9) /10
                                time.sleep(valueWait)
                except:pass
            time.sleep(1)
        except Exception as e:
            print(f"Acc {tenProfile} FAIL-saving info to file note !!!! Error: {str(e)}")
            self.save_fail_info(tenProfile, profile_id)
            self.close_profile(profile_id)
        finally:
            self.close_profile(profile_id)
    def log_fang_game(self, tenProfile, driver):
        driver.get("chrome://settings/")
        time.sleep(1)
        driver.get(self.ref_group_link)
        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//span[@class="translatable-message"]//a[text()="{self.linkPicture}"]')))
        driver.execute_script("arguments[0].click();", element)
        try:
            element = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Launch"]')))
            driver.execute_script("arguments[0].click();", element)
        except:pass
        iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
        print(f"{tenProfile} wait 10s for Checking banner popup to close ...")
        try:
            element = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_container_n1egb_1"]//div[@class="_close_n1egb_30"]')))
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(2)
        except:pass
        try:
            element = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Go to Web version"]')))
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(3)
            try:
                for tab in range(1,3):
                    driver.switch_to.window(driver.window_handles[tab])
                    driver.close()
                    time.sleep(0.3)
            except:time.sleep(0.5)
            driver.switch_to.window(driver.window_handles[0])
            iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
            time.sleep(1)
        except:pass        
        for closeBanner in range(2):
            try:
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_container_1df7o_14"]//div[@class="_header_q0ezh_11"]/div[1]')))
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                time.sleep(2)
            except:pass
            try:
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_container_1df7o_14"]//div[@class="_header_n1egb_11"]/div[2]/div[1]')))
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                time.sleep(2)
            except:pass
    def save_fail_info(self, tenProfile, profile_id):
        with open(self.linkNoteAccFail, 'a+') as noteAccFail:
            noteAccFail.write(f'{tenProfile}|{profile_id}|error #NOTPIXEL paint\n')
    def close_profile(self, profile_id):
        try:
            close_url = self.api_url.format(action="close", id=profile_id)
            close_response = requests.get(close_url)
            if close_response.status_code == 200:
                close_data = close_response.json()
                print(f"Profile closed, code: {close_data.get('message')}")
            else:
                print("Lỗi khi đóng profile. Status code:", close_response.status_code)
        except:
            pass
    def run_turn(self):
        while True:
            try:
                for i in range(0, 5000, self.accPerTurn):
                    time.sleep(1)
                    idBeginturnacc = str(self.fileExcelLoad.iloc[i, 1])
                    print(f"Turn bắt đầu từ acc: {self.fileExcelLoad.iloc[i, 0]}")
                    if len(idBeginturnacc) < 10:
                        break                    
                    run_threads = []
                    for x in range(self.accPerTurn):
                        t_run = threading.Thread(target=self.run, args=(x, i))
                        run_threads.append(t_run)
                        t_run.start()
                    for t_run in run_threads:
                        t_run.join()
                    print(">>ĐÃ QUẤT XONG TURN ACC !!!")
                    print("Đang Vào chạy turn tiếp")
                    self.countdown(5)
            except Exception as e:
                print(f'Đã xong lô acc... {str(e)}')
    def countdown(self, seconds):
        for sec in range(seconds, 0, -1):
            print(f'Continue in {sec}s !')
            time.sleep(1)
if __name__ == "__main__":
    manager = ProfileManager()
    manager.run_turn()
