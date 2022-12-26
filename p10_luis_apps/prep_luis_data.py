import pandas as pd
import numpy as np
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import json,functools,operator,os,datetime,time
from glom import glom
import warnings
warnings.filterwarnings('ignore')

def fpp(msaTitle,msaText):
    print("#\n# --> ",msaTitle," : ",type(msaText),"\n#\n\n\t",msaText,"\n")
    
def fp(x):
    print(json.dumps(x,indent=4))    
    
def entete(*msgz):
    print("#"*len(' '.join(msgz))+"#"*10,"\n###")
    for msg in msgz:
        print("### --> ",msg)
    print("###")
    print("#"*len(' '.join(msgz))+"#"*10)    

###################################
#
#-----> initialisation des données
#
###################################
plain_data_source_file = "data/frames.json"
model_dir = "./model_data/"
data_initialization_lock =os.path.join(model_dir,'msaFileInitialisationLock.txt')
data_source_fileName = 'training_data.csv'
test_data_source_fileName = "test_data.csv"

####################################################################
#                                                                  #
# --------------------- Extraction des données ------------------- #
#                                                                  #
####################################################################
def p10_data_initialization(lock=True):        
    os.makedirs(model_dir, exist_ok=True)
    if lock and os.path.exists(data_initialization_lock):
        return "\nError : données deja initialisée avec verroulliage en ecriture."
    else:
        print("Initialisation de l'extraction des données : ",end='')
        if os.path.exists(plain_data_source_file):
            with open(data_initialization_lock,'x') as f:
                f.write(str(datetime.datetime.now()))
            print('OK.')
        else:
            print("NOK.")
            return "\n---> Error : la fichier frames.json est absent.\n"
    
    fileName = os.path.join(model_dir,data_source_fileName)
    testFileName = os.path.join(model_dir,test_data_source_fileName)
    entete("Initialisation des données :","Fichier d'entrainement : " + fileName,"Fichier de test : " + testFileName)
    
    s_start = time.time()
    with open(plain_data_source_file,'r') as f:
        data = json.loads(f.read())

    df_nested_list = pd.json_normalize(data, record_path =['turns'],meta=['labels'])
    df_nested_list = df_nested_list[df_nested_list.author=='user'].drop(['db.result','db.search'],axis=1)

    df_nested_list['agentRate']     = df_nested_list.labels.apply(lambda e: e['userSurveyRating'])
    df_nested_list['wizardSuccess'] = df_nested_list.labels.apply(lambda e: e['wizardSurveyTaskSuccessful'])
    df_nested_list = df_nested_list[~df_nested_list.agentRate.isna()]

    df_nested_list['msaStep0']=df_nested_list['labels.acts'].apply(len)
    df_nested_list = df_nested_list[df_nested_list.msaStep0>0]

    df_nested_list['msaStep1'] = df_nested_list['labels.acts'].apply(lambda x: [list(e.values()) for e in functools.reduce(operator.iconcat,[glom(e,'args') for e in x],[])])
    df_nested_list['msaStep2'] = df_nested_list.msaStep1.apply(lambda e: str(e).count('annotations')>0)
    df_nested_list[df_nested_list.msaStep2].shape
    df_nested_list=df_nested_list[~df_nested_list.msaStep2]
    df_nested_list['msaStep3'] = df_nested_list.msaStep1.apply(len)
    greeting_df = df_nested_list[df_nested_list.msaStep3==0]
    df_nested_list.drop(greeting_df.index,inplace=True)

    df_nested_list['msaStep6'] = df_nested_list.msaStep1.apply(lambda listE: [e for e in listE if len(e)>1 ])
    totos = ['intent','or_city','dst_city','str_date','end_date','budget']

    df_nested_list['msaFinalStep'] = df_nested_list.msaStep6.apply(lambda listE: [e for e in listE if e[1] in totos ])
    for toto in totos:
        df_nested_list[toto] = df_nested_list.msaFinalStep.apply(lambda listE: '#'.join([ e[0] for e in listE if e[1]==toto and e[0]!='-1'] ) )
        # df_nested_list[toto] = df_nested_list.msaFinalStep.apply(lambda listE: '#'.join([ e[0] for e in listE if e[1]==toto ] ) )
        df_nested_list[toto] = df_nested_list[toto].replace('',np.nan,regex = True)
        
    df_nested_list['absent_n']  = df_nested_list[totos[1:]].T.isna().sum()
    # df_nested_list['composite'] = df_user_inputs[totos[1:]].isna().apply(lambda row: '_'.join([str(int(not e)) for e in row]),axis=1)
    df_nested_list['composite'] = "a_definir_apres_selection"
    vars = ['text','agentRate','wizardSuccess']
    vars.extend(totos)
    vars.extend(['absent_n','composite'])
    df_user_inputs = df_nested_list[vars]
    #
    totos_renamed = ['intent','ville_depart','ville_destination','date_depart','date_retour','budget']
    vars = ['text','agentRate','wizardSuccess']
    vars.extend(totos_renamed)
    vars.extend(['absent_n','composite'])
    df_user_inputs.columns = vars

    #
    vars = ['agentRate','wizardSuccess','intent','absent_n','composite','text',]
    vars.extend(totos_renamed[1:])
    df_user_inputs = df_user_inputs[vars].reset_index()
    l = list(df_user_inputs.columns)
    l[0]='original_index'
    df_user_inputs.columns = l
    #
    #
    #
    df_user_inputs = df_user_inputs[df_user_inputs.intent=='book'][df_user_inputs.wizardSuccess==True]
    test_data_idx = np.random.choice(df_user_inputs[df_user_inputs.wizardSuccess==True][df_user_inputs.absent_n<5].index,100,replace=False)
    assert len(test_data_idx)==100,'we got a pb!'
    test_data = df_user_inputs.loc[test_data_idx]
    print(test_data.shape)
    df_user_inputs.drop(test_data_idx,inplace=True)
    #
    df_user_inputs.to_csv(fileName,index=False)  
    test_data.to_csv(testFileName,index=False)    
    check_test_data = pd.read_csv(testFileName)
    print(check_test_data.shape)
    return "Initialisation completed successfully  " + " [" + str(round((time.time() -s_start)/60,2)) + " min.] : "+ fileName 

try:
    df_user_inputs = pd.read_csv(os.path.join(model_dir,data_source_fileName))
    df_test = pd.read_csv( os.path.join(model_dir,test_data_source_fileName))
    print("Les données sont déja initialisées :  Chargement effectuée")
except:
    print(p10_data_initialization(True))
    df_user_inputs = pd.read_csv(os.path.join(model_dir,data_source_fileName))
    df_test = pd.read_csv(os.path.join(model_dir,test_data_source_fileName))

if df_user_inputs.shape[0]==0 or df_test.shape[0]==0:
    print("Données initialisées sont vides")
    sys.exit(-1)

    
entities = df_user_inputs.columns[-5:]
intent_name = "book"

####################################################################
#                                                                  #
# ----------------------- Les utterrances -----------------------  #
#                                                                  #
####################################################################
def geolocalize_value_of_entity_within_user_text(user_text, entity_name, value):
    user_text = user_text.upper()
    value = str(value).upper()
    return {
        'entity_name': entity_name,
        'start_char_index': user_text.find(value),
        'end_char_index': user_text.find(value) + len(value)
    }
    
def get_utterances(intent_name,df_user_inputs=df_user_inputs,wizardSuccess=None,absent_n=0,strict=True,entities=entities):
    # filters = []
    # filters.append(df_user_inputs.intent==intent_name)
    # if wizardSuccess != None:
    #     filters.append(df_user_inputs.wizardSuccess == wizardSuccess)
    # if strict:
    #     filters.append(df_user_inputs.absent_n == absent_n)
    # else:
    #     filters.append(df_user_inputs.absent_n <= absent_n)
    # #
    # user_inputs_idx = []
    # for filter in filters:
    #     vx = np.zeros(df_user_inputs.shape[0],dtype=np.int32)
    #     np.put(vx,np.where(filter)[0],np.ones(filter.sum()))
    #     user_inputs_idx.append(vx)
        
    # user_inputs_idx = np.where(np.product(user_inputs_idx,axis=0))[0]
    data = df_user_inputs[df_user_inputs.intent==intent_name][df_user_inputs.wizardSuccess==wizardSuccess]
    if strict:
        data = data[data.absent_n==absent_n]
    else:
        data = data[data.absent_n<=absent_n]
    #
    data['composite'] = data[entities].isna().apply(lambda row: '_'.join([str(int(not e)) for e in row]),axis=1)
    #
    data['entity_labels'] = data.apply(lambda row: [ geolocalize_value_of_entity_within_user_text(row['text'],entity,row[entity]) for entity in entities if not row[entity]!=row[entity] ],axis=1)
    data['text_as_utterance']=data.apply(lambda row: {
        'text': row['text'],
        'intent_name': "intention_reserver_un_billet_d_avion",
        'entity_labels': row['entity_labels']
    },axis=1)
    print("Nombre de utterances pour l'entrainement du model : ",data.shape[0])
    return data.text_as_utterance.values.tolist()


def geolocalize_value_of_entity_within_user_text_for_test(user_text, entity_name, value):
    user_text = user_text.upper()
    value = str(value).upper()
    return {
        'entity': entity_name,
        'startPos': user_text.find(value),
        'endPos': user_text.find(value) + len(value)
    }
    
    
def get_utterances_for_test(data=df_test,entities=entities):
    data['composite'] = data[entities].isna().apply(lambda row: '_'.join([str(int(not e)) for e in row]),axis=1)
    #
    data['entity_labels'] = data.apply(lambda row: [ geolocalize_value_of_entity_within_user_text_for_test(row['text'],entity,row[entity]) for entity in entities if not row[entity]!=row[entity] ],axis=1)
    data['text_as_utterance']=data.apply(lambda row: {
        'text': row['text'],
        'intent': "intention_reserver_un_billet_d_avion",
        'entities': row['entity_labels']
    },axis=1)
    return data.text_as_utterance.values.tolist()


data = get_utterances_for_test()
# print(json.dumps(data[0],indent=2))
# print(json.dumps(data[1],indent=2))

with open('model_data/utterances_for_test.json','w') as f:
    f.write('[\n')
    l=[]
    i=0
    # for utterance in data:
    while i < len(data):
        l.append(str(json.dumps(data[i],indent=2)))
        f.write(str(json.dumps(data[i],indent=2)))
        i+=1
        if i != len(data):
            f.write(',')
    # f.write(str(l[0]))
    # f.write(',')1
    # f.write(str(l[0]))
    f.write('\n]')
    # f.write(str(data))



# [
#     {
#         "text": "hey happy dad, aren't you happy big daddy?  is it or isn't it ?",
#         "intent": "None",
#         "entities": [
#             {
#                 "entity": "FamilyMember",
#                 "startPos": 4,
#                 "endPos": 6
#             }
#         ]
#     }
# ]

