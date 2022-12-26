from botbuilder.core    import BotFrameworkAdapterSettings
from botbuilder.core    import ConversationState,    MemoryStorage,    UserState
from botbuilder.core    import TelemetryLoggerMiddleware
#
from botbuilder.schema  import Activity
#
from botbuilder.applicationinsights                     import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import AiohttpTelemetryProcessor
#
from dialogs  import MainDialog, ReservationDialog
from bots     import DialogAndWelcomeBot,DialogBot
from adapter_with_error_handler            import AdapterWithErrorHandler
from Reserver_un_billet_d_avion_Recognizer import Reserver_un_billet_d_avion_Recognizer
from config import Bot_luis_app_and_insights_configuration
#
from http import HTTPStatus
from aiohttp        import web as aiohttp_web
from aiohttp.web    import Request, Response, json_response
#

#######################################################
# Creation de l'adaptateur :
#   - lecture de la configuration
#   - creation des espaces memoires
#   - configuration et activation de la telemetrie
#######################################################
# ----> Lecture de la configuration : 
CONFIG      = Bot_luis_app_and_insights_configuration()
Adapter_SETTINGS    = BotFrameworkAdapterSettings(CONFIG.APP_ID)#, CONFIG.APP_PASSWORD)

# ---> Espace temporaire
MEMORY              = MemoryStorage()
USER_STATE          = UserState(MEMORY)
CONVERSATION_STATE  = ConversationState(MEMORY)

# ---> Telemetrie appinsights
#
# Create telemetry client. Note the small 'client_queue_size'.  This is for demonstration purposes.  
# Larger queue sizes result in fewer calls to ApplicationInsights, improving bot performance at the expense of less frequent updates.

INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY


TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    INSTRUMENTATION_KEY, 
    telemetry_processor=AiohttpTelemetryProcessor(), 
    client_queue_size=10
)
TELEMETRY_CLIENT.track_trace("Starting the chatbot...",severity='INFO')

# ---> Logging :  Code for enabling activity and personal information logging.
TELEMETRY_LOGGER_MIDDLEWARE = TelemetryLoggerMiddleware(telemetry_client=TELEMETRY_CLIENT, log_personal_information=True)

#######################################################
# - creation de l'adapter
# Creation des dialogs et du bot
# 
#######################################################

# ---> Definition de l'adaptateur : 


ADAPTER = AdapterWithErrorHandler(Adapter_SETTINGS, CONVERSATION_STATE)
ADAPTER.use(TELEMETRY_LOGGER_MIDDLEWARE)




print("L'adaptateur : ",dir(ADAPTER),"\n\n")
RECOGNIZER          = Reserver_un_billet_d_avion_Recognizer(CONFIG)
Reservation_DIALOG  = ReservationDialog()
DIALOG          = MainDialog(RECOGNIZER, Reservation_DIALOG, telemetry_client=TELEMETRY_CLIENT)
BOT             = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG, TELEMETRY_CLIENT)


#
async def fx_handle_new_user_message_to_bot_api(req: Request) -> Response:
    # 
    # On n accepte que de JSON
    #
    
    print("----> [App - fx_handle_new_user_message_to_bot_api : Handling new user message ]")
    print("\t ----> [App - fx_handle_new_user_message_to_bot_api : 1. receiving user text ]")
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
        print("\t----> [App - fx_handle_new_user_message_to_bot_api ] received request :  ",body)
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    #
    # Ce qui est recu est transformée en un nouveau objet Activity incluant  the authentication header 
    #
    print("\n\n############ body : \n",body,"\n\n")
    print("\t ----> [App - fx_handle_new_user_message_to_bot_api : 2. creating the Activity object ]")
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    #
    # Notre object Activity est renvoyée à la methode process_activity de l'adaptateur
    #
    print("\t ----> [App - fx_handle_new_user_message_to_bot_api : 3. Calling the adapter with the activtity object ]")
    # print("\n\n############ BOT.on_turn : \n",BOT.on_turn,"\n\n")
    print("\n App - fx_handle_new_user_message_to_bot_api : 3 --- START")
    print('--------------------------------------------------------------\n')
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    #
    # - L'adaptateur cree le context 
    # - L'adaptateur envoie le context crée au pipeline middleware
    # - L'adaptateur continue par envoyer le context au "turn handler" du bot : BOT.on_turn
    # - L'adaptateur termine par formatter et retourner the response
    # - Durant ce temps, l'adaptateur reste le dernier recours des exceptions generees non prises en charge
    #
    
    if response:
        print("\t ----> [App - fx_handle_new_user_message_to_bot_api : received response from the adapter ]")
        print("\t\t - responde.body : ",response.body)
        print("\t\t - responde.status : ",response.status)
        return json_response(data=response.body, status=response.status)
    else:
        print("\t ----> [App - fx_handle_new_user_message_to_bot_api : OK with no received response from the adapter]")
    print("\n\nApp - fx_handle_new_user_message_to_bot_api : 3 --- END")
    print("--------------------------------------------------------")
    return Response(status=HTTPStatus.OK)



#
# Finally : 
#

def fx_init_app(argv=None):
    #
    # Declaration de l'application 
    #
    print("INFO: [App.py -  fx_init_app ]  fx_init_app called : argv==",argv)
    #
    from botbuilder.integration.applicationinsights.aiohttp import bot_telemetry_middleware
    from botbuilder.core.integration                        import aiohttp_error_middleware
    #
    APP = aiohttp_web.Application(
        middlewares = [            
                bot_telemetry_middleware,             
                aiohttp_error_middleware        
        ]
    )
    print("\tINFO: [App.py -  msa fx_init_app ] APP created")  
    #
    # Definition des EndPoints
    #
    APP.router.add_post("/p10/api/messages", fx_handle_new_user_message_to_bot_api) 
    
    print("\tINFO: [App.py -  fx_init_app ] APP endpoint configured")
    print("\tINFO: [app.py -  fx_init_app ] Nombre d'objets DialogAndWelcomeBot ==",DialogAndWelcomeBot.nb)
    print("\tINFO: [app.py -  fx_init_app ] Nombre d'objets DialogBot           ==",DialogBot.nb)
    return APP

APP = fx_init_app()


if __name__ == "__main__":
    print("INFO: [App.py - main ] start running the bot APP")
    try:
        aiohttp_web.run_app(APP, host="0.0.0.0", port=CONFIG.PORT)
    except Exception as error:
        raise error


#
# Startup classique
#
# gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 -P 3978 app:APP

# python -m aiohttp.web -H 0.0.0.0 -P 8000 p10_chatbot_app:fx_init_app


# 022-12-16T12:06:13.469436029Z usage: aiohttp.web [-h] [-H HOSTNAME] [-P PORT] [-U PATH] entry-func
# 2022-12-16T12:06:13.469501527Z aiohttp.web: error: unable to import p10_chatbot_app.py: No module named 'p10_chatbot_app.py'; 'p10_chatbot_app' is not a package
# 2022-12-16T12:06:13.476125266Z INFO: [AdapterWithErrorHandler : instatiated] nb =  1


# customEvents
# | where customDimensions['text'] == 'No'
# | summarize AggregatedValue=count() by bin(timestamp, 1m)

# {
#     "activityId":"0f29b6b0-7d49-11ed-84e7-7505ed90b334",
#     "activityType":"message","channelId":"emulator",
#     "fromId":"e66a6bec-0adb-43b9-8164-5e66ba1acba0",
#     "fromName":"User","locale":"en-US","recipientId":"ea251710-7d48-11ed-89c4-b5a62ee1fd78","recipientName":"Bot",
#     "text":"No"
# }
