import asyncio
from datetime import datetime
import websockets

connect_clients = {}
users = {}

# Префиксы для сообщений
PRIVATE_PREFIX = "[ЛС]"
SYSTEM_PREFIX = "[СИСТЕМА]"
HELP_PREFIX = "[ПОМОЩЬ]"
USERS_PREFIX = "[ПОЛЬЗОВАТЕЛИ]"


async def send_help(websocket):
    help_text = f"""
{HELP_PREFIX}
=== Доступные команды ===
/help - показать это сообщение
/users - список пользователей онлайн
/private <username> <message> - отправить личное сообщение
/exit - выйти из чата
"""
    await websocket.send(help_text)


async def send_users_list(websocket):
    if users:
        users_list = "\n".join([f"• {username}" for username in users.keys()])
        message = f"{USERS_PREFIX}\n=== Пользователи онлайн ({len(users)}) ===\n{users_list}"
    else:
        message = f"{USERS_PREFIX}\nНет пользователей онлайн"
    await websocket.send(message)


async def send_private_message(sender_ws, sender_name, command_parts):
    if len(command_parts) < 3:
        await sender_ws.send(f"{SYSTEM_PREFIX} Использование: /private username сообщение")
        return

    recipient_name = command_parts[1]
    message_text = ' '.join(command_parts[2:])

    if recipient_name not in users:
        await sender_ws.send(f"{SYSTEM_PREFIX} Пользователь '{recipient_name}' не найден или не в сети")
        return

    if recipient_name == sender_name:
        await sender_ws.send(f"{SYSTEM_PREFIX} Нельзя отправить сообщение самому себе")
        return

    recipient_ws = users[recipient_name]

    timestamp = datetime.now().strftime("%H:%M:%S")
    await recipient_ws.send(f"{PRIVATE_PREFIX} от {sender_name} ({timestamp}): {message_text}")

    await sender_ws.send(f"{SYSTEM_PREFIX} ✓ Сообщение для {recipient_name} отправлено")


async def broadcast(message, sender_ws=None):
    disconnected = []
    current_time = datetime.now().strftime("%H:%M:%S")

    for ws, username in list(connect_clients.items()):
        if ws == sender_ws:
            continue
        try:
            if sender_ws and sender_ws in connect_clients:
                sender_name = connect_clients[sender_ws]
                await ws.send(f"{sender_name} ({current_time}): {message}")
            else:
                await ws.send(f"{SYSTEM_PREFIX} {message}")
        except:
            disconnected.append(ws)
    for ws in disconnected:
        await handle_disconnect(ws)


async def handle_disconnect(websocket):
    if websocket in connect_clients:
        username = connect_clients[websocket]
        connect_clients.pop(websocket, None)
        users.pop(username, None)
        await broadcast(f"🔴 {username} вышел из чата")
        print(f"{username} отключился")


async def server(websocket):
    await websocket.send(f"{SYSTEM_PREFIX} Введите ваше имя: ")

    try:
        username = await asyncio.wait_for(websocket.recv(), timeout=30)
        username = username.strip()

        if username in users:
            await websocket.send(f"{SYSTEM_PREFIX} Это имя уже занято. Отключение...")
            return

        if not username:
            await websocket.send(f"{SYSTEM_PREFIX} Имя не может быть пустым. Отключение...")
            return
        connect_clients[websocket] = username
        users[username] = websocket
        await websocket.send(f"{SYSTEM_PREFIX} Добро пожаловать, {username}! Введите /help для списка команд")
        await broadcast(f"🔵 {username} присоединился к чату")
        print(f"{username} подключился")
        async for message_data in websocket:
            message = message_data.strip()

            if not message:
                continue

            print(f"{username}: {message}")

            # Обработка команд
            if message.startswith('/'):
                command_parts = message.split()
                command = command_parts[0].lower()

                if command == '/help':
                    await send_help(websocket)

                elif command == '/users':
                    await send_users_list(websocket)

                elif command == '/private':
                    await send_private_message(websocket, username, command_parts)

                elif command == '/exit':
                    await websocket.send(f"{SYSTEM_PREFIX} До свидания!")
                    break

                else:
                    await websocket.send(f"{SYSTEM_PREFIX} Неизвестная команда: {command}. Введите /help для помощи")

            else:
                await broadcast(message, sender_ws=websocket)

    except asyncio.TimeoutError:
        await websocket.send(f"{SYSTEM_PREFIX} Время ожидания истекло")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await handle_disconnect(websocket)


async def main():
    async with websockets.serve(server, "localhost", 8766):
        print("✅ Сервер запущен на ws://localhost:8766")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())