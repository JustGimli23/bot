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


def start_markup():
    item1 = KeyboardButton(text='Chats')
    item2 = KeyboardButton(text='Message')

    row = KeyboardButtonRow([
        item1, item2
    ])

    markup = ReplyKeyboardMarkup(
        [row], resize=True, single_use=True, placeholder='Этот бот создан для индивидуального использования')

    return markup
