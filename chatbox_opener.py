from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep

def open_chatbox_schoolai(driver):
    name = f"Persona {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    name_input = driver.find_element(By.ID, "name-input")
    name_input.send_keys(name)
    name_input.send_keys(Keys.ENTER)

def open_chatbox_dhl(driver):
    button1 = driver.find_element(By.CSS_SELECTOR, ".buttonsWrapper")
    button1.click()
    sleep(4)
    button2 = driver.find_element(By.CSS_SELECTOR, "[data-test-id='start-button']")
    button2.click()

def get_open_chatbox_function(selector):
    if(selector == "schoolai"):
        return open_chatbox_schoolai
    if(selector == "dhl"):
        return open_chatbox_dhl
    else:
        raise Exception("INVALID_COMPANY_NAME")