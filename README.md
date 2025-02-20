# Rasa Restaurant Chatbot

## 📋 Project Overview
The **Rasa Restaurant Chatbot** is designed to handle customer interactions for a restaurant. It provides users with essential information and enables them to place food orders through natural language conversations. The chatbot is built using **Rasa** and is integrated with **Facebook Messenger** for real-time customer engagement.

## 🎯 Features
- **Check Opening Hours:** Responds to customer inquiries about whether the restaurant is open on a specific date and time.
- **Menu Listing:** Lists available menu items from a configurable file.
- **Order Placement:** Processes customer orders, and provides order confirmation.
- **Intent Recognition:** Handles at least three different phrasings for each intent (opening hours, menu listing, and order placement).
- **Dynamic Configuration:** Opening hours and menu items are fetched from a configuration file.
- **Messenger Integration:** Fully integrated with **Facebook Messenger** with a dedicated page.

## 🚀 Getting Started

### Prerequisites
- Python 3
- Rasa
- Ngrok
- Facebook Developer Account

### Running the Chatbot on Messenger
1. **Open 3 terminal windows.**

2. **In the first terminal, start Rasa actions server:**
   ```bash
   rasa run actions
   ```
3. **In the second terminal, start ngrok to expose the Rasa server:**
   ```bash
   ngrok http 5005
   ```
   - Copy the generated ngrok URL
   - In your Facebook Developer Console, go to your app settings.
   - Under Webhooks, set the Callback URL as:
   ```bash
   <ngrok-url>/webhooks/facebook/webhook
   ```
   - Set Verify Token to
   ```bash
   chatbot
   ```
4. **In the third terminal, run the Rasa server:**
   ```bash
   rasa run
   ```
### Running the Chatbot in Console
1. **Open 2 terminal windows.**

2. **In the first terminal, start Rasa actions server:**
   ```bash
   rasa run actions
   ```
3. **In the second terminal, run the chatbot in console mode:**
   ```bash
   rasa shell
   ```
