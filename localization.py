import logging

translations = {
    'en': {
        'welcome_message': "Hi, we are still a little bit away from the release of SCAM$, stay tuned to our Telegram "
                           "channel for the latest news."
    },
    'ru': {
        'welcome_message': "Привет, еще немного до релиза SCAM$, следите за нашим Telegram-каналом для последних "
                           "новостей."
    }
}


def get_translation(language, key):
    translation = translations.get(language, translations['en']).get(key, key)
    logging.info(f"Translation for language '{language}' and key '{key}': {translation}")
    return translation
