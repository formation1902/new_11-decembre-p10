from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient

from functools import reduce
import json, time,datetime, uuid,pickle
import pandas as pd

from p10_LUIS_module import *

####################################################################################################
####################################################################################################
####################################################################################################
INITIAL_VERSION_ID ="0.1"

def fx_stop(msg=None):
    if msg:
        print("fx_stop : raison == ",msg)
    sys.exit(-1)


#
# test
# #    
# prediction_end_point =  'https://p10-luis-authoring.cognitiveservices.azure.com/'
# SLOT_NAME='Production'
# publishing_slot = prediction_end_point + '/luis/v3.0-preview/apps/<YOUR-APP-ID>/slots/' + SLOT_NAME + '/evaluations'
# test_end_point = prediction_end_point + '/luis/v3.0-preview/apps/' + str(app_id) + '/slots/' +  SLOT_NAME + '/evaluations'



if __name__=='__main__':
    my_project = Project10()
    all_luis_apps  = my_project.list_apps(quiete=True)
    print("Nombre d'applications louis configurées :",len(all_luis_apps))
    #
    #
    #
    msaCondition   = "initialisation"
    # msaCondition = "train_after_update"
    # msaCondition   = 'test_trained_active_model'
    
    if msaCondition == "initialisation":
        print('Initialisation des environnements LUIS : ')
        my_project._all_delete()
        #
        my_project = Project10()
        all_luis_apps  = my_project.list_apps(quiete=True)
        if len(all_luis_apps)==0:
            app_id = my_project.create_application()
            all_luis_apps  = my_project.list_apps(quiete=True)

        assert len(all_luis_apps)==1;"Nombre d'applications LUIS detectees different de 1"
        app_id = all_luis_apps[0].id
        my_project.app_show_details(app_id,quiete=False)
        
        my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
        entete("L'application luis active : ")
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        my_project.set_model()
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        my_project.model_utterances_batch(absent_n=4,strict=False)
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        print("\n\nTraining the luis model\n\n")
        my_project.model_train()
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    elif msaCondition == 'test_trained_active_model':
        all_luis_apps  = my_project.list_apps(quiete=True)
        assert len(all_luis_apps)==1;"Nombre d'applications LUIS detectees different de 1"
        app_id = all_luis_apps[0].id
        prediction_end_point =  'https://p10-luis-authoring.cognitiveservices.azure.com/'
        SLOT_NAME='Production'
        publishing_slot = prediction_end_point + '/luis/v3.0-preview/apps/<YOUR-APP-ID>/slots/' + SLOT_NAME + '/evaluations'
        test_end_point = prediction_end_point + '/luis/v3.0-preview/apps/' + str(app_id) + '/slots/' +  SLOT_NAME + '/evaluations'
        print("\n\test_end_point :")
        print(test_end_point)

    elif msaCondition == "trainAfterUpdate":
        all_luis_apps  = my_project.list_apps(quiete=True)
        assert len(all_luis_apps)==1;"Nombre d'applications LUIS detectees different de 1"
        app_id = all_luis_apps[0].id
        current_active_version = my_project.app_show_details(app_id,quiete=False)['active_version']
        major_version = int(current_active_version.split('.')[0])
        minor_version = int(current_active_version.split('.')[1])
        new_minor_version = minor_version + 1 if minor_version <9 else 1
        new_major_version = major_version if new_minor_version!=1 else major_version + 1
        print("current active version : ",current_active_version)
        new_version_id = str(new_major_version)+'.'+str(new_minor_version)
        print("new_version_id = ",new_version_id)
        print('\napp_export_version_as_json : ')
        res = my_project.app_export_version_as_json(app_id,current_active_version) 
        print('\napp_import_version_from_json_export : ')
        res=my_project.app_import_version_from_json_export(app_id,res,new_version_id)
        print("res = ")
        print(res)
        #
        # Update the project active vesrion
        #
        entete("Update the project active vesrion","Current active version == " + current_active_version,"Target active version == " + new_version_id)
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        my_project.project_set_active_luis_app(app_id,new_version_id)
        entete("-------> The new activated application luis  : ")
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        my_project.model_utterances_batch(absent_n=2)
        my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
        my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
        
        print("\n\nTraining the luis model\n\n")
        my_project.model_train()
        pass
    else:
        pass
    
    fx_stop()
    
    
    fx_stop()
    
    app_id = all_luis_apps[0].id
    x = clean_project.app_show_details(app_id,quiete=False)
    print(x['active_version'])
    # print('\napp_export_version_as_json : ')
    # res = clean_project.app_export_version_as_json(app_id,x['active_version']) 
    # print('res = ')
    # print(res)
    # print('\napp_import_version_from_json_export : ')
    # res=clean_project.app_import_version_from_json_export(app_id,res,'10.0')
    # print("res = ")
    # print(res)
    prediction_end_point =  'https://p10-luis-authoring.cognitiveservices.azure.com/'
    SLOT_NAME='Production'
    publishing_slot = prediction_end_point + '/luis/v3.0-preview/apps/<YOUR-APP-ID>/slots/' + SLOT_NAME + '/evaluations'
    test_end_point = prediction_end_point + '/luis/v3.0-preview/apps/' + str(app_id) + '/slots/' +  SLOT_NAME + '/evaluations'
    print("\n\test_end_point :")
    print(test_end_point)
    fx_stop()
    if len(all_luis_apps)==0:
        app_id = clean_project.create_application()
        all_luis_apps  = clean_project.list_apps(quiete=True)

    assert len(all_luis_apps)==1;"Nombre d'applications LUIS detectees different de 1"
    app_id = all_luis_apps[0].id
    clean_project.app_show_details(app_id,quiete=False)
    fx_stop()
    
    clean_project._all_delete()  
    
    my_project = Project10()
    all_luis_apps  = my_project.list_apps(quiete=True)
    print("Nombre d'applications louis configurées :",len(all_luis_apps))
    
    if len(all_luis_apps)==0:
        app_id = my_project.create_application()
        all_luis_apps  = my_project.list_apps(quiete=True)

    assert len(all_luis_apps)==1;"Nombre d'applications LUIS detectees different de 1"
    app_id = all_luis_apps[0].id
    my_project.app_show_details(app_id,quiete=False)
    
    
    
    my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
    entete("L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    my_project.set_model()
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    my_project.model_utterances_batch()
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    print("\n\nTraining the luis model\n\n")
    my_project.model_train()
    
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    
    print("\n\nPublication de l'application\n\n")

    publish_result = my_project.luis_authoring_client.apps.publish(
        my_project.active_luis_app_id,
        {
            'version_id': my_project.active_luis_app_version_id,
            'is_staging': False
        }
    )
    print("\n\n - publish result : \n",publish_result)
    endpoint = publish_result.endpoint_url + "?subscription-key=" + my_project.authoring_key + "&q="
    print("\n\nYour app is published. You can now go to test it on\n{}".format(endpoint))
    
    
    fx_stop("rasion 1001")

    # my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
    
    
    predictionKey = 'c0ecc2043afe4ae3a2eb7a97b8e0c8e4'
    predictionEndpoint = 'https://msa-luis-1902.cognitiveservices.azure.com/'
    runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials)
    
    
    
    # Production == slot name
    predictionRequest = { "query" : "I want to travel from paris to tokyo" }

    predictionResponse = clientRuntime.prediction.get_slot_prediction(app_id, "Production", predictionRequest)
    get_slot_prediction(
        app_id, slot_name, 
        prediction_request, verbose=None, 
        show_all_intents=None, log=None, custom_headers=None, raw=False, **operation_config)
    print("Top intent: {}".format(predictionResponse.prediction.top_intent))
    print("Sentiment: {}".format (predictionResponse.prediction.sentiment))
    print("Intents: ")

    for intent in predictionResponse.prediction.intents:
        print("\t{}".format (json.dumps (intent)))
    print("Entities: {}".format (predictionResponse.prediction.entities))

    
    my_project._all_delete()
    my_project.create_application()
    
    # # # #
    # # # # On garde une seule appli
    # # # #
    all_luis_apps  = my_project.list_apps(quiete=True)
    print("Nombre d'applications louis configurées :",len(all_luis_apps))
    assert len(all_luis_apps)==1;"C'est koi ce bordel"
        
    #### app_id = my_project.create_application()
    app_id = all_luis_apps[0].id
    my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
    entete("L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    
    # # #
    # # # Il faut trouver la condition adequate
    # # #
    # entete("Setteing the model on the active luis app")
    my_project.set_model()
    entete("Recheck z L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    print("\n\n")
    entete("Ajout des utterances")
    my_project.model_utterances_batch()
    
    
    print("\n\n")
    entete("Entrainement du modele")
    # my_project.model_train()
    
    app_id = my_project.active_luis_app_id
    version_id = my_project.active_luis_app_version_id
    async_training = my_project.luis_authoring_client.train.train_version(app_id, version_id)

    is_trained = async_training.status == "UpToDate"

    trained_status = ["UpToDate", "Success"]
    
    i=0
    
    while not is_trained:
        time.sleep(1)
        status = my_project.luis_authoring_client.train.get_status(app_id, version_id)
        is_trained = all(m.details.status in trained_status for m in status)
        if i%10==0:
            entete(' status')
            print(status)
            entete("Iteration : " +str(i))
            for m in status:
                print("\t - ",m.details.status)
                print(m.details)
        i+=1

    
    
    
    
    
    entete("L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    # Publish the app
    publish_result = my_project.luis_authoring_client.apps.publish(
        app_id,
        {
            'version_id': version_id,
            'is_staging': False,
            'region' : 'westeurope'
        }
    )
    print("\nPublication de l'application")

    publish_result = my_project.luis_authoring_client.apps.publish(
        my_project.active_luis_app_id,
        {
            'version_id': my_project.active_luis_app_version_id,
            'is_staging': False
        }
    )
    print("\n\n - publish result : \n",publish_result)
    endpoint = publish_result.endpoint_url + "?subscription-key=" + my_project.authoring_key + "&q="
    print("\n\nYour app is published. You can now go to test it on\n{}".format(endpoint))