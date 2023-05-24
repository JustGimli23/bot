import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import (
    PeerChannel,
    PeerUser,
    ReplyKeyboardMarkup,
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButton,
    KeyboardButtonUrl,
    KeyboardButtonCallback
)
from database import show_chats, set_chats,\
    create_chat, del_chat, show_chats_id
from utils import get_chat_id
from markup import start_markup
import time

api_id = 12009119
api_hash = '1f18072879f776ab016bdd88e4ccf818'

API_TOKEN = '6118373344:AAGptcWacRXTSkePlbW6Q1X2vF72zcoerHY'

bot = TelegramClient('anon', api_id, api_hash)
client = TelegramClient('anon1', api_id, api_hash,
                        timeout=1)


@bot.on(events.NewMessage(pattern='/start'))
async def handler(message):
    create_chat(message.chat.id)

    text = 'Hello this is sender bot'

    await bot.send_message(message.chat.id, message=text, buttons=start_markup())


@bot.on(events.NewMessage(pattern='Chats'))
async def handler(message):
    res = show_chats(message.chat.id)

    markup = ReplyKeyboardMarkup(
        [KeyboardButtonRow(
            [
                KeyboardButton('Add Chat'),
                KeyboardButton('Delete Chat')
            ]
        )], resize=True)

    await bot.send_message(message.chat.id, message=f'Чаты:\n{res}', buttons=markup)


@bot.on(events.NewMessage(pattern='Add Chat'))
async def handler(message):
    await bot.send_message(message.chat.id, 'Введите имя чатов:')
    bot.add_event_handler(handler1, events.NewMessage(
        incoming=True, pattern=r'(?!Add\sChat)'))


async def handler1(message):
    chats = [i for i in message.text.strip().split('\n')]
    set_chats(message.chat.id, chats)
    await bot.send_message(message.chat.id, 'Успешно добавлено. Введите сообщение.')
    bot.remove_event_handler(handler1)
    bot.add_event_handler(handler_mes, events.NewMessage(
        incoming=True, pattern=r'^(?!Успешно\sдобавлено.\sВведите\sсообщение.)'))


@bot.on(events.NewMessage(pattern='Delete Chat'))
async def handler(message):
    markup = ReplyInlineMarkup(
        [
            KeyboardButtonRow([
                KeyboardButtonCallback(text='ALL', data=b'del_all')
            ])
        ]
    )
    await bot.send_message(message.chat.id, 'Введите id чатов через пробел:', buttons=markup)

    bot.add_event_handler(handler_del, events.NewMessage(
        incoming=True, pattern=r'^(?!Delete Chat)'))


@bot.on(events.CallbackQuery(data=b'del_all'))
async def handler(message):
    del_chat(message.chat.id, show_chats_id(message.chat.id))
    await bot.send_message(message.chat.id, 'Успешно удалено', buttons=start_markup())
    bot.remove_event_handler(handler_del)


async def handler_del(message):
    inds = [int(i) for i in message.text.strip().split(' ')]
    del_chat(message.chat.id, inds)

    await bot.send_message(message.chat.id, 'Успешно удалено', buttons=start_markup())
    bot.remove_event_handler(handler_del)


@bot.on(events.NewMessage(pattern='Message'))
async def handler(message):
    await bot.send_message(message.chat.id, 'Введите ваше сообщение')
    bot.add_event_handler(handler_mes, events.NewMessage(
        incoming=True, pattern=r'^(?!Message)'))


async def handler_mes(message):
    global data

    data = {'message': message.text}
    data['isId'] = False

    text = show_chats(message.chat.id)

    res = 'Введите id чата:\n' + text

    markup = ReplyInlineMarkup([
        KeyboardButtonRow(
            [
                KeyboardButtonCallback(text='ALL', data=b'all', )
            ]
        )
    ], )

    await bot.send_message(message.chat.id, message=res, buttons=markup)

    bot.remove_event_handler(handler_mes)
    bot.add_event_handler(handler_id, events.NewMessage)


@bot.on(events.CallbackQuery(data=b'all'))
async def handler(message):
    data['ids'] = show_chats_id(message.chat.id)
    data['user_id'] = message.chat.id

    markup = ReplyKeyboardMarkup([
        KeyboardButtonRow([
            KeyboardButton(text='Set period'),
            KeyboardButton(text='Send Now')

        ])
    ], resize=True)

    await bot.send_message(message.chat.id, message='Выберите опцию', buttons=markup)
    bot.remove_event_handler(handler_id)


async def handler_id(message):
    data['ids'] = [int(i) for i in message.text.strip().split(' ')]
    data['user_id'] = message.chat.id

    markup = ReplyKeyboardMarkup([
        KeyboardButtonRow([
            KeyboardButton(text='Set period'),
            KeyboardButton(text='Send Now')

        ])
    ], resize=True)

    await bot.send_message(message.chat.id, message='Выберите опцию', buttons=markup)
    bot.remove_event_handler(handler_id)


@bot.on(events.NewMessage(pattern='Set period'))
async def handler(message):
    await bot.send_message(message.chat.id, 'Задайте периодичность в минутах')
    bot.add_event_handler(handler_period, events.NewMessage(
        pattern=r'^(?!Set\speriod)'))


@bot.on(events.NewMessage(pattern='/set'))
async def handler(message):
    data['set'] = False

    await bot.send_message(message.chat.id, 'Рассылка остановлена', buttons=start_markup())


async def handler_period(message):
    data['period'] = float(message.text)
    data['set'] = True

    bot.remove_event_handler(handler_period)
    await bot.send_message(message.chat.id, f'Сообщения каналам будут отправляться каждые {data["period"]} минут чтобы отменить оправку введите /set')
    await shedule_send(data['period'])


@bot.on(events.NewMessage(pattern='Send Now'))
async def handler(message):

    await bot.send_message(message.chat.id, message=await client_task(), buttons=start_markup())


async def client_task(i):
    print(f'succesufuly send-{i}')
    try:
        await asyncio.wait_for(client.send_message(i, data['message']), timeout=10)
    except asyncio.TimeoutError:
        pass


async def shedule_send(sec: int):
    dialogs = client.iter_dialogs()
    ids, mes = await get_chat_id(data, dialogs)
    ids.pop()

    while data['set']:
        tasks = []
        for user_id in ids:
            task = asyncio.create_task(client_task(user_id))
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)


async def main():
    await bot.start(bot_token=API_TOKEN)
    await client.start()

    await asyncio.gather(bot.run_until_disconnected(), client.run_until_disconnected())


asyncio.run(main())
