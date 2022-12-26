#!/usr/bin/env python

import os


class Bot_luis_app_and_insights_configuration:
    #
    # Elements pour la configuration de l'application chatbot : 
    #   - ___________________________PORT: port du service pour le bot emulator
    #   - _________________________APP_ID: 
    #   - ___________________APP_PASSWORD: 
    #   - ____________________LUIS_APP_ID: 
    #   - ___________________LUIS_API_KEY: 
    #   - _____________LUIS_API_HOST_NAME: 
    #   - APPINSIGHTS_INSTRUMENTATION_KEY: app-insight
    #
    
    PORT = 3978
    
    APP_ID = os.environ.get("MicrosoftAppId", "")
    
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    LUIS_APP_ID = os.environ.get("LuisAppId","9159a5e0-246d-4723-9fd1-865fdd18d709")
    
    LUIS_API_KEY = os.environ.get("LuisAPIKey","898a47800608435ea33ccde7f880abc5")
    
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName","p10-luis-authoring.cognitiveservices.azure.com/")
    
    # 
    # LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName","westeurope.api.cognitive.microsoft.com")
    # LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName","p10-luis.cognitiveservices.azure.com")
    
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "d546dc50-469e-4f4b-abc6-2f30577a7572"
        # "AppInsightsInstrumentationKey", "a8995314-2a9d-4720-b3ad-cba0cbd2258c"
    )
    
    
# https://p10-luis.cognitiveservices.azure.com/luis/prediction/v3.0/apps/cf2d6334-8bf9-459a-8a52-573d90fa218c/slots/staging/predict?verbose=true&show-all-intents=true&log=true&subscription-key=a328ef4940ad427db28faf097810819c&query=YOUR_QUERY_HERE    
# ywr0zn4eao2cjy8jd8dsc8f8qbzm04exxs204cfq
# secret    : cCh8Q~DYaC65HHHrpFs9K0KxzFldic.6W7eF-cp3
# secret-id : 652e1a58-6963-4a32-a4b4-9e1c2a1db355

# https://msa-p10-appservicename-svc-name.azurewebsites.net:8000/p10/api/messages