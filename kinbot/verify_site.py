import requests
import asyncio
from time import sleep

from .web_driver import WebDriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class VerifySite():
    """"""
    urls = {
        'login': 'https://app.kinsol.com.br',
        'calendario': 'https://app.kinsol.com.br/admin/calendar?user=me',
        'propostas': 'https://app.kinsol.com.br/admin/board'
    }
    
    def __init__(self, verify_time: float, user_name: str, user_passwd: str):
        self.verify_time:float = verify_time
        self.user_name:str = user_name
        self.user_passwd:str = user_passwd
        
    async def finalize_driver(self, driver):
        try:
            driver.close()
            driver.quit()
        except:
            print('>>> [ERROR]: Não foi possível finalizar o driver atual.')

    async def set_verify_time(self):
        print('\n>>> A página será verifica a cada 15 minutos')
        print('>>> Se deseja alterar esse valor digite o tempo desejado em minutos')
        print('>>> Caso contrário prescione `Enter` para continuar: ')
        try:
            op_time = int(input('<<< '))
        except:
            print('>>> Ops, algo inválido foi digitado... Vamos tentar novamento, ok?')
            self.set_verify_time

        if op_time > 0:
            self.verify_time = op_time

        print(f'>>> Tudo certo o tempo de verificação é de: {self.verify_time} minutos!\n')
        
    async def login_site(self, driver):
        """
        Reliza o login no plataforma, retorna o driver com os novos valores
        """
        try:
            # Acessa o site
            driver.get(self.urls['login'])
            # Informar usuário
            driver.find_element(By.NAME, 'email').send_keys(self.user_name)
            # Informar senha
            driver.find_element(By.NAME, 'password').send_keys(self.user_passwd)
            # Clicar no botão de login
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        except NoSuchElementException as error:
            print('>>> [ERROR]: ', error)
            print('>>> [ERROR]: Não foi possível realizar o login')
        
        return driver

    async def verify_site(self):
        """
        Verifica se o site está online e realiza login
        """
        # Iniciar o driver
        driver = WebDriver().driver

        # Status code
        data = {'status_code': '', 'login_success': False}
        r = requests.get(self.urls['login'])
        data['status_code'] = r.status_code
        print('\n>>> Status Code: ', r.status_code)

        # Login
        driver = await self.login_site(driver)
        await asyncio.sleep(2)
        if driver.current_url != self.urls['calendario']:
            await self.finalize_driver(driver)
            return data

        driver.close()

        print('>>> [INFO]: Login Realizado com suscceso')
        data['login_success'] = True

        # self.finalize_driver(driver)
        return data
    
    async def action_site(self):
        # Iniciar o driver
        driver = WebDriver().driver
        data = {'response': False, 'title': ''}

        driver = await self.login_site(driver)
        await asyncio.sleep(3)
        
        driver.get('https://app.kinsol.com.br/admin/board')
        await asyncio.sleep(5)
        # Capturar todos os cards da tela de proposta
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, 'article[class="card"]')

            if not cards:
                return data

            # Clicar no primeiro card capturado e trocar de aba
            try:
                driver.execute_script("arguments[0].click();", cards[0])
                driver.switch_to.window(driver.window_handles[1])
                
                # Achar o título
                title = driver.find_element(By.CSS_SELECTOR, 'h3[class="page-title"]')
                data['response'] = True
                data['title'] = title.text
            except NoSuchElementException as error:
                print('>>> [ERROR]: Não consegui selecionar o card.')
                print('>>> [ERROR]: ', error)
                return data
            
            self.finalize_driver(driver)
            
            return data
            
        except NoSuchElementException as error:
            self.finalize_driver(driver)
            print('>>> [ERROR]: Nenhum card de propósta foi localizado!')
            print('>>> [ERROR]:', error)
            return False

    async def score_site(self):
        """
        Pega os valores presentes no cabeçalho da tabela de propostas
        """
        # Iniciar o driver
        driver = WebDriver().driver
        score_list = []

        driver = await self.login_site(driver)
        await asyncio.sleep(2)
        driver.get(self.urls['propostas'])
        await asyncio.sleep(8)
        headers = driver.find_elements(By.CSS_SELECTOR, 'section[class="list"] > header')
        
        for header in headers:
            if not header.text.strip():
                continue
            header_title = header.text.split('R$')[0].strip()
            header_business = header.text.split('\n')[-1].strip()
            score_list.append(f'{header_title} - {header_business}')
            
        driver.close()
        driver.quit()

        return score_list