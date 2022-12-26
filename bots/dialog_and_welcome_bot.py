#
# Le bot principal : acceuil utilisateur
#
import json
import os.path
from typing import List

from botbuilder.dialogs import Dialog
from botbuilder.core    import TurnContext    
from botbuilder.core    import ConversationState, UserState
from botbuilder.core    import BotTelemetryClient

from botbuilder.schema import Activity 
from botbuilder.schema import Attachment
from botbuilder.schema import ChannelAccount


from p10bot_utils.activity_helper import create_activity_reply
from .dialog_bot import DialogBot


class DialogAndWelcomeBot(DialogBot):
    #
    # Bot acceuil des utilisateurs 
    #
    nb=0
    WELCOME_MESSAGE = "We are happy to assit you book your Flight !!!"
    def __init__(self,conversation_state: ConversationState,user_state: UserState,dialog: Dialog,telemetry_client: BotTelemetryClient,msaName='msaName-DialogAndWelcomeBot'):
        DialogAndWelcomeBot.nb+=1
        self.msaName = msaName + "_" + str(DialogAndWelcomeBot.nb)
        super(DialogAndWelcomeBot, self).__init__(conversation_state, user_state, dialog, telemetry_client)
        self.telemetry_client = telemetry_client
        self.already_sent = False
        print("INFO: [DialogAndWelcomeBot : instatiated] nb = ",DialogAndWelcomeBot.nb," name == ",self.msaName)
        print("INFO: [DialogAndWelcomeBot : DialogAndWelcomeBot.nb ] --> ",DialogAndWelcomeBot.nb)
        print("INFO: [DialogAndWelcomeBot : DialogBot.nb ] --> ",DialogBot.nb)
        
        
    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        print(" --> [ DialogAndWelcomeBot: call to  on_members_added_activity ]")
        for member in members_added:
            # Greet when users are added to the conversation.
            # To learn more about Adaptive Cards, see https://aka.ms/msbot-adaptivecards
            if member.id != turn_context.activity.recipient.id :
                print("\nINFO: [ DialogAndWelcomeBot - on_members_added_activity ] new member, member_id == ",member.id)
                
                welcome_card = self.create_adaptive_card_attachment()
                response = self.create_response(turn_context.activity, welcome_card)
                
                print("INFO: [ DialogAndWelcomeBot - on_members_added_activity ] 1. sending card to new member")
                await turn_context.send_activity(response)
                                
                print("INFO: [ DialogAndWelcomeBot - on_members_added_activity ] 2. sending welcome messages")
                await turn_context.send_activity(
                    f"Hi there { member.name }. " + DialogAndWelcomeBot.WELCOME_MESSAGE
                )
                print("INFO: [ DialogAndWelcomeBot - on_members_added_activity ] 3. greeting done")
                
                
                
    def create_response(self, activity: Activity, attachment: Attachment):
        print(" --> [ DialogAndWelcomeBot: call to  create_response ]")
        """Create an attachment message response."""
        response = create_activity_reply(activity)
        response.attachments = [attachment]
        return response

    # Load attachment from file.
    def create_adaptive_card_attachment(self):
        print(" --> [ DialogAndWelcomeBot: call to  create_adaptive_card_attachment ]")
        """Create an adaptive card."""
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "resources/p10Bot_greetingCard.json")
        with open(path) as card_file:
            card = json.load(card_file)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )
