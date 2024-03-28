from selenium import webdriver
from selenium.webdriver.common.by import By

def extract_bot_msg_schoolai(driver):
    response_elements = driver.find_elements(By.CSS_SELECTOR, "div.datadog-chat_assistant")

    if response_elements:
        latest_response_element = response_elements[-1]
        paragraphs = latest_response_element.find_elements(By.TAG_NAME, "p")
        ordered_lists = latest_response_element.find_elements(By.CSS_SELECTOR, "ol.list-decimal")
        unordered_lists = latest_response_element.find_elements(By.CSS_SELECTOR, "ul.list-disc")
        
        msg_bot = ""
        
        for paragraph in paragraphs:
            msg_bot += paragraph.text.strip() + "\n"

        for ordered_list in ordered_lists:
            list_items = ordered_list.find_elements(By.TAG_NAME, "li")
            for item in list_items:
                msg_bot += "• " + item.text.strip() + "\n"
        
        for unordered_list in unordered_lists:
            list_items = unordered_list.find_elements(By.TAG_NAME, "li")
            for item in list_items:
                msg_bot += "• " + item.text.strip() + "\n"

        return msg_bot.strip()
    
def extract_bot_msg_dhl(driver):
    bot_msgs = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='chat-response']")

    # for response_element in bot_msgs:
    #     paragraphs = response_element.find_elements(By.TAG_NAME, "p")
    #     for paragraph in paragraphs:
    #         print(paragraph.text.strip() + "\n")

    latest_response_element = bot_msgs[len(bot_msgs) - 1]
    paragraphs = latest_response_element.find_elements(By.TAG_NAME, "p")
    
    msg_bot = ""
    for paragraph in paragraphs:
        msg_bot += paragraph.text.strip() + "\n"

    return msg_bot.strip()

def get_msg_extractor_function(selector):
    if(selector == "schoolai"):
        return extract_bot_msg_schoolai
    if(selector == "dhl"):
        return extract_bot_msg_dhl
    else:
        raise Exception("INVALID_COMPANY_NAME")