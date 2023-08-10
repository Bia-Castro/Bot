import logging
import asyncio
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, Updater, MessageHandler, filters, ConversationHandler
from .verify_site import VerifySite

from .extracao_agenda import obter_agenda_usuario
from .verificar_id_crm import obter_lista_usuario

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

class KinBot():
    """
        KinBot - Bot do Telegram 
    """
    
    ### TOKEN EDITADO ##### 
    # TOKEN = '6530582523:AAF-nZl5q9Ws8JKrqLaGpngGfQ1sfF-8KyA' # @kinsolengenhariabot
    TOKEN = '5840284976:AAE0pGUW3v79DZtZ6cKiGlum83k4b5VwqPs' # @botbia
    application = None
    monitor_flag = False
    task = None
    LOGIN, CALENDAR, CALENDAR_USUARIO , GET_EMAIL = range(4)
    user_list = []

    crm_list = [
                ['18321', 'Brena Fernanda (Executiva de Engenharia)'],
                ['817', 'Antonio Mateus (Beto) (Engenharia)'],
                ['812',  'Fernanda Mendes Macedo Oliveira ( Engenharia - Projetos )']
    ]

    verify_settings = {
        'user_name': 'kinsol.servidor@gmail.com',
        'user_passwd': 'kinsolbot10',
        'verify_time': 15,
    }

    async def start(self, update: Update, context) -> None:
        """Send a message when the command /start is issued."""
        user = update.message.from_user
        await update.message.reply_text(f'Olá {user.first_name} {user.last_name} 👋, bom te ver!')
        
        if not await self.user_is_authenticated(update):
            return

    async def cancel_get_passwd(self, update: Update, context) -> int:
        await update.message.reply_text('Login cancelado.')
        return ConversationHandler.END

    async def help_command(self, update: Update, context):
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    async def monitor_site(self, update):
        """Realiza verificações do status de operação do site dentro de um intervalo de tempo"""
        status_code = ''
        login_success = False
        
        await update.message.reply_text(f'👀Iniciando o monitoramento...\n⌚A cada {self.verify_settings["verify_time"]} minutos será atualizado o status do site!🔥')
        
        while self.monitor_flag:
            driver = VerifySite(**self.verify_settings)
            result = await driver.verify_site()
            status_code = result['status_code']
            login_success = 'Login realizado com sucesso 🟢' if result['login_success'] else 'Erro ao realizar login ❌'

            await update.message.reply_text(f'Status code: {status_code}\n{login_success}')

            await asyncio.sleep(self.verify_settings["verify_time"] * 60)

    async def monitor_command(self, update: Update, context) -> None:
        """Inicia o monitoramento em uma nova tarefa assíncrona"""
        
        if not await self.user_is_authenticated(update):
            return

        if self.monitor_flag:
            await update.message.reply_text('O monitoramento já está em andamento.')
            return

        self.monitor_flag = True
        self.task = asyncio.create_task(self.monitor_site(update))

        print('>>> [INFO]: Monitoramento iniciado.')
        await update.message.reply_text('Monitoramento iniciado.')
        
        return

    async def stop_command(self, update, context) -> None:
        """Interrompe o monitoramento"""
        
        if not await self.user_is_authenticated(update):
            return

        if not self.monitor_flag:
            await update.message.reply_text('O monitoramento não está em andamento.')
            return
        
        # Cancela a tarefa do monitoramento
        self.monitor_flag = False
        self.task.cancel()
        print('>>> [INFO]: Monitoramento finalizado.')
        await update.message.reply_text('Monitoramento finalizado.')

    async def action(self, update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Realiza uma interação com site, caso realizado com sucesso retorna
        um valor booleano
        """
        if not await self.user_is_authenticated(update):
            return
        
        await update.message.reply_text('Realizando interação com o site...')
        driver = VerifySite(**self.verify_settings)
        result = await driver.action_site()
        
        print(result)
        if not result['response']:
            print('>>> [INFO]: Não foi possível realizar a interação!')
            await update.message.reply_text('❌ Não foi possível realizar a interação...')
            return
        
        print(f'>>> [INFO]: Interaçaõ realizada com sucesso!\nitem verificado: {result["title"]}.')
        await update.message.reply_text(f'Interaçaõ realizada com sucesso!\nitem verificado: {result["title"]}.')
        if not result['passed']:
            await update.message.reply_text('❌ A atividade não foi inserida com sucesso!')
        else:
            await update.message.reply_text('✅ A atividade foi inserida com sucesso!')
        return
    
    async def crm_score(self, update, context) -> None:
        if not await self.user_is_authenticated(update):
            return

        print('>>> [INFO]: Filtrando score...')
        await update.message.reply_text('Filtrando score...')
        
        driver = VerifySite(**self.verify_settings)
        score_list = await driver.score_site()
        
        if not len(score_list):
            print('>>> [INFO]: nenhum score localizado.')
            await update.message.reply_text('nenhum score localizado.')
            return

        str_score = '\n'.join(score_list)
        
        print('>>> [INFO]: Lista de Leads por etapas:\n', str_score)
        await update.message.reply_text(f'📊Lista de Leads por etapas:\n{str_score}')
    
    async def user_is_authenticated(self, update: Update) -> bool:
        user_id = update.message.from_user.id
        is_authenticated = user_id in self.user_list
        if not is_authenticated:
            await update.message.reply_text('Você deve realizar a autenticação\nDigite: /login.')
            
        return is_authenticated
    
    ### CALENDARIO ### 
    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Autenticar/Logar usuário"""
        await update.message.reply_text('Por favor, envie o seu ID de usuário:\nPara cancelar o login digite: /cancel.')
        return self.LOGIN
        
    ## substitui o /login em vez de pedir senha, pede o ID do usuário do CRM
    async def get_id_usuario(self, update: Update, context) -> int:
            id_usuario_crm = update.message.text
            await update.message.reply_text('🔎 Realizando a autenticação de usuário\.\.\.',parse_mode='MarkdownV2')
            try:
                """ ORIGINAL """
                # authenticated_user = obter_lista_usuario(id_usuario_crm)

                """PARA TESTES"""
                authenticated_user = 'Fernanda Mendes Macedo Oliveira ( Engenharia - Projetos )'

            except Exception as error:
                authenticated_user = None
                print('>>> ERROR: ', error)

            if authenticated_user is None:
                await update.message.reply_text("❌  *Falha na autenticação*\!\nDesculpe, não foi possível localizar o ID inserido, verifique e tente novamente\.\.\.",parse_mode='MarkdownV2')
                return

            user_id = update.message.from_user.id
            self.user_list.append(user_id)

            await update.message.reply_text(f"✅  Usuário autenticado com sucesso!\n\n👤 {authenticated_user}")
            context.user_data['authenticated_user'] = authenticated_user
            
            ## extra ?? listar ferramentas disponíveis 
            await update.message.reply_text(f'\n\n🗓️ Para verificar a *agenda* digite: \n\n 📆/calendar',parse_mode='MarkdownV2')

            return ConversationHandler.END
    
    async def calendar(self, update: Update, context):
        if not await self.user_is_authenticated(update):
            return
    
        await update.message.reply_text('Deseja listar a agenda de hoje ou de amanhã?\n[h ou a]')
    
        return self.CALENDAR_USUARIO  # Redireciona para o próximo estágio da conversa
    
    async def get_option_calendar(self, update: Update, context) -> None:
        op = update.message.text.lower()
        if op not in ['h', 'a']:
            await update.message.reply_text('Opção inválida!')
            return ConversationHandler.END
        # Aqui você pode continuar o processamento do resultado, se necessário
        
        # Armazene a opção do calendário no contexto
        context.user_data['calendar_option'] = op

        return self.CALENDAR_USUARIO
    
    async def get_usuario_calendar(self, update: Update, context):

        def obter_icone_status(status):
                if status == "No prazo":
                    icone = '🟢'
                elif status == "Atraso":
                    icone = '🔴'
                elif status == 'Futuro':
                    icone = '⚪'
                return icone
        
        op = update.message.text.lower()
        context.user_data['calendar_option'] = op
        if op not in ['h', 'a']:
            await update.message.reply_text('❌ *Opção inválida!\*',parse_mode='MarkdownV2')
            return ConversationHandler.END
        
        await update.message.reply_text('🚀     *Vamos iniciar\!*',parse_mode='MarkdownV2')

        usuario = context.user_data.get('authenticated_user')
        option = context.user_data.get('calendar_option')
        if option == 'h':
            day = 'de hoje'
        elif option == 'a':
            day = 'de amanhã'
        await update.message.reply_text(f'🔎   Verificando a agenda {day} de {usuario} ...')
        await update.message.reply_text(f'⏳   Verificando\.\.\.   ⏳',parse_mode='MarkdownV2')
        
        agenda = obter_agenda_usuario(usuario, option)
        # imprimir agenda para verificação de vetor
        print(f'>>> AGENDA: {agenda}')
        try:
            if agenda == []:
                await update.message.reply_text('📆✅  *Nenhum evento encontrado na agenda\!*',parse_mode='MarkdownV2')
            no_prazo = []
            atraso = []
            futuro = []
            for evento in agenda:
                id = evento[0]
                data = evento[1]
                status = evento[2]
                concluido_em = evento[3]
                Tipo_de_Atividade = evento[4]
                Responsavel = evento[5]
                Criado_por = evento[6]
                cliente = evento[7]

                # aplicar "semáfaro" '⚪🟢🔴' no status da atividade
                icone_status = obter_icone_status(status)
                def substituir_caracteres(texto):
                    try:
                        texto = texto.replace('-', '\-')
                        texto = texto.replace('.', '\.')
                        texto = texto.replace('(', '\(')
                        texto = texto.replace(')', '\)')
                    except Exception as error: print(error)
                    return texto 
                
                Tipo_de_Atividade = substituir_caracteres(Tipo_de_Atividade)
                cliente = substituir_caracteres(cliente)
                Criado_por = substituir_caracteres(Criado_por)

                evento_menu = (  
                                f"🚨    *{Tipo_de_Atividade}* \n" 
                                f"🆔    *{id}*              {icone_status} *{status}* \n\n"
                                f"🌞 *Cliente:* {cliente}\n\n"

                                f"🗣️ *Criado por:* {Criado_por}\n\n"
                                # f"👤 Responsável: {Responsavel}\n\n"
                                f"🗓️ *Data:* {data}      \n"
                                # f"✔️ Concluído em: {concluido_em}\n\n"
                                
                                )
                # await update.message.reply_text(evento_menu, parse_mode='MarkdownV2')
                
                if status == 'No prazo':
                    no_prazo.append(evento_menu)
                elif status == 'Atraso':
                    atraso.append(evento_menu)
                elif status == 'Futuro':
                    futuro.append(evento_menu)

            # Atraso
            for evento_menu in atraso:
                await update.message.reply_text(evento_menu, parse_mode='MarkdownV2')  

            # No prazo
            for evento_menu in no_prazo:
                await update.message.reply_text(evento_menu, parse_mode='MarkdownV2')
            
            # Futuro
            for evento_menu in futuro:
                await update.message.reply_text(evento_menu, parse_mode='MarkdownV2')   
   
        except Exception as error: print('>>> [ERROR]:', error)
     
        return ConversationHandler.END
    
    async def cancel_get_calendar(self, update: Update, context) -> int:
        await update.message.reply_text('Operação cancelada')
        return ConversationHandler.END
    
    def start_kin(self):
        self.application = Application.builder().token(self.TOKEN).build()

        # Commands - answer in Telegram
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CommandHandler('track', self.monitor_command))
        self.application.add_handler(CommandHandler('stop', self.stop_command))
        self.application.add_handler(CommandHandler('action', self.action))
        self.application.add_handler(CommandHandler('crm_score', self.crm_score))
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('calendar', self.calendar), CommandHandler('login', self.login)],
            states={
                self.LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_id_usuario)],
                self.CALENDAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_option_calendar)],
                self.CALENDAR_USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_usuario_calendar)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_get_calendar)]
        )

        self.application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        self.application.run_polling()