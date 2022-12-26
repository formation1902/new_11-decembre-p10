#
#
#
from botbuilder.core import ActivityHandler
from botbuilder.core import ConversationState,    UserState
from botbuilder.core import TurnContext
from botbuilder.core import BotTelemetryClient,    NullTelemetryClient
from botbuilder.dialogs import Dialog, DialogExtensions
from p10bot_utils.dialog_helper import DialogHelper


class DialogBot(ActivityHandler):
    nb=0
    def __init__(self,conversation_state: ConversationState,  user_state: UserState, dialog: Dialog,telemetry_client: BotTelemetryClient,msaName="msaName-DialogBot-"):
        DialogBot.nb+=1
        #
        #   conversation_state : 
        #   user_state         :
        #   dialog             :
        #   telemetry_client   :
        #
        if conversation_state is None:
            raise Exception("[DialogBot]: Missing parameter. conversation_state is required")
        
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state         = user_state
        self.dialog             = dialog
        self.telemetry_client   = telemetry_client
        
        self.msaName = msaName + "_" + str(DialogBot.nb)
        print("INFO: [DialogBot : instatiated] nb = ",DialogBot.nb, " name == ",self.msaName)
        print("INFO: [DialogBot : DialogBot.nb ] --> ",DialogBot.nb)

    async def on_message_activity(self, turn_context: TurnContext):
        print('[DialogBot : on_message_activity ] turn_context : ',turn_context)
        #
        #
        #
        print("\nINFO: [DialogBot - on_message_activity ] 1.1 - DialogExtensions.run_dialog ............... \n\t - turn_context.activity == ",turn_context.activity)
        
        await DialogExtensions.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState")
        )
        
        
        print("\nINFO: [DialogBot - on_message_activity ] 1.2 - after run_dialog ............. \n\t - turn_context.activity == ",turn_context.activity)

        # Save any state changes that might have occured during the turn.
        #
        #
        #
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)
        print("\nINFO: [DialogBot - on_message_activity ] 2. Converstation and user states saved\n\t - turn_context.activity == ",turn_context.activity)

    @property
    def telemetry_client(self) -> BotTelemetryClient:
        """
        Gets the telemetry client for logging events.
        """
        return self._telemetry_client

    
    @telemetry_client.setter
    def telemetry_client(self, value: BotTelemetryClient) -> None:
        """
        Sets the telemetry client for logging events.
        """
        if value is None:
            self._telemetry_client = NullTelemetryClient()
        else:
            self._telemetry_client = value
