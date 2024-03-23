import os
import maihem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime

os.environ['MAIHEM_API_KEY'] = 'maihem-20240320-cANx30AceO^LclbykXht78W7b3l{5n01'
MAIHEM_MAX_MESSAGES = 20

MAIHEM_TEST_NAME = "Education Bot Test - SchoolAI"
MAIHEM_TEST_CHATBOT_ROLE = "education tutor"
MAIHEM_TEST_INDUSTRY = "Education"
MAIHEM_TEST_PERSONAS_COUNT = 5
MAIHEM_TEST_TOPIC = "Secondary school"
MAIHEM_TEST_LANGUAGE = "English"

def initialize_maihem_test():
    maihem.create_test(
        test_name=MAIHEM_TEST_NAME,
        chatbot_role=MAIHEM_TEST_CHATBOT_ROLE,
        industry=MAIHEM_TEST_INDUSTRY,
        n=MAIHEM_TEST_PERSONAS_COUNT,
        topic=MAIHEM_TEST_TOPIC,
        language=MAIHEM_TEST_LANGUAGE
    ) 

def getMaihemResponse(persona_id, message):
    msg = maihem.chat_with_persona(
        test_name=MAIHEM_TEST_NAME, 
        test_run_name=MAIHEM_TEST_RUN_NAME, 
        persona_id=persona_id,
        message=message
    )
    print("Persona response: " + msg)
    return msg

def remove_non_bmp_chars(text):
  return ''.join(c for c in text if ord(c) <= 0xFFFF)

def getSchoolAIResponse(driver):
    sleep(3)

    SCHOOLAI_RESPONSE_CSS_SELECTOR = "div.dark\:text-white p"
    response_element = driver.find_element(By.CSS_SELECTOR, SCHOOLAI_RESPONSE_CSS_SELECTOR)

    message = ""
    for child in response_element.find_elements(By.TAG_NAME, "p"):
        message += child.text.strip() + "\n"

    msg_bot_temp = message.strip()
    print("AI bot: " + msg_bot_temp)
    return msg_bot_temp

def send_message_to_schoolai(driver, msg):
    try:
        message_box = driver.find_element(By.CSS_SELECTOR, "#chat-input")
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
    except WebDriverException as e:
        print(e)

def schoolAIConversation(MAIHEM_PERSONA_ID):

    conversation = []

    # INIITIALIZE SCHOOLAI ON SELENIUM
    SCHOOLAI_URL = "https://app.schoolai.com/space?code=WZ5U"
    driver = webdriver.Chrome()
    driver.get(SCHOOLAI_URL)
    sleep(7)

    while len(conversation) < MAIHEM_MAX_MESSAGES:
        msg_bot = getSchoolAIResponse(driver)
        conversation.append(msg_bot)
        msg_persona = getMaihemResponse(MAIHEM_PERSONA_ID, msg_bot)
        msg_persona_without_bmp = remove_non_bmp_chars(msg_persona)
        send_message_to_schoolai(driver, msg_persona_without_bmp)
        
        if msg_persona == "Maximum number of conversation turns reached":
            print("CONVERSATION COMPLETED: MAIHEM LIMIT REACHED")
            break
        if msg_bot == "END" or "The conversation has ended" in msg_bot:
            print("CONVERSATION COMPLETED: SCHOOLAI LIMIT REACHED")
            break

        sleep(3)

    driver.quit()
    return conversation

# initialize_maihem_test()
MAIHEM_TEST_RUN_NAME = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
for persona_id in range(MAIHEM_TEST_PERSONAS_COUNT):
    print(">>>>>>SWITCHING MAIHEM PERSONA<<<<<<")
    conversation = schoolAIConversation(persona_id)

# for msg in conversation:
#   print(msg)