import os
import maihem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from time import sleep
from datetime import datetime
from bot_message_extractor import get_msg_extractor_function
import json
import sys

bot_company = sys.argv[1]
with open(f'configs/config-{bot_company}.json', 'r') as config_file:
  bot_config = json.load(config_file)

with open('config-maihem.json', 'r') as config_file:
  maihem_config = json.load(config_file)

MAIHEM_MAX_MESSAGES = int(maihem_config["MAIHEM_MAX_MESSAGES"])
MAIHEM_TEST_PERSONAS_COUNT = int(maihem_config["MAIHEM_TEST_PERSONAS_COUNT"])
MAIHEM_TEST_METRICS_CHATBOT = maihem_config["MAIHEM_TEST_METRICS_CHATBOT"]
MAIHEM_TEST_METRICS_PERSONA = maihem_config["MAIHEM_TEST_METRICS_PERSONA"]

MAIHEM_TEST_CHATBOT_ROLE = bot_config["MAIHEM_TEST_CHATBOT_ROLE"]
MAIHEM_TEST_INDUSTRY = bot_config["MAIHEM_TEST_INDUSTRY"]
MAIHEM_TEST_TOPIC = bot_config["MAIHEM_TEST_TOPIC"]
MAIHEM_TEST_LANGUAGE = bot_config["MAIHEM_TEST_LANGUAGE"]
BOT_URL = bot_config["BOT_URL"]
CSS_SELECTOR_MESSAGE_TB = bot_config["CSS_SELECTOR_MESSAGE_TB"]

CURRENT_TIMESTAMP = datetime.now()
DATE_YYYYMMDD = CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
TIME_HHMMSS = CURRENT_TIMESTAMP.strftime("%H:%M:%S")
MAIHEM_TEST_NAME = f"[{DATE_YYYYMMDD}] {bot_company} - {MAIHEM_TEST_INDUSTRY} (Personas = {MAIHEM_TEST_PERSONAS_COUNT})"
MAIHEM_TEST_RUN_NAME = TIME_HHMMSS

def initialize_maihem_test():
    maihem.create_test(
        test_name=MAIHEM_TEST_NAME,
        chatbot_role=MAIHEM_TEST_CHATBOT_ROLE,
        industry=MAIHEM_TEST_INDUSTRY,
        n=MAIHEM_TEST_PERSONAS_COUNT,
        topic=MAIHEM_TEST_TOPIC,
        language=MAIHEM_TEST_LANGUAGE
    )

def get_maihem_response(persona_id, message):
    msg = maihem.chat_with_persona(
        test_name=MAIHEM_TEST_NAME, 
        test_run_name=MAIHEM_TEST_RUN_NAME, 
        persona_id=persona_id,
        message=message
    )
    return msg

def remove_non_bmp_chars(text):
  return ''.join(c for c in text if ord(c) <= 0xFFFF)

def evaluate_results():
    df_eval = maihem.evaluate(
        test_name=MAIHEM_TEST_NAME, 
        test_run_name=MAIHEM_TEST_RUN_NAME, 
        metrics_chatbot=MAIHEM_TEST_METRICS_CHATBOT, 
        metrics_persona=MAIHEM_TEST_METRICS_PERSONA
    )

def send_message_to_bot(driver, msg):
    try:
        message_box = driver.find_element(By.CSS_SELECTOR, CSS_SELECTOR_MESSAGE_TB)
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
    except WebDriverException as e:
        print(e)

extract_bot_msg = None
try:
    extract_bot_msg = get_msg_extractor_function(bot_company)
except Exception as e:
    print(e)

def start_conversation(maihem_persona_id):

    conversation = []

    # INIITIALIZE SELENIUM
    driver = webdriver.Chrome()
    driver.get(BOT_URL)
    sleep(7)

    while True:
        msg_bot = ""
        if len(conversation) > MAIHEM_MAX_MESSAGES:
            msg_bot = "END"
        else:
            msg_bot = extract_bot_msg(driver)
            # sleep(5)
        print(f"AI bot: {msg_bot}")

        conversation.append(msg_bot)
        msg_persona = get_maihem_response(maihem_persona_id, msg_bot)
        print(f"Persona response: {msg_persona}")
        # sleep(5)
        msg_persona_without_bmp = remove_non_bmp_chars(msg_persona)
        send_message_to_bot(driver, msg_persona_without_bmp)
        # sleep(5)
        conversation.append(msg_persona)
        
        if msg_persona == "Maximum number of conversation turns reached":
            print("CONVERSATION COMPLETED: MAIHEM LIMIT REACHED")
            break
        if msg_bot == "END" or "The conversation has ended" in msg_bot:
            print("CONVERSATION COMPLETED: BOT LIMIT REACHED")
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
for persona_id in range(MAIHEM_TEST_PERSONAS_COUNT):
    print(f">>>>>>MAIHEM PERSONA {persona_id} for MAIHEM TEST RUN {MAIHEM_TEST_RUN_NAME}<<<<<<")
    conversation = start_conversation(persona_id)

# for msg in conversation:
#   print(msg)

# EVALUATE TEST RUN
evaluate_results()