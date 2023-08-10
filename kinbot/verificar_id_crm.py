from selenium.common.exceptions import NoSuchElementException
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

# Instalação do ChromeDriver compatível com a versão do Chrome instalada
verify_settings = {
        'user_name': 'brenafernanda@kinsolenergia.com.br', # conta engenharia
        'user_passwd': 'minhau123',
        'verify_time': 15,
    }
    
def obter_lista_usuario(ID):
        # ler o item Mostrando de 1 até 775 de 775 registos e extrair só o total de registros
        def obter_qtde_registros():
            try:
                info_pagina = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_info"]').text
                info_pagina_texto = info_pagina.split(' ')
                # Mostrando de 1 até 775 de 775 registos
                elemento1 = info_pagina_texto[0] ## Mostrando
                elemento2 = info_pagina_texto[1] ## de
                elemento3 = info_pagina_texto[2] ## 1
                elemento4 = info_pagina_texto[3] ## até
                elemento5 = info_pagina_texto[4] ## 10 ou 775(total)
                elemento6 = info_pagina_texto[5] ## de
                elemento7 = info_pagina_texto[6] ## total (775)
                elemento8 = info_pagina_texto[7] ## registros

                return elemento5
            except Exception as error: print(error) 
                
        # leitura da pagina  (ler o item Mostrando de 1 até 775 de 775 registos)
        def aguardar_mostrar_tudo():
            try:
                info_pagina = driver.find_element(By.ID, 'DataTables_Table_0_info').text
                info_pagina_texto = info_pagina.split(' ')
                # Mostrando de 1 até 775 de 775 registos
                elemento1 = info_pagina_texto[0] ## Mostrando
                elemento2 = info_pagina_texto[1] ## de
                elemento3 = info_pagina_texto[2] ## 1
                elemento4 = info_pagina_texto[3] ## até
                elemento5 = info_pagina_texto[4] ## 10 ou 775(total)
                elemento6 = info_pagina_texto[5] ## de
                elemento7 = info_pagina_texto[6] ## total (775)
                elemento8 = info_pagina_texto[7] ## registros

                if elemento5 == elemento7:
                     print('Todos os elementos foram localizados...')
                     return True
                else:
                     return False
            except Exception as error: print(error)
        
        # clicar o select e selecionar a opção Mostrar Tudo
        def selecionar_mostrar_tudo():
            try:
                # Localizar o elemento select   ## VERIFICAR SE É ESSE XPATH MESMO
                select_element = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_length"]/label/select')

                # Criar um objeto Select a partir do elemento
                select = Select(select_element)

                # Selecionar a opção de itens por página
                select.select_by_value('-1')  # Certifique-se de que '-1' (Tudo) seja o valor correto para a opção desejada
                print('Aguardando mostrar todos os itens na página...')
            except Exception as error: print(error)

        # Iniciar o driver  
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        data = {'response': False, 'title': ''}
        
        # Versão 115.0.5790.110 (Versão oficial) 64 bits
        driver = webdriver.Chrome(executable_path=ChromeDriverManager(version="114.0.5735.16").install(), options=options)
        
        # LOGINN
        urls = {
                'login': 'https://app.kinsol.com.br',
                'usuarios': 'https://app.kinsol.com.br/admin/users',
                }
        
        """
        Reliza o login no plataforma, retorna o driver com os novos valores
        """
        try:
            user_name= verify_settings['user_name']
            user_passwd =  verify_settings['user_passwd']
            # Acessa o site
            driver.get(urls['login'])
            # Informar usuário
            driver.find_element(By.NAME, 'email').send_keys(user_name)
            # Informar senha
            driver.find_element(By.NAME, 'password').send_keys(user_passwd)
            # Clicar no botão de login
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        except NoSuchElementException as error:
            print('>>> [ERROR]: ', error)
            print('>>> [ERROR]: Não foi possível realizar o login')
        
        driver.get(urls['usuarios'])

        print('Acessou calendario...')
        time.sleep(2)
        selecionar_mostrar_tudo()
        ## aguardar enquanto a quantidade de registros na página nao for igual a quantidade total de registros
        while not aguardar_mostrar_tudo():
             time.sleep(3)
             print('*', end="")

        registros = obter_qtde_registros()
        print(f'registros = {registros}')
        time.sleep(5)
        # loop para ler todos os registros 
        for i in range(1, int(registros)+1):
             try:
                id_crm = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[1]').text
                if id_crm == ID:               
                            nome = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[2]').text             
                            print(f'ID: {id_crm}       NOME: {nome}')
                            nome_usuario = nome
                            return nome_usuario
                
             except Exception as e: print('<< ERROR: ', e, '\nErro ao extrair usuários!')

        return None