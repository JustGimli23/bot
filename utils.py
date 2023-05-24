from database import get_name_chats


async def get_chat_id(data: dict, dialogs: list):
    name_chats = get_name_chats(data['user_id'], data['ids'])

    ids = []

    async for name in dialogs:
        if name.name in name_chats:
            ids.append(name.id)

    if ids == []:
        return [], 'Извините, нет чатов с такими именами у вас в диалогах'
    else:

        return ids, 'Успешно отправлено'
