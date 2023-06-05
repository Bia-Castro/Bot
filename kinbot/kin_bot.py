import logging
import asyncio

from .verify_site import VerifySite

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, Updater, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class KinBot():
    """
    KinBot
    """
    PASSWD_ACCESS = 'kinsol@0106'
    TOKEN = '6251978006:AAGeTPZuLrFTNg3BpZ_mcIjaCsqpvFFXg0Y'
    application = None
    monitor_flag = False
    task = None
    LOGIN = range(1)
    user_list = []
    verify_settings = {
        'user_name': 'kinsol.servidor@gmail.com',
        'user_passwd': 'kinsolbot10',
        'verify_time': 15,
    }
    
    async def user_is_authenticated(self, update: Update) -> bool:
        user_id = update.message.from_user.id
        is_authenticated = user_id in self.user_list
        if not is_authenticated:
            await update.message.reply_text('Você deve realizar a autenticação\nDigite: /login.')
            
        return is_authenticated
    
    async def start(self, update: Update, context) -> None:
        """Send a message when the command /start is issued."""
        user = update.message.from_user
        await update.message.reply_text(f'Olá {user.first_name} {user.last_name} 👋, bom te ver!')
        
        if not await self.user_is_authenticated(update):
            return
        
    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Autenticar/Logar usuário"""
        await update.message.reply_text('Por favor, envie a senha:\nPara cancelar o login digite: /cancel.')
        return self.LOGIN
        
    async def get_passwd(self, update: Update, context) -> int: 
        passwd = update.message.text
        if passwd != self.PASSWD_ACCESS:
            await update.message.reply_text("Senha incorreta.")
            return
        
        user_id = update.message.from_user.id
        self.user_list.append(user_id)
        await update.message.reply_text("Usuário autenticado com sucesso.")

        return ConversationHandler.END
    
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
            result = driver.verify_site()
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
        result = driver.action_site()
        if not result['response']:
            print('>>> [INFO]: Não foi possível realizar a interação!')
            await update.message.reply_text('❌ Não foi possível realizar a interação...')
            return
        
        print(f'>>> [INFO]: Interaçaõ realizada com sucesso!\nitem verificado: {result["title"]}.')
        await update.message.reply_text(f'Interaçaõ realizada com sucesso!\nitem verificado: {result["title"]}.')
        return
    
    async def crm_score(self, update, context) -> None:
        """
        """
        if not await self.user_is_authenticated(update):
            return

        print('>>> [INFO]: Filtrando score...')
        await update.message.reply_text('Filtrando score...')
        
        driver = VerifySite(**self.verify_settings)
        score_list = driver.score_site()
        
        if not len(score_list):
            print('>>> [INFO]: nenhum score localizado.')
            await update.message.reply_text('nenhum score localizado.')
            return

        str_score = '\n'.join(score_list)
        
        print('>>> [INFO]: Lista de Leads por etapas:\n', str_score)
        await update.message.reply_text(f'📊Lista de Leads por etapas:\n{str_score}')
        
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
            entry_points=[CommandHandler('login', self.login)],
            states={
                self.LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_passwd)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_get_passwd)]
        )

        # adicionar o ConversationHandler ao updater
        self.application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        self.application.run_polling()