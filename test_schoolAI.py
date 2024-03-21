import os
import maihem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep, time

os.environ['MAIHEM_API_KEY'] = 'maihem-20240320-cANx30AceO^LclbykXht78W7b3l{5n01'
MAX_MESSAGES = 20
MAIHEM_TEST_ID = str(time())

def initialize_maihem_test(test_name, chatbot_role, industry, n, topic, language):
    maihem.create_test(
        test_name=test_name,
        chatbot_role=chatbot_role,
        industry=industry,
        n=n,
        topic=topic,
        language=language
    ) 

def getMaihemResponse(test_name, test_run_name, persona_id, message):
    msg = maihem.chat_with_persona(
        test_name=test_name, 
        test_run_name=test_run_name, 
        persona_id=persona_id,
        message=message
    )
    print("Persona response: " + msg)
    return msg

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

def schoolAIConversation():

    conversation = []

    # INIITIALIZE SCHOOLAI ON SELENIUM
    SCHOOLAI_URL = "https://app.schoolai.com/space?code=WZ5U"
    driver = webdriver.Chrome()
    driver.get(SCHOOLAI_URL)
    sleep(7)

    while len(conversation) < MAX_MESSAGES:
        sleep(3)

        msg_bot = getSchoolAIResponse(driver)
        conversation.append(msg_bot)
        msg_persona = getMaihemResponse(MAIHEM_TEST_ID, "test_run_1", 0, msg_bot)
        send_message_to_schoolai(driver, msg_persona)
 
        if msg_persona == "Maximum number of conversation turns reached":
            print("CONVERSATION COMPLETED: MAIHEM LIMIT REACHED")
            break

        if msg_bot == "END" or "The conversation has ended" in msg_bot:
            print("CONVERSATION COMPLETED: SCHOOLAI LIMIT REACHED")
            break

    driver.quit()
    return conversation

initialize_maihem_test(MAIHEM_TEST_ID, "education tutor", "Education", 5, "Secondary school","English")
conversation = schoolAIConversation()

# for msg in conversation:
#   print(msg)