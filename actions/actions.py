from typing import Any, Text, Dict, List
import json
from datetime import datetime, timedelta
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSayDeliveryTime(Action):
    def name(self) -> str:
        return "action_say_delivery_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        delivery_time = tracker.get_slot("")
        dispatcher.utter_message(text=f"Our menu:\n{menu_items}")


class ExtractFood(Action):

    def name(self) -> Text:
        return "action_extract_food"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the food entity from the tracker
        food_entity = next(tracker.get_latest_entity_values('food'), None)

        if food_entity:
            # Extract the full message text
            user_message = tracker.latest_message.get('text', '').lower()

            # Detect "with" and "without" in the user's message
            if "without" in user_message:
                modifier_start = user_message.find("without") + len("without")
                modifier = user_message[modifier_start:].strip()

                dispatcher.utter_message(text=f"You have selected {food_entity} without {modifier}.")
            elif "with" in user_message:
                modifier_start = user_message.find("with") + len("with")
                modifier = user_message[modifier_start:].strip()

                dispatcher.utter_message(text=f"You have selected {food_entity} with {modifier}.")
            else:
                # Load the menu from a JSON file
                try:
                    with open("data/menu.json") as f:
                        menu = json.load(f)["items"]
                except FileNotFoundError:
                    dispatcher.utter_message(text="Menu data is unavailable at the moment. Please try again later.")
                    return []

                # Check if the selected food is in the menu
                item = next((item for item in menu if item["name"].lower() == food_entity.lower()), None)

                if item:
                    # If the food item is in the menu, ask for confirmation
                    dispatcher.utter_message(text=f"You have selected {food_entity}. "
                                                  "Do you want to pick up at a restaurant or have it delivered to you?")
                else:
                    # If the food item is not in the menu
                    dispatcher.utter_message(text=f"I'm sorry, {food_entity} is not on our menu.")
        else:
            dispatcher.utter_message(text="I am sorry, I could not detect the food choice.")

        return []


class ActionCheckOpeningHours(Action):
    def name(self) -> str:
        return "action_check_opening_hours"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        day = next(tracker.get_latest_entity_values('day'), None)
        time = next(tracker.get_latest_entity_values('time'), None)
        # day = tracker.get_slot("day")
        # time = tracker.get_slot("time")

        with open("data/opening_hours.json") as f:
            hours = json.load(f)["items"]

        if day in hours:
            open_time = hours[day]["open"]
            close_time = hours[day]["close"]
            if time:
                hour = int(datetime.strptime(time, "%I %p").hour)
                if open_time <= hour < close_time:
                    dispatcher.utter_message(text=f"Yes, we're open at {time} on {day}.")
                else:
                    dispatcher.utter_message(text=f"Sorry, we're closed at {time} on {day}.")
            else:
                dispatcher.utter_message(text=f"We're open from {open_time} to {close_time} on {day}.")
        else:
            dispatcher.utter_message(text="Sorry, I don't have the hours for that day.")


class ActionDisplayOpeningHours(Action):
    def name(self) -> str:
        return "action_display_opening_hours"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Load opening hours data from file
        try:
            with open("data/opening_hours.json") as f:
                opening_hours = json.load(f)["items"]
        except FileNotFoundError:
            dispatcher.utter_message(text="Opening hours data is unavailable at the moment. Please try again later.")
            return []

        # Extract day and time from tracker
        day = next(tracker.get_latest_entity_values('day'), None)
        time = next(tracker.get_latest_entity_values('time'), None)

        if not day or not time:
            dispatcher.utter_message(text="Please provide both the day and the time to check opening hours.")
            return []

        # Standardize day input to match the JSON keys
        day = day.capitalize()

        if day not in opening_hours:
            dispatcher.utter_message(text=f"Sorry, I don't have opening hours information for {day}.")
            return []

        try:
            # Parse the input time
            input_time = datetime.strptime(time, "%I %p").time()
        except ValueError:
            dispatcher.utter_message(
                text="The time format is incorrect. Please provide the time in the format '10 AM' or '3 PM'.")
            return []

        # Get opening and closing times for the specified day
        times = opening_hours[day]
        open_time = datetime.strptime(f"{times['open']}:00", "%H:%M").time()
        close_time = datetime.strptime(f"{times['close']}:00", "%H:%M").time()

        if times['open'] == 0 and times['close'] == 0:
            dispatcher.utter_message(text=f"No, on {day} we are closed.")
            return []

        # Check if the input time falls within the opening hours
        if open_time <= input_time < close_time:
            dispatcher.utter_message(text=f"Yes, at {time} on {day} we are open.")
        else:
            open_hour = f"{open_time.strftime('%I:%M %p')}"
            close_hour = f"{close_time.strftime('%I:%M %p')}"
            dispatcher.utter_message(text=f"No, on {day} we are open from {open_hour} to {close_hour}.")

        return []


class ActionListMenu(Action):
    def name(self) -> str:
        return "action_list_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        with open("data/menu.json") as f:
            menu = json.load(f)["items"]

        menu_items = "\n".join([f"{item['name']} - ${item['price']}" for item in menu])
        dispatcher.utter_message(text=f"Our menu:\n{menu_items}")


class ActionPlaceOrder(Action):
    def name(self) -> str:
        return "action_place_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Retrieve slots safely
        food_item = tracker.get_slot("food_item")
        additional_request = tracker.get_slot("additional_request")

        # Check if food_item slot has a value
        if not food_item:
            dispatcher.utter_message(text="I didn't catch what you wanted to order.")
            return []

        # Load menu data from file
        try:
            with open("data/menu.json") as f:
                menu = json.load(f)["items"]
        except FileNotFoundError:
            dispatcher.utter_message(text="Menu data is unavailable at the moment. Please try again later.")
            return []

        # Find item in menu, handling case-insensitive comparison
        item = next((item for item in menu if item["name"].lower() == food_item.lower()), None)

        # Respond based on whether item was found in the menu
        if item:
            preparation_time = item["preparation_time"]
            dispatcher.utter_message(
                text=f"Order confirmed: {food_item} {additional_request or ''}. It will be ready in {preparation_time} hours."
            )
        else:
            dispatcher.utter_message(text=f"{food_item} is not on our menu, but we'll try to accommodate your request.")

        return []


class ActionShowDeliveryTime(Action):
    def name(self) -> str:
        return "action_show_delivery_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Retrieve the address from the slot
        address = tracker.get_slot("address")
        food_item = tracker.get_slot("food")  # Retaining this for context

        # Check if the address is provided
        if not address:
            dispatcher.utter_message(text="Please provide your delivery address.")
            return []

        # Calculate courier's departure time
        current_time = datetime.now()
        courier_departure_time = current_time + timedelta(minutes=15)  # Example: Courier departs in 15 minutes

        # Format the time for user-friendly display
        formatted_time = courier_departure_time.strftime("%I:%M %p")

        # Generate the response message
        message = (
            f"Your dish '{food_item}' will be delivered to '{address}'. "
            f"The courier will depart at {formatted_time}."
        )

        dispatcher.utter_message(text=message)
