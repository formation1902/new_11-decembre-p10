#
#
#
from datatypes_date_time.timex import Timex
import json

from botbuilder.dialogs         import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core            import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog    import CancelAndHelpDialog
from .date_resolver_dialog      import DateResolverDialog,DateResolverDialogRetour

from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

class ReservationDialog(CancelAndHelpDialog):
    #
    #
    #
    nb = 0
    def __init__( self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        ReservationDialog.nb+=1
        print("INFO :[ ReservationDialog : Instantiated ] nb = ",ReservationDialog.nb)
        #        
        super(ReservationDialog, self).__init__( dialog_id or ReservationDialog.__name__, telemetry_client )
        self.telemetry_client        = telemetry_client
        text_prompt                  = TextPrompt(TextPrompt.__name__)
        confirm_prompt               = ConfirmPrompt(ConfirmPrompt.__name__)
        
        text_prompt.telemetry_client = telemetry_client
        confirm_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.fx_ville_depart_step,
                self.fx_ville_destination_step,
                self.fx_date_depart_step,
                self.fx_date_retour_step,
                self.fx_budget_step,
                self.fx_confirm_step,
                self.fx_final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(DateResolverDialogRetour(DateResolverDialogRetour.__name__, self.telemetry_client))
        self.add_dialog(waterfall_dialog)
        self.add_dialog(confirm_prompt)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def fx_ville_depart_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # print("\n\n\n--------> step_context == ",step_context.activity,"\n\n")::mentors is bullshit <je decouvre ce besoin le 18 decembre au detour d'une reflexion >
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # - prompt pour ville_depart si absente
        #
        if x.ville_depart is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your ville depart : ?")
                ),
            )

        return await step_context.next(x.ville_depart)
    
    async def fx_ville_destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel modif ou l'information d'origine (next<->result)
        #
        x.ville_depart = step_context.result
        
        #
        # - prompt pour ville_destination si absente
        #
        # x.ville_destination = step_context.ville_destination

        if x.ville_destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your ville destination : ?")
                ),
            )

        return await step_context.next(x.ville_destination)
    
    async def fx_date_depart_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.ville_destination = step_context.result

        #
        # - prompt pour la date depart si absente
        #
        if not x.date_depart or self.is_ambiguous( x.date_depart):
            print("INFO [RSERVATION_DIALOG - fx_date_depart_step ] 1..... date_depart exists : ", x.date_depart)
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, 
                x.date_depart
            )

        print("INFO [RSERVATION_DIALOG - fx_date_depart_step ] 2..... date_departdoes not exists : ", x.date_depart)
        return await step_context.next(x.date_depart)
    
    async def fx_date_retour_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.date_depart = step_context.result

        #
        # - prompt pour  la date retour si absente
        #
        if not x.date_retour or self.is_ambiguous( x.date_retour):
            return await step_context.begin_dialog(
                DateResolverDialogRetour.__name__, 
                x.date_retour
            )

        return await step_context.next(x.date_retour)
    
    async def fx_budget_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.date_retour = step_context.result

        #
        # - prompt  le budget si absent
        #
        if not x.budget:
            
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your budget : ?")
                ),
            )
        return await step_context.next(x.budget)

    async def fx_confirm_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        # ---> On finalise la collecte des donées utilisateurs : 
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.budget = step_context.result
        
        # ---> On demande confirmation de l'ensemble des données par l'utilisateurs:
        #
        #
        #
        user_gathered_resevation_details = x
        
        print("\n\n\n---------------------------------------\nINFO : [ReservationDialog - fx_confirm_step ] Demande confirmation a l'utilisateur : \n",json.dumps(x.__dict__,indent=4),"\n---------------------------------------\n\n\n")
        
        msg = (
            f"Please confirm, I have you traveling"
            f" from: { user_gathered_resevation_details.ville_depart }"
            f"   to: { user_gathered_resevation_details.ville_destination }"
            f" date_depart: { user_gathered_resevation_details.date_depart}"
            f" date_retour: { user_gathered_resevation_details.date_retour}"
            f" budget: { user_gathered_resevation_details.budget}"
        )

        #
        # Permettre à l'utilisateur de confimer ou non les informations collectées
        #
        return await step_context.prompt(
            ConfirmPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def fx_final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        #
        # Finaliser le turn : 
        #
        x = step_context.options
        confirmation = step_context.result

        print("type telemtry_client : ",type(self.telemetry_client))
        if confirmation:
            print("\n\n\n-------------> Good little chatbot\n\n\n")
            self.telemetry_client.track_trace("Good little chatbot...Your though has been validated by le client roi!",severity='INFO')
        else:
            print("\n\n\n-------------> Bad little chatbot\n\n\n")
            self.telemetry_client.track_trace("'Bad little chatbot...Your though hasn't been validated by le client roi! is it ?",severity='CRITICAL')
        
        self.telemetry_client.flush()
        return await step_context.end_dialog()    

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
