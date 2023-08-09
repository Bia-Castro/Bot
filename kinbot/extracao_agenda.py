import time
import datetime
# Chrome Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

# Instalação do ChromeDriver compatível com a versão do Chrome instalada
verify_settings = {
        'user_name': 'brenafernanda@kinsolenergia.com.br', # conta engenharia
        'user_passwd': 'minhau123',
        'verify_time': 15,
    }
    
def calendar_site(option):
        
        # Iniciar o driver  
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        
        # Versão 115.0.5790.110 (Versão oficial) 64 bits
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        
        # driver.get('https://app-lab.kinsol.com.br/admin/calendar?')

        data = {'response': False, 'title': ''}
        
        # LOGINN
        urls = {
                'login': 'https://app.kinsol.com.br',
                'calendario': 'https://app.kinsol.com.br/admin/calendar?user=me',
                'propostas': 'https://app-lab.kinsol.com.br/admin/board'
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
        

        # driver.get('https://app-lab.kinsol.com.br/admin/calendar?')
        # time.sleep(5)
#

        if option == 'h':
            calendar_date = datetime.date.today()
            print(f'Opção h - imprimir calendario do dia {calendar_date}')
            driver.get('https://app.kinsol.com.br/admin/activities?status=today')

        elif option == 'a':
            calendar_date = datetime.date.today() + datetime.timedelta(days=1)
            print(f'Opção a - imprimir calendario do dia {calendar_date}')

            driver.get('https://app.kinsol.com.br/admin/activities?status=tomorow')
        else:
            ValueError("Opção inválida! Deve ser 'h' para hoje ou 'a' para amanhã.")
        
        try:
            calendar_url = urls['calendario'] + f'&date={calendar_date}'
            # driver.get(calendar_url)

            time.sleep(5)
            print('Acessou calendario...')

            # Localizar o elemento select
            select_element = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_length"]/label/select')

            # Criar um objeto Select a partir do elemento
            select = Select(select_element)

            # Selecionar a opção de itens por página
            select.select_by_value('-1')  # Certifique-se de que '-1' (Tudo) seja o valor correto para a opção desejada
            

            """ 
             ESSE TIME BUGA O CODIGO POIS AS VEZES DEMORA MAIS QUE ISSO PARA ATUALIZAR A PAGINA

             O CRM TEM O TEMPO DE ESPERA PARA ATUALIZAR PARA MOSTRAR TODOS OS REGISTROS NA MESMA TELA

             SELECIONAR "TUDO" > AGUARDAR ATÉ A PÁGINA SER ATUALIZADA
             
            """
            time.sleep(20)  ## tempo longo para garantir que tudo seja impresso tudo na mesma página
            ## substituir por (????)
            """
                idéia 1: Pegar o texto_paginas e aguardar aparecer todos os registros na mesma página 

                def alterar_pag_tudo():
                    try:
                        driver.find_element( texto_pagina )
                        if texto_pagina == 'pag 1 de 10':
                            return false
                        else:
                            return true
                    except:
                        return false

                while not alterar_pag_tudo():
                    time.sleep(1)
                    print('*', end="")


                # dessa forma, quando o texto da página estiver como o padrão (mostrando 10 registros por página)
                  o código se mantém em loop até o elemento atualizar e mostrar todos os itens na mesma página

            """



            try:
                # xpath do elemento que mostra a quantidade de registros na agenda
                texto_paginas = driver.find_element(By.XPATH, '//*[@id="DataTables_Table_0_info"]').text
                print(texto_paginas) ## Quantidade de registros na página 
                # Extrair o número total de registros usando manipulação de string 
                registros = texto_paginas.split(' ')
                qtdade_registros = registros[4]


                cards = []  # vetor vazio para receber os registros

                for i in range (1,int(qtdade_registros)+1):
                    try:
                        print(f'\n\nRegistro: {i} ', end=" | ")
                        id_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[2]')
                        print(f'ID: {id_agenda.text}', end=" | ")

                        data_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[3]')

                        status_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[4]')

                        concluido_em_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[5]')

                        tipo_de_atividade_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[6]')

                        responsavel_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[7]')
                        print(f'Responsável: {responsavel_agenda.text}', end=" | ")

                        criado_por_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[8]')

                        cliente_agenda = driver.find_element(By.XPATH, f'//*[@id="DataTables_Table_0"]/tbody/tr[{i}]/td[9]')
                        
                        card = [id_agenda.text, data_agenda.text, status_agenda.text, concluido_em_agenda.text, tipo_de_atividade_agenda.text, responsavel_agenda.text, criado_por_agenda.text, cliente_agenda.text]
                        cards.append(card)

                    except Exception as erro: print('')
                print('\n***********************************************************')
                # print(cards)  # vetor com todos os eventos da agenda
                return cards

            except Exception as error: print(error)
        except Exception as erro: print(erro)


## filtrar apenas os registros do usuario ##
def cards_usuario(usuario, cards):
    cards_user = []
    for card in cards:
        responsavel = card[5]
        if responsavel == usuario:
            id = card[0]
            data = card[1]
            status = card[2]
            concluido_em = card[3]
            tipo_de_atividade = card[4]
            responsavel = card[5]
            criado_por = card[6]
            cliente = card[7]
            evento = [id, data, status, concluido_em, tipo_de_atividade, responsavel, criado_por, cliente]
            cards_user.append(evento)
    return cards_user


## função chamada no kinbot ## 
def obter_agenda_usuario(usuario, option):
    cards = calendar_site(option)
    cards_user = cards_usuario(usuario, cards)
    print(cards_user)
    return cards_user
