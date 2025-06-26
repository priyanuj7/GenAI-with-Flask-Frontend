from flask import Flask, redirect, url_for, render_template, request
from functions import *

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)



conversation = initialize_conversation()
introduction = get_chat_completions(conversation)
top_3_laptops = None

conversation_bot = []
conversation_bot.append({'bot': introduction})


@app.route("/")
def default_func():
    global conversation_bot, conversation, top_3_laptops
    return render_template("index_invite.html", name=conversation_bot)

# @app.route("/hello/<name>")
# def hello(name):
#     # return f"<html>  <body> <h1>Hello {name}, you are invited to the event, </h1></body></html>"
#     return render_template("index_hello.html", name = name)


# @app.route("/bye/<name>")
# def bye(name):
#     # return f"<html><body><h1>Sorry {name}, you're not invited to the event.</h1></body></html>"
#     return render_template("index_bye.html", name = name)

@app.route("/end_conv", methods = ['POST'])
def end_conv():
    global conversation_bot, conversation, top_3_laptops
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_completions(conversation)
    conversation_bot.append({'bot': introduction})
    top_3_laptops = None
    return redirect(url_for("default_func"))


#Decorator is nothing but a wrapper around a function
# @app.route("/invite/<name>") - not required now as we are taking through html url
@app.route("/invite", methods = ['POST'])
def invite():
    global conversation_bot, conversation, top_3_laptops, conversation_reco
    user_input = request.form["user_input_messages"]
    

    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        display("Sorry, this message has been flagged. Please restart your conversation.")
        

    if top_3_laptops is None:

        conversation.append({"role": "user", "content": user_input})
        conversation_bot.append({'user': user_input})

        response_assistant = get_chat_completions(conversation)
        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            display("Sorry, this message has been flagged. Please restart your conversation.")
            


        confirmation = intent_confirmation_layer(response_assistant)

        print("Intent Confirmation Yes/No:",confirmation.get('result'))

        if "No" in confirmation.get('result'):
            conversation.append({"role": "assistant", "content": str(response_assistant)})
            conversation_bot.append({'bot': response_assistant})
            print("\n" + str(response_assistant) + "\n")

        else:
            print("\n" + str(response_assistant) + "\n")
            print('\n' + "Variables extracted!" + '\n')

            response = dictionary_present(response_assistant)

            print("Thank you for providing all the information. Kindly wait, while I fetch the products: \n")
            conversation_bot.append({'bot': "Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
            top_3_laptops = compare_laptops_with_user(response)

            print("top 3 laptops are", top_3_laptops)

            validated_reco = recommendation_validation(top_3_laptops)

            conversation_reco = initialize_conv_reco(validated_reco)

            conversation_reco.append({"role": "user", "content": "This is my user profile" + str(response)})
            

            recommendation = get_chat_completions(conversation_reco)

            moderation = moderation_check(recommendation)
            if moderation == 'Flagged':
                display("Sorry, this message has been flagged. Please restart your conversation.")
                

            conversation_reco.append({"role": "assistant", "content": str(recommendation)})
            conversation_bot.append({'bot': str(recommendation)})
            print(str(recommendation) + '\n')
    else:
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user': user_input})

        response_asst_reco = get_chat_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            print("Sorry, this message has been flagged. Please restart your conversation.")
            

        print('\n' + response_asst_reco + '\n')
        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({'bot': response_asst_reco})
    
    return redirect(url_for('default_func'))


if __name__ == '__main__':
    app.run(debug=True)