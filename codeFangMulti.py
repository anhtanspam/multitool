import requests
import time
import pandas as pd
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import dataLoad

class ProfileManager:
    def __init__(self):
        self.choseBlumAction = 1 #SET 1 nhặt lá, SET 2 làm nhiệm vụ
        self.link_check = f"http://{dataLoad.proxyLink}:6868/status?proxy={dataLoad.proxyLink}:"
        self.link_reset = f"http://{dataLoad.proxyLink}:6868/reset?proxy={dataLoad.proxyLink}:"
        self.link_get_ip = f"http://{dataLoad.proxyLink}:6868/api/v1/proxy/public_ip?proxy={dataLoad.proxyLink}:"
        self.file_ip = dataLoad.fileIp
        self.numberDcom = int(dataLoad.numberDcom)
        self.port_proxy_from = int(dataLoad.portProxyFrom)
        self.fileExcelLoad = pd.read_excel(f'{dataLoad.fileExcelLoad}', sheet_name="Sheet1")
        self.portProxyFrom = int(dataLoad.portProxyFrom)
        self.linkNoteAccFail = dataLoad.fileAccFail
        self.linkNoteAccDie = dataLoad.fileAccDie
        self.accPerTurn = int(dataLoad.accPerTurn) #Thêm "/2" ở cuối nếu chỉ chạy riêng notpixel
        self.ref_group_link = dataLoad.ref_group_link
        self.ref_group_link_blum = dataLoad.ref_group_link_blum
        self.linkRefBlum = dataLoad.linkRefBlum
        self.linkPicture = dataLoad.linkPicture
        self.scale_windows = dataLoad.scale_windows
        self.colour_in_rgb = str(dataLoad.colour_in_rgb)
        self.js_script = dataLoad.js_script
        self.api_url = "http://127.0.0.1:12683/api/v3/profiles/{action}/{id}"
        time.sleep(1)
    
    def proxy_reset(self, p):
        setData2 = int(p)
        portProxy1 = setData2 + self.port_proxy_from
        portProxy = str(portProxy1)
        linkCheckProxy = self.link_check + portProxy
        linkResetProxy = self.link_reset + portProxy
        linkGetipProxy = self.link_get_ip + portProxy
        while True:
            checkIp = requests.get(linkCheckProxy)
            kqCheckip = checkIp.json()["status"]
            if kqCheckip:
                print("PORT:", portProxy, "- Connected")
                time.sleep(1)
                while True:
                    getIpport = requests.get(linkGetipProxy)
                    ipPort = getIpport.json()["ip"]
                    with open(self.file_ip, 'r') as fileip:
                        historyIp = fileip.read()
                        if ipPort not in historyIp:
                            print('Port', portProxy, "ip:", ipPort, 'GOOD !')
                            with open(self.file_ip, 'a+') as fileIpload:
                                fileIpload.write(f'{ipPort}\n')
                            time.sleep(1)
                            break
                        else:
                            print('Port', portProxy, "ip:", ipPort, 'bị trùng lặp IP, đang reset lại ip !!!')
                            time.sleep(1)
                            requests.get(linkResetProxy)
                            time.sleep(20)
                        time.sleep(1)
                time.sleep(1)
                break
            else:
                print("Port", portProxy, "Oẳng rồi, đang reset lại, đợi 15s !")
                time.sleep(1)
                requests.get(linkResetProxy)
                time.sleep(20)
            time.sleep(1)
        time.sleep(1)

    def run(self, x, i):
        setData1 = int(i)
        setData2 = int(x)
        rowProfile = setData1 + setData2
        if x < 8:
            rowProfile = setData1 + setData2
            tenProfile1 = self.fileExcelLoad.iloc[rowProfile, 0]
            idTab1 = self.fileExcelLoad.iloc[rowProfile, 1] 
        else:
            rowProfile = (setData1 + setData2) - 8
            tenProfile1 = self.fileExcelLoad.iloc[rowProfile, 2]
            idTab1 = self.fileExcelLoad.iloc[rowProfile, 3]
        tenProfile = str(tenProfile1)         
        profile_id = idTab1.strip()
        for openChrome in range(12):
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
                    print(f"Profile {tenProfile} mở thành công, code:{success_value}...Delay 11s before loading...")
                    time.sleep(11)
                    break
            except Exception as e:
                print(f"Đã có lỗi xảy ra: {tenProfile}>>>Đang quay lại từ đầu.")
                time.sleep(5)
                continue
        if x < 8:
            self.notpixel_fang(driver, tenProfile, profile_id)
        else:
            if self.choseBlumAction == 1:
                self.blum_fang_nhatla(driver, tenProfile, profile_id)
            else:
                self.blum_nhiemvu_fang(driver, tenProfile, profile_id)


    def calculate_window_position(self, x):
        line1 = x * 505
        line2 = (x-8)*505
        line3 = (x-16)*505
        if x < 8:
            return f"{line1},5"
        elif 7 < x < 16:
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
    def blum_fang_nhatla(self, driver, tenProfile, profile_id):
        try:
            for ff in range (8):
                driver.get('https://web.telegram.org/k/')
                try:
                    element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//h4[text()="Log in to Telegram by QR Code"]')))                    
                    print(f'{tenProfile}>>>acc DIE')
                    with open(self.linkNoteAccDie, 'a+') as noteAccDie:
                        noteAccDie.write(f'{tenProfile}|Die\n')
                    time.sleep(1)
                    self.close_profile(profile_id)
                except:pass
                for l in range(10):
                    try:
                        time.sleep(1)
                        driver.get("chrome://settings/")
                        time.sleep(1)
                        driver.get(self.ref_group_link_blum)
                        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//span[@class="translatable-message"]//a[text()="{self.linkRefBlum}"]')))
                        driver.execute_script("arguments[0].click();", element)
                        try:
                            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Launch"]')))
                            driver.execute_script("arguments[0].click();", element)
                        except:pass                
                        elementIframe = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '//iframe[@class="payment-verification"]')))                        
                        break
                    except:pass
                iframe = WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                for dd in range(1,19,1):
                    print(f'>>{tenProfile}-try checkin turn: {dd}/18')
                    try:
                        elementReload = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                        elementReload.click()
                    except:pass           
                    try:
                        elementTask = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                        break
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="daily-reward-page page no-padding"]//div[@class="kit-fixed-wrapper no-layout-tabs"]//button[1]/div[2]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Claim"]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[@class="button-label"]/span[1]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                try:
                    elementTask = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                    print(f'``{tenProfile} Check in ok>>>>playgame')
                    break
                except:pass              
            for playGame in range(1,21,1):
                print(f'>>>{tenProfile}>>> play turn: {playGame}/20')
                if playGame == 1:
                    driver.execute_script(self.js_script)
                else:pass 
                for clickError in range(9):
                    try:
                        elementReload = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                        elementReload.click()
                        if clickError == 8:
                            time.sleep(1)
                            self.close_profile(profile_id)                     
                    except:                  
                        break
                try:
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//i[@class="ticket"]')))
                    js_code2 = "arguments[0].scrollIntoView();"
                    element = driver.find_element(By.XPATH, '//i[@class="ticket"]')
                    driver.execute_script(js_code2, element)
                except:pass
                time.sleep(1)
                try:
                    try:
                        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="play-btn secondary"]/i[@class="ticket"]')))
                        print(f'--acc {tenProfile} hết Vé Chơi>>> Close profile in 2s...')
                        break
                    except:   
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="play-btn"]')))
                        driver.execute_script("arguments[0].click();", element)            
                except:pass
                try:
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="buttons"]/button[1]/div[2]')))
                    js_code2 = "arguments[0].scrollIntoView();"
                    element = driver.find_element(By.XPATH, '//div[@class="buttons"]/button[1]/div[2]')
                    driver.execute_script(js_code2, element)                       
                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="buttons"]/button[2]/div[2]/span[1]')))
                    driver.execute_script("arguments[0].click();", element)
                except:pass
                try:                    
                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-game-end animation-stage-final"]//div[@class="buttons"]/button[2]')))
                    driver.execute_script("arguments[0].click();", element)
                except:pass
                if playGame == 20:
                    element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//div[@class="content"]//div[@class="reward"]')))
                    print(f'--acc {tenProfile} hết ván game cuối>>CLOSING profile...')
                else:pass               
            time.sleep(2)
        except Exception as e:
            print(f"Acc {tenProfile} LoadBlumGame FAIL-saving info to file note !!!!")
            self.save_fail_info(tenProfile, profile_id)
            self.close_profile(profile_id)
        finally:
            self.close_profile(profile_id)
    def blum_nhiemvu_fang(self, driver, tenProfile, profile_id):
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)
        driver.execute_script("window.open('chrome://settings/', '_blank');")
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[0])
        try:
            for ff in range (8):
                driver.get('https://web.telegram.org/k/')
                try:
                    element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//h4[text()="Log in to Telegram by QR Code"]')))                    
                    print(f'{tenProfile}>>>acc DIE')
                    with open(self.linkNoteAccDie, 'a+') as noteAccDie:
                        noteAccDie.write(f'{tenProfile}|Die\n')
                    time.sleep(1)
                    self.close_profile(profile_id)
                except:pass
                for l in range(10):
                    try:
                        time.sleep(1)
                        driver.get("chrome://settings/")
                        time.sleep(1)
                        driver.get(self.ref_group_link_blum)
                        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//span[@class="translatable-message"]//a[text()="{self.linkRefBlum}"]')))
                        driver.execute_script("arguments[0].click();", element)
                        try:
                            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Launch"]')))
                            driver.execute_script("arguments[0].click();", element)
                        except:pass                
                        elementIframe = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '//iframe[@class="payment-verification"]')))                        
                        break
                    except:pass
                iframe = WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                for dd in range(1,19,1):
                    print(f'>>{tenProfile}-try checkin turn: {dd}/18')
                    try:
                        elementReload = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                        elementReload.click()
                    except:pass           
                    try:
                        elementTask = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                        break
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="daily-reward-page page no-padding"]//div[@class="kit-fixed-wrapper no-layout-tabs"]//button[1]/div[2]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Claim"]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                    try:
                        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[@class="button-label"]/span[1]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                try:
                    elementTask = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                    print(f'``{tenProfile} Check in ok>>>>playgame')
                    break
                except:pass      
                #############################################
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="layout-tabs tabs"]/a[2]')))
            driver.execute_script("arguments[0].click();", element)
            for clickBar in range(4,3,-1):
                c1Bar = str(clickBar)
                for fixError in range(6):
                    try:
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                        element.click()
                    except:
                        print(f'>>{tenProfile}-Không có lỗi xảy ra...')
                        break
                    if fixError == 5:
                        for ff in range (6):                            
                            try:
                                time.sleep(1)
                                driver.get("chrome://settings/")
                                time.sleep(1)
                                driver.get(self.ref_group_link_blum)
                                element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//span[@class="translatable-message"]//a[text()="{self.linkRefBlum}"]')))
                                driver.execute_script("arguments[0].click();", element)
                                try:
                                    element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Launch"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass                
                                elementIframe = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '//iframe[@class="payment-verification"]')))                        
                                break
                            except:pass
                        iframe = WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))                    
                        for dd in range(1,19,1):
                            print(f'>>{tenProfile}-try checkin turn: {dd}/18')
                            try:
                                elementReload = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                                elementReload.click()
                            except:pass           
                            try:
                                elementTask = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                                break
                            except:pass
                            try:
                                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="daily-reward-page page no-padding"]//div[@class="kit-fixed-wrapper no-layout-tabs"]//button[1]/div[2]')))
                                driver.execute_script("arguments[0].click();", element)
                            except:pass
                            try:
                                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Claim"]')))
                                driver.execute_script("arguments[0].click();", element)
                            except:pass
                            try:
                                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[@class="button-label"]/span[1]')))
                                driver.execute_script("arguments[0].click();", element)
                            except:pass
                            try:
                                elementTask = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-index-index"]/div[3]//div[text()="Farming"][1]')))
                                print(f'``{tenProfile} Check in ok>>>>playgame')
                                break
                            except:pass              
                            #############################################
                        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="layout-tabs tabs"]/a[2]')))
                        driver.execute_script("arguments[0].click();", element)
                        for fixError2 in range(3):
                            try:
                                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                                element.click()
                            except:
                                print(f'>>{tenProfile}-Không có lỗi xảy ra...')
                                break
                            if fixError2==2:
                                self.close_profile(profile_id)
                            else:pass
                if c1Bar==2:pass                    
                else:
                    ###333
                    element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-tasks-list is-short-card"]/div[3]//div[text()="Mở"]')))
                    driver.execute_script("arguments[0].click();", element)                        
                    for cst in range(3):
                        print(f'>>>>>>{tenProfile}-try click start: {cst}')
                        try:
                            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-tasks-subtasks-modal"]//div[text()="Bắt đầu"][1]')))
                            driver.execute_script("arguments[0].click();", element)
                            print(f'{tenProfile} clicked [start]')
                            driver.switch_to.window(driver.window_handles[1])
                            time.sleep(0.5)
                            try:
                                driver.switch_to.window(driver.window_handles[2])
                                driver.close()
                                time.sleep(0.3)
                            except:pass
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get("chrome://settings/")
                            time.sleep(3)
                            driver.switch_to.window(driver.window_handles[0])
                            iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                        except:break
                    try:
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="kit-button is-medium is-ghost is-icon-only close-btn"]/div[3]/div[1]')))
                        driver.execute_script("arguments[0].click();", element)
                    except:pass
                    ######
                    try:
                        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//div[@class="list"]/label[{c1Bar}]')))
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                    except:pass
                    js_code2 = "arguments[0].scrollIntoView();"
                    element = driver.find_element(By.XPATH, f'//div[@class="list"]/label[{c1Bar}]')
                    driver.execute_script(js_code2, element)
                    try:
                        for c1Start in range(1,101,1):                    
                            print(f'@{tenProfile}> Đang Click <START> lần {c1Start}/100')
                            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="sections"]/div[3]//div[text()="Bắt đầu"][1]')))
                            driver.execute_script("arguments[0].click();", element)
                            try:
                                for tab in range(2,5,1):
                                    driver.switch_to.window(driver.window_handles[tab])
                                    driver.close()
                                    time.sleep(0.3)
                            except:time.sleep(0.5)
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get("chrome://settings/")
                            time.sleep(5)
                            driver.switch_to.window(driver.window_handles[0])
                            iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                    except:
                        print(f'@{tenProfile}> Không còn <START>')
                    try:
                        for qv in range(1,101,1):
                            print(f'{tenProfile} đang tìm verify lần {qv}/100')              
                            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Xác minh"][1]')))
                            driver.execute_script("arguments[0].click();", element)
                            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="heading"]//div[@class="title"]')))
                            titleTask = element.text
                            if titleTask == "What is On-chain Analysis?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMEXTRA")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "What is Slippage?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOBUZZ")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "What’s Next for DeFi?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMNOW")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Understanding Gas Fees":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOGAS")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Choosing a Crypto Exchange":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOZONE")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Node Sales in Crypto":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMIFY")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "What's Crypto DEX?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("DEXXX")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Crypto Slang. Part 2":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("FOMOOO")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "DeFi Risks: Key Insights":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMHELPS")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Pumptober Special":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("PUMPIT")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "DeFi Explained":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMFORCE")
                                for kg in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Crypto Slang. Part 1":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMSTORM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "How To Find Altcoins?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("ULTRABLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Sharding Explained":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMTASTIC")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "How to trade Perps?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOFAN")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Crypto Terms. Part 1":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMEXPLORER")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Bitcoin Rainbow Chart?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("SOBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Token Burning: How & Why?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("ONFIRE")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "How to Memecoin?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("MEMEBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Pre-Market Trading?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("WOWBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Doxxing? What's that?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("NODOXXING")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "$2.5M+ DOGS Airdrop":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("HAPPYDOGS")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Liquidity Pools Guide":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BLUMERSSS")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "What Are AMMs?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOSMART")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Say No to Rug Pull!":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("SUPERBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "What are Telegram Mini Apps?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("CRYPTOBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Navigating Crypto":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("HEYBLUM")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Secure your Crypto!":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("BEST PROJECT EVER")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "Forks Explained":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("GO GET")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            elif titleTask == "How to Analyze Crypto?":
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
                                element.send_keys("VALUE")
                                for kf in range(5):
                                    try:
                                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="kit-fixed-wrapper no-layout-tabs"]//div[text()="Verify"]')))
                                        driver.execute_script("arguments[0].click();", element)
                                    except:break
                                    time.sleep(1)
                                try:
                                    driver.switch_to.default_content()
                                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="animated-close-icon state-back"]')))
                                    driver.execute_script("arguments[0].click();", element)
                                except:pass
                                time.sleep(1)
                                iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                            else:pass
                    except:
                        print(f'Hết <verify> in {tenProfile}')
                    try:
                        for c1Claim in range(1,101,1):                    
                            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Claim"][1]')))
                            driver.execute_script("arguments[0].click();", element)
                            print(f'{tenProfile} clicked <claim> turn {c1Claim}/50')
                            time.sleep(5)
                    except:print(f'Hết <CLAIM> in: {tenProfile}')
                # #############################################
        
            print(f'>>{tenProfile} VÀO LÀM 540')
            js_code3 = "arguments[0].scrollIntoView();"
            element = driver.find_element(By.XPATH, '//div[text()="Weekly"]')
            driver.execute_script(js_code3, element)
            for fap in range (1):
                try:
                    elementError = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[text()="We are already on the issue"]')))
                    elementReload = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                    elementReload.click()
                except:
                    print(f'>>{tenProfile}-taskWeekly Không có lỗi xảy ra...') 
                print(f'{tenProfile} lần: {fap}/1>>>>>>')               
                try:
                    try:
                        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="reset"]')))
                        element.click()
                    except:print(f'>>{tenProfile}-Không có lỗi xảy ra...')
                    try:
                        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pages-tasks-list is-short-card"]//div[@class="kit-icon done-icon"]')))
                        print(f'{tenProfile} ĐÃ LÀM 540!')
                        break
                    except:
                        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-tasks-list is-short-card"]/div[2]//div[text()="Mở"]')))
                        driver.execute_script("arguments[0].click();", element)
                        for fwl in range(1):
                            print(f'>>>>>>{tenProfile}-turn try: {fwl}/8...')
                            try:
                                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[text()="Earn for checking socials 5/5"]')))
                                print(f'{tenProfile} Done weekly task !')
                                break
                            except:pass
                            for cst in range(7):
                                print(f'>>>>>>{tenProfile}-try click start: {cst}/6...')
                                try:
                                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-tasks-subtasks-modal"]//div[text()="Bắt đầu"][1]')))
                                    driver.execute_script("arguments[0].click();", element)
                                    print(f'{tenProfile} clicked [start]')
                                    driver.switch_to.window(driver.window_handles[1])
                                    time.sleep(0.5)
                                    try:
                                        driver.switch_to.window(driver.window_handles[2])
                                        driver.close()
                                        time.sleep(0.3)
                                    except:pass
                                    driver.switch_to.window(driver.window_handles[1])
                                    driver.get("chrome://settings/")
                                    time.sleep(3)
                                    driver.switch_to.window(driver.window_handles[0])
                                    iframe = WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@class="payment-verification"]')))
                                except:break
                            for cickClaim in range(7):
                                try:
                                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Claim"][1]')))
                                    driver.execute_script("arguments[0].click();", element)
                                    time.sleep(5)
                                except:break
                        try:
                            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="kit-button is-medium is-ghost is-icon-only close-btn"]/div[3]/div[1]')))
                            driver.execute_script("arguments[0].click();", element)
                        except:pass
                except:print(f'{tenProfile} Done weeklytask')
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="pages-tasks-list is-short-card"]/div[3]//div[text()="Mở"]')))
            driver.execute_script("arguments[0].click();", element)
            try:
                for cickClaim in range(7):            
                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Claim"][1]')))
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(5)
            except:pass
            try:
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="kit-button is-medium is-ghost is-icon-only close-btn"]/div[3]/div[1]')))
                driver.execute_script("arguments[0].click();", element)
            except:pass
            print(f'@@@@@@@@@@@Done acc {tenProfile}, Closing.....')
            time.sleep(2)
        except Exception as e:
            print(f"Acc {tenProfile} Pain notpixel FAIL-saving info to file note !!!!")
            self.save_fail_info(tenProfile, profile_id)
            self.close_profile(profile_id)
        finally:
            self.close_profile(profile_id)
    def notpixel_fang(self, driver, tenProfile, profile_id):
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
                    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="root"]/div[1]/div[1]/div[1]/div[2]/div[2]/button[1]//*[@class="_button_img_17fy4_119"]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    time.sleep(3)
                    actions.move_to_element(element).click().perform()
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[text()="Your balance"]')))
                               
                except:pass                     
                try:
                    print(f">>>{tenProfile}>>> Claim pixel ")
                    time.sleep(1)
                    element = driver.find_element(By.XPATH, '//div[text()="Your balance"]')
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(2)

                    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="_button_13oyr_11"]')))
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
                    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_info_posug_58"]/div[1]')))
                    break
                except:pass
            time.sleep(5)
            xpath_father = f'//div[@class="_order_panel_posug_1"]//div[@class="_info_posug_58"]/div[@style="background-color: rgb{self.colour_in_rgb};"]'
            xpath_son = f'//div[@class="_color_line_epppt_15"]//div[@style="background-color: rgb{self.colour_in_rgb};"]'
            while True:
                print(f"{tenProfile}>>>ĐANG PICK COLOUR")
                try:
                    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_info_posug_58"]/div[1]')))
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    try:
                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_color_line_epppt_15"]/div[17]')))
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
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_info_posug_58"]/div[1]')))
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
                    element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_counter_oxfjd_32"]/span[2]')))
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
                        element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_order_panel_posug_1"]//div[@class="_counter_oxfjd_32"]/span[2]')))
                        soLuot1 = element.text
                        if soLuot1== "0":
                            time.sleep(1)
                            break
                        else:
                            soLanChamBi = int(soLuot1)
                            for clickPaint in range(soLanChamBi):
                                random_x = random.randint(-50, 50)
                                random_y = random.randint(-50, 15)                            
                                actions = ActionChains(driver)
                                actions.move_to_element_with_offset(canvas, random_x, random_y).click().perform()
                                valueWait = random.randint(2,9) /10
                                time.sleep(valueWait)
                except:pass           
            time.sleep(1)
        except Exception as e:
            print(f"Acc {tenProfile} Pain notpixel FAIL-saving info to file note !!!!")
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
            element = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="_container_1df7o_14"]//div[@class="_header_q0ezh_11"]/div[1]')))
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
            noteAccFail.write(f'{tenProfile}|{profile_id}|error multi\n')

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

        try:
            for i in range(0, 5000, self.numberDcom):
                print(f"Turn bắt đầu từ acc: {self.fileExcelLoad.iloc[i, 0]} and {self.fileExcelLoad.iloc[i, 2]}")
                run1_threads = []
                for p in range(self.numberDcom):
                    t1_run = threading.Thread(target=self.proxy_reset, args=(p,))
                    run1_threads.append(t1_run)
                    t1_run.start()
                for t1_run in run1_threads:
                    t1_run.join()

                print("Proxy reset xong, bắt đầu Quất acc...")
                idBeginturnacc = str(self.fileExcelLoad.iloc[i, 1])
                if len(idBeginturnacc) < 10:
                    print("Xong lô acc. Kết thúc.")
                    break

                run_threads = []
                for x in range(self.accPerTurn):
                    t_run = threading.Thread(target=self.run, args=(x, i))
                    run_threads.append(t_run)
                    t_run.start()
                for t_run in run_threads:
                    t_run.join()

                print(">> ĐÃ QUẤT XONG TURN ACC !!!")
                print("Đang vào chạy turn tiếp theo...")
                self.reset_all_ip()
                self.countdown(20)
        except Exception as e:
            print(f'Lỗi xảy ra trong khi chạy: {str(e)}')
        finally:print(f'Đã xong lô acc !!!')

    def countdown(self, seconds):
        for sec in range(seconds, 0, -1):
            print(f'Continue in {sec}s !')
            time.sleep(1)
    def reset_all_ip(self):
        print("Đang reset IP để chạy turn tiếp")
        requests.get(f"http://{dataLoad.proxyLink}:6868/reset_all")
        print("----Reset IP thành công, Vui lòng đợi 20s !------")

if __name__ == "__main__":
    manager = ProfileManager()
    manager.run_turn()
