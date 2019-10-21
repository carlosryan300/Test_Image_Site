
import csv
import json
import os
import pprint
import subprocess
import sys
import time
import gspread
import openpyxl
import pandas as pd
import requests, socket
from oauth2client.service_account import ServiceAccountCredentials
import time, datetime
from google.cloud import bigquery

PATH = os.getcwd()
LisApiKey = []


def InsertRow_BQ(tuple_data): 
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/data/sfdump/bot_loaded/bigquery/de.json'
    client = bigquery.Client()
    project_id = 'project_id'
    dataset_id = 'dataset_id'
    table_id = 'table_id'
    print("Metódo Construtor Criado Com Sucesso\nProject: {0}\nDataSet: {1}\nTableId: {2}"
        .format(project_id,dataset_id,table_id))
    table_referece = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_referece)
    rows_to_insert = [
        tuple_data
    ]
    request_BQ = client.insert_rows(table, rows_to_insert) 
    print(request_BQ)


def webspeedtest(id_test, url_next_test, url_site, type_test):
    Valida_Connection()
    MountUrlWSST = 'https://webspeedtest-api.cloudinary.com/test/'+id_test
    req = requests.api.get(MountUrlWSST).json()
    pprint.pprint(req['status'])
    if req['status'] != 'success':
        req_new_test = requests.api.get(url_next_test).json()
        status_code = int(req_new_test['statusCode'])
        print('dormindo webspeedteste linha 37')
        while status_code == 400:
            LisApiKey.remove(LisApiKey[0])
            url_wpt = f"http://www.webpagetest.org/runtest.php?k={LisApiKey[0]}&url={url_site}&breakdown=1&runs=1&fvonly=0&f=json&location={type_test}.Cable"
            RequestTest = requests.api.get(url_wpt).json()
            status_code = int(RequestTest['statusCode'])
        new_url_json = RequestTest['data']['jsonUrl']
        Espera(1,new_url_json)
        MountUrlWSST = 'https://webspeedtest-api.cloudinary.com/test/'+new_url_json[47:]
        req = requests.api.get(MountUrlWSST).json()
        #pprint.pprint(req)
    URL = req['data']['resultSumm']['url']
    if 'code' in req:
        print(f'O TESTE AINDA NÃO FOI FINALIZADO PARA A URL: {MountUrlWSST}')  
    else: 
        print('O PROCESSO IRÁ CONTINUAR')
        leght_image = len(req['data']['imagesTestResults'])
        for i in range(0, leght_image-1):
            leght_dynamicFormats = len(req['data']['imagesTestResults'][i]['dynamicFormats'])
            if 'format' in req['data']['imagesTestResults'][i] or 'url' in req['data']['imagesTestResults'][i]:
                for j in range(0, leght_dynamicFormats):
                    leght_image_w = int(req['data']['imagesTestResults'][i]['width'])
                    leght_image_h = int(req['data']['imagesTestResults'][i]['height'])
                    if leght_image_h >= 30 and leght_image_w >= 43:
                        if req['data']['resultSumm']['viewportSize']['height']<=750 and req['data']['resultSumm']['viewportSize']['width']<=500:
                            tipo = 'Mobile'
                        else:
                            tipo = 'Desktop'
                        print('IMAGEM RELEVANTE')
                        data_stamp = datetime.datetime.now().timestamp()
                        lista = [
                            str(data_stamp),
                            str(req['data']['resultSumm']['url']),
                            str(req['data']['resultSumm']['browserName']),
                            str(req['data']['resultSumm']['browserVersion']),
                            str(req['data']['resultSumm']['location']),
                            str(tipo),
                            str(req['data']['resultSumm']['totalPageRank']),

                            int(req['data']['resultSumm']['totalImagesCount']),
                            int(req['data']['resultSumm']['totalImagesWeight']),
                            float(req['data']['resultSumm']['totalPercentChange']),

                            str(req['data']['imagesTestResults'][i]['url']),

                            int(req['data']['imagesTestResults'][i]['bytes']),
                            int(req['data']['imagesTestResults'][i]['width']),
                            int(req['data']['imagesTestResults'][i]['height']),

                            str(req['data']['imagesTestResults'][i]['format']),
                            str(req['data']['imagesTestResults'][i]['resource_type']),
                            str(req['data']['imagesTestResults'][i]['original_filename']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['format']['value']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['fit']['value']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['compression']['value']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['color_space']['value']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['color_depth']['value']),
                            str(req['data']['imagesTestResults'][i]['analyze']['grading']['aggregated']['value']),
                            
                            int(req['data']['imagesTestResults'][i]['transformedImage']['bytes']),
                            
                            str(req['data']['imagesTestResults'][i]['transformedImage']['url']),
                            
                            int(req['data']['imagesTestResults'][i]['transformedImage']['width']),
                            int(req['data']['imagesTestResults'][i]['transformedImage']['height']),
                            float(req['data']['imagesTestResults'][i]['transformedImage']['percentChange']),
                            
                            str(req['data']['imagesTestResults'][i]['transformedImage']['analyze']['data']['format']),
                            
                            int(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['bytes']),
                            
                            str(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['url']),
                            
                            int(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['width']),
                            int(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['height']),
                            float(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['percentChange']),
                            
                            str(req['data']['imagesTestResults'][i]['dynamicFormats'][j]['analyze']['data']['format']),
                        ]
                        #InsertSheets(lista)
                        lista[0]=data_stamp
                        try:
                            InsertRow_BQ(tuple(lista))
                            print('INSERIDO EM BIGQUERY')
                        except Exception as e:
                            print('=-=-=-=-=Error no BigQuery=-=-=-=-=')
                            print(e)  
                    else:
                        print(30*'=-')
                        print('IMAGEM IRRELEVANTE')
                        print(f"Nome:{req['data']['imagesTestResults'][i]['original_filename']}")
                        print(f"Tamanho:{leght_image_w}x{leght_image_h}")
                        print(30*'=-')
            else:
                print(30*'=-')
                print('FALTA CAMPOS')
                print(30*'=-')
        else:
            print(f'Teste Para a URL:{URL}\n Foi Invalido')

def InsertSheets(List):
    escopo = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(PATH+"/websitespeedtest.json", escopo)
    autorizacao = gspread.authorize(credenciais)
    Valida_Connection()
    try:
        sheet = autorizacao.open('Website Speed Test').worksheet('websitespeedtest')
        print(List)
        sheet.append_row(List)
    except Exception as Erro:
        print(Erro)
        pass

def WebPageTest():
    global LisApiKey
    TypeTests = ["Dulles_MotoG4", "Dulles"]
    ListUrlSite = GSheets()
    ListUrlTest = list()
    tempo = 0       
    for TypeTest in TypeTests:
        for UrlSite in ListUrlSite:
            TestWebPage = f"http://www.webpagetest.org/runtest.php?k={LisApiKey[0]}&url={UrlSite}&breakdown=1&runs=1&fvonly=0&f=json&location={TypeTest}:Chrome.Cable"
            print(TestWebPage)
            Valida_Connection()
            RequestTest = requests.api.get(TestWebPage).json()
            status_code = int(RequestTest['statusCode'])
            while status_code == 400:
                LisApiKey.remove(LisApiKey[0])
                TestWebPage = f"http://www.webpagetest.org/runtest.php?k={LisApiKey[0]}&url={UrlSite}&breakdown=1&runs=1&fvonly=0&f=json&location={TypeTest}:Chrome.Cable"
                print(TestWebPage)
                RequestTest = requests.api.get(TestWebPage).json()
                status_code = int(RequestTest['statusCode'])
            ListUrlTest.append(RequestTest['data']['jsonUrl'])
    with open(f'{PATH}/URL.txt','a') as TxtSaveUrl:
        for txt in ListUrlTest:
            TxtSaveUrl.write(f'{txt}'+'\n')
    tempo = 0
    FinalUrl = ListUrlTest[len(ListUrlTest)-1]
    if tempo == 0:
        print("TENTANDO TESTAR O TEMPO DE ESPERA")
        tempo = Espera(len(ListUrlTest), FinalUrl)
    else:
        pass

    for i in ListUrlTest:
        req = requests.api.get(i).json()
        if 'testUrl' in req['data']:
            url_site = req['data']['testUrl']
            type_test = req['data']['location']
            url_wpt = f"http://www.webpagetest.org/runtest.php?k={LisApiKey[0]}&url={url_site}&breakdown=1&runs=1&fvonly=0&f=json&location={type_test}.Cable"
            id_test = i[47:]
            print(f'ID TEST: {id_test}\nURL WEBPAGE: {url_wpt}')
            try:
                SFR = int(req['data']["successfulFVRuns"])
                if SFR > 0:
                    print(10*'=-test=-')
                    webspeedtest(id_test, url_wpt, url_site, type_test)
                    print(10*'=-sucess=-')
                    print(f'ID TEST: {id_test}\nURL WEBPAGE: {url_wpt}')
                    print(10*'=-sucess=-')
                else:
                    print('SFR INVÁLIDO')
            except Exception as err:
                print(10*'-=error-='+f'\n{err}\n'+10*'-=error-=')
        else:
            print(req)

def GSheets():
    lista = []
    escopo = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(PATH+"/websitespeedtest.json", escopo)
    autorizacao = gspread.authorize(credenciais)
    Valida_Connection()
    sheets = autorizacao.open("Website Speed Test").worksheet('urls')
    dados = sheets.get_all_records()
    df_sheets = pd.DataFrame(dados)
    lista =  list(df_sheets['URL'])
    dados = []
    for string in lista:
        string = str(string.rstrip())
        if string != '':
            dados.append(string)
    #pprint.pprint(dados)
    return list(dados)
             
def Espera(Len, URL):
        i = 60
        testtime = (int(Len)*2)
        time.sleep(testtime)
        ValidaUrl = requests.api.get(URL).json()
        Statuscode = json.dumps(ValidaUrl["statusCode"])
        if Statuscode!= '200':
            Valida_Connection()
            ValidaUrl = requests.api.get(URL).json()
            Statuscode = json.dumps(ValidaUrl["statusCode"])
            while Statuscode != '200':
                ValidaUrl = requests.api.get(URL).json()
                time.sleep(i)
                Statuscode = json.dumps(ValidaUrl["statusCode"])
                i = i + 60
        else:
            pass
        return (testtime+i)

def ChecaConexao():
    URLConfiaveis = ['www.google.com', 'www.yahoo.com', 'www.bb.com.br']
    for urlconfiaveis in URLConfiaveis:
        a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        a.settimeout(.5)
        try:
            b = a.connect_ex((urlconfiaveis, 80))
            if b == 0:  # ok, conectado
                return True
        except:
            pass
        a.close()
    return False

def Valida_Connection():
    check = False
    i = 0
    while check == False:
        if ChecaConexao() == True:
            check = True
            pass
        else:
            print("..Opss! NÃO HÁ CONEXÃO COM A INTERNET, POR FAVOR VERIFIQUE A CONEXÃO!..")
            print(12*"-="+" EM {0} MIN TENTAREI EXECUTAR NOVAMENTE! ".format(math.trunc(i/60))+ 12*"-=")
            time.sleep(i)
            i = i+60



try:
    WebPageTest()
    subprocess.check_output(['bash', '-c', 'echo "O TESTE FOI CONCLUIDO COM SUCESSO!" | mail -s "Website Speed Sucess" carlos.silva@jussi.com.br'])
except Exception as erro:
    print(erro)
    subprocess.check_output(['bash', '-c', 'echo "ERROR: {0}\n" | mail -s "ERROR: Na Exportação de Website Speed Test" carlos.silva@jussi.com.br'.format(erro)])
    time.sleep(360)
    WebPageTest()


