import os
import maihem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from time import sleep
from datetime import datetime

CURRENT_TIMESTAMP = datetime.now()
DATE_YYYYMMDD = CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
TIME_HHMMSS = CURRENT_TIMESTAMP.strftime("%H:%M:%S")

os.environ['MAIHEM_API_KEY'] = 'maihem-20240320-cANx30AceO^LclbykXht78W7b3l{5n01'
MAIHEM_MAX_MESSAGES = 5

MAIHEM_TEST_PERSONAS_COUNT = 2
MAIHEM_TEST_CHATBOT_ROLE = "education tutor"
MAIHEM_TEST_INDUSTRY = "Education"
MAIHEM_TEST_TOPIC = "Secondary school"
MAIHEM_TEST_LANGUAGE = "English"
MAIHEM_TEST_NAME = f"[{DATE_YYYYMMDD}] SchoolAI - {MAIHEM_TEST_INDUSTRY} (Personas = {MAIHEM_TEST_PERSONAS_COUNT})"

MAIHEM_TEST_METRICS_CHATBOT = {
    "Empathy": "The chatbot was able to understand and empathize with the persona's feelings",
    "Politeness": "The chatbot used polite language and tone to communicate with the persona",
    "On topic": "The chatbot stayed on topic and anwered the persona's request",
    "Correct language": "The response of the chatbot was in the correct language"
}
MAIHEM_TEST_METRICS_PERSONA = {
    "Mood improvement": "The persona's mood improved",
    "Goal completion": "The goal of the persona was achieved",
    "Frustration avoidance": "The persona was not fustrated",
}

def initialize_maihem_test():
    maihem.create_test(
        test_name=MAIHEM_TEST_NAME,
        chatbot_role=MAIHEM_TEST_CHATBOT_ROLE,
        industry=MAIHEM_TEST_INDUSTRY,
        n=MAIHEM_TEST_PERSONAS_COUNT,
        topic=MAIHEM_TEST_TOPIC,
        language=MAIHEM_TEST_LANGUAGE
    )

def getMaihemResponse(test_run_name, persona_id, message):
    msg = maihem.chat_with_persona(
        test_name=MAIHEM_TEST_NAME, 
        test_run_name=test_run_name, 
        persona_id=persona_id,
        message=message
    )
    print("Persona response: " + msg)
    return msg

def remove_non_bmp_chars(text):
  return ''.join(c for c in text if ord(c) <= 0xFFFF)

def evaluate_results(test_run_name):
    df_eval = maihem.evaluate(
        test_name=MAIHEM_TEST_NAME, 
        test_run_name=test_run_name, 
        metrics_chatbot=MAIHEM_TEST_METRICS_CHATBOT, 
        metrics_persona=MAIHEM_TEST_METRICS_PERSONA
    )

def getSchoolAIResponse(driver):
    SCHOOLAI_RESPONSE_CSS_SELECTOR = "div.datadog-chat_assistant"  # Adjusted CSS selector
    response_elements = driver.find_elements(By.CSS_SELECTOR, SCHOOLAI_RESPONSE_CSS_SELECTOR)

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
        
        print("AI bot: " + msg_bot)
        return msg_bot.strip()

def send_message_to_schoolai(driver, msg):
    try:
        message_box = driver.find_element(By.CSS_SELECTOR, "#chat-input")
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
    except WebDriverException as e:
        print(e)

def schoolAIConversation(test_run_name, maihem_persona_id):

    conversation = []

    # INIITIALIZE SCHOOLAI ON SELENIUM
    SCHOOLAI_URL = "https://app.schoolai.com/space?code=UE8R"
    driver = webdriver.Chrome()
    driver.get(SCHOOLAI_URL)
    sleep(5)
    name = f"Persona {maihem_persona_id} | Test {MAIHEM_TEST_NAME} | Test Run {test_run_name}"
    name_input = driver.find_element(By.ID, "name-input")
    name_input.send_keys(name)
    name_input.send_keys(Keys.ENTER)
    sleep(5)

    while True:
        if len(conversation) == MAIHEM_MAX_MESSAGES:
            msg_bot = "END"
        else:
            msg_bot = getSchoolAIResponse(driver)
            sleep(5)

        conversation.append(msg_bot)
        msg_persona = getMaihemResponse(test_run_name, maihem_persona_id, msg_bot)
        # sleep(5)
        msg_persona_without_bmp = remove_non_bmp_chars(msg_persona)
        send_message_to_schoolai(driver, msg_persona_without_bmp)
        conversation.append(msg_persona)
        
        if msg_persona == "Maximum number of conversation turns reached":
            print("CONVERSATION COMPLETED: MAIHEM LIMIT REACHED")
            break
        if msg_bot == "END" or "The conversation has ended" in msg_bot:
            print("CONVERSATION COMPLETED: SCHOOLAI LIMIT REACHED")
            break

    driver.quit()
    return conversation

# INITIALIZE TEST (IF NOT ALREADY EXISTS)
try:
    initialize_maihem_test()
    print(f"NEW MAIHEM TEST PROFILE CREATED: {MAIHEM_TEST_NAME}")
except Exception as e:
    print(e)

# RUN TEST
MAIHEM_TEST_RUN_NAME = TIME_HHMMSS
for persona_id in range(MAIHEM_TEST_PERSONAS_COUNT):
    print(f">>>>>>MAIHEM PERSONA {persona_id} for MAIHEM TEST RUN {MAIHEM_TEST_RUN_NAME}<<<<<<")
    conversation = schoolAIConversation(MAIHEM_TEST_RUN_NAME, persona_id)

# for msg in conversation:
#   print(msg)

# EVALUATE TEST RUN
evaluate_results(MAIHEM_TEST_RUN_NAME)