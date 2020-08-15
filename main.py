import requests

API_TOKEN = "1349962959:AAEXec9Yf_H5C_DagKibiGTKk4SOl1QsHN8"
url = "https://api.telegram.org/bot%s/" % API_TOKEN


# Get chat id from update
def get_chat_id(update):
    return update["message"]["chat"]["id"]


# Get message from update
def get_message_text(update):
    return update["message"]["text"]


# Get last update
def last_update(req):
    response = requests.get(req + "getUpdates")
    response = response.json()
    result = response["result"]
    total_updates = len(result) - 1
    return result[total_updates]


# Send message
def send_message(chat_id, message):
    params = {"chat_id": chat_id, "text": message}
    response = requests.post(url + "sendMessage", data=params)
    return response


# Main function to navigate or reply messages
# TODO: if two messages came in before this could read the first one, it will be forgotten
def main():
    update_id = last_update(url)["update_id"]
    while True:
        update = last_update(url)
        if update_id == update["update_id"]:
            print("Received: ")
            print(get_message_text(update))
            if get_message_text(update).lower() == "/start":
                send_message(get_chat_id(update), "BOKITA EL MAS GRANDE, PAPA!!!")
            else:
                send_message(get_chat_id(update), "No entiendo vieja. Te fuiste a la B")
            update_id += 1


main()
