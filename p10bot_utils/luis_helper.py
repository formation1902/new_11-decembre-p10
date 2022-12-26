#
#
#
from enum import Enum
from typing import Dict
import json

from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from ReservationDetails import ReservationDetails


class Intent(Enum):
    BOOK_FLIGHT = "intention_reserver_un_billet_d_avion"
    CANCEL = "Cancel"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    
    @staticmethod
    async def execute_luis_query(luis_recognizer: LuisRecognizer, turn_context: TurnContext) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        #
        # Retourne les resultat de l'app LUIS preformattée en destination des objets dialogs du bot
        #
        result = None
        intent = None

        # try:
        print("INFO : [LuisHelper - execute_luis_query] 1...... turn_context = ",turn_context)
        recognizer_result = await luis_recognizer.recognize(turn_context)

        print("INFO : [LuisHelper - execute_luis_query] 2...... recognizer_result = ",recognizer_result)
        intent = sorted(recognizer_result.intents,key=recognizer_result.intents.get,reverse=True)[:1][0] if recognizer_result.intents  else None

        print("\t --> INFO : [LuisHelper - execute_luis_query] manual check")
        print("\t\t ----> [LuisHelper - execute_luis_query] intent returned by luis = ",intent)
        print("\t\t ----> [LuisHelper - execute_luis_query] intent attendu = ",Intent.BOOK_FLIGHT.value)
        
        if intent == Intent.BOOK_FLIGHT.value:
            print("INFO : [LuisHelper - execute_luis_query] 3...... intention correctement reconnu =  ",intent)
            #
            # On instancie un object vide
            #
            result = ReservationDetails()

            # We need to get the result from the LUIS JSON which at every level returns an array.

            #--------------------------------------------------------------------------------------------------------------
            print("############ ville depart : ")
            ville_depart_entities = recognizer_result.entities.get("$instance", {}).get("ville_depart", [])
            print("---> ville_depart_entities : ", ville_depart_entities)
            if len(ville_depart_entities) > 0:
                print("A..... : ",recognizer_result.entities.get("ville_depart",[{"$instance": {}}] ))
                print("\nB........ : ",recognizer_result.entities.get("ville_depart",[{"$instance": {}}] )[0])
                if recognizer_result.entities.get("ville_depart",[{"$instance": {}}] )[0]:
                    print("===>=====>====> ",ville_depart_entities[0]["text"])
                    result.ville_depart = ville_depart_entities[0]["text"].capitalize()
            print("Finally : ville_depart == ",result.ville_depart)
            
            #--------------------------------------------------------------------------------------------------------------
            print("############ ville destination : ")
            ville_destination_entities = recognizer_result.entities.get("$instance", {}).get("ville_destination", [])
            if len(ville_destination_entities) > 0:
                if recognizer_result.entities.get("ville_destination", [{"$instance": {}}])[0]:
                    result.ville_destination = ville_destination_entities[0]["text"].capitalize()

            print("Finally : ville_destination == ",result.ville_destination)
            
            #--------------------------------------------------------------------------------------------------------------
            print("############ date_depart : ")
            # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
            # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
            # e.g. missing a Year.
            date_depart_entities = recognizer_result.entities.get("date_depart", [])
            print("---> date_depart_entities : ",date_depart_entities)
            if date_depart_entities:
                timex = date_depart_entities[0]["timex"]

                if timex:
                    datetime = timex[0].split("T")[0]

                    result.date_depart = datetime
            else:
                result.date_depart = None

            #--------------------------------------------------------------------------------------------------------------
            print("############ date_retour : ")
            # date_retour_entities = recognizer_result.entities.get("date_retour", [])
            # if date_retour_entities:
            #     timex = date_retour_entities[0]["timex"]

            #     if timex:
            #         datetime = timex[0].split("T")[0]

            #         result.date_retour = datetime
            # else:
            #     result.date_retour = None
            
            #--------------------------------------------------------------------------------------------------------------
            print("############ budget : ")
            budget_entities = recognizer_result.entities.get("$instance", {}).get("budget", [])
            print("---> budget_entities : ", budget_entities)
            if len(budget_entities) > 0:
                result.budget = budget_entities[0]["text"]
            print("Finally : budget == ",result.budget)
        # except Exception as exception:
        #     print("We got a problem! Error during execute luis_query routine. \nmore details ? : ", exception)

        print("\n================ 3................... : ",intent)
        print("\n================ 4................... : ",json.dumps(result.__dict__))

        return intent, result
