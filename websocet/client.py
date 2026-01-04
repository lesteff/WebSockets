import asyncio
import websockets


class ChatClient:
    def __init__(self):
        self.websocket = None
        self.username = None
        self.running = True

    def format_message(self, message):
        if message.startswith("[ЛС]"):
            return f"\n📩 {message[4:]}"
        elif message.startswith("[СИСТЕМА]"):
            return f"\n⚡ {message[9:]}"
        elif message.startswith("[ПОМОЩЬ]"):
            return f"\n{message}"
        elif message.startswith("[ПОЛЬЗОВАТЕЛИ]"):
            return f"\n{message}"
        else:
            return f"\n{message}"

    async def connect(self, uri):
        self.websocket = await websockets.connect(uri)

        welcome = await self.websocket.recv()
        print(self.format_message(welcome), end="")

        self.username = input()
        await self.websocket.send(self.username)
        response = await self.websocket.recv()
        print(self.format_message(response))

    async def sender(self):
        while self.running:
            try:
                message = await asyncio.get_event_loop().run_in_executor(None, input, ">>> ")

                if not message.strip():
                    continue

                await self.websocket.send(message.strip())

                if message.strip().lower() == '/exit':
                    self.running = False
                    break

            except (asyncio.CancelledError, EOFError, KeyboardInterrupt):
                self.running = False
                break
            except Exception as e:
                print(f"\nОшибка отправки: {e}")
                break

    async def receiver(self):
        while self.running:
            try:
                message = await self.websocket.recv()
                print(self.format_message(message), end='')
                print(">>> ", end='', flush=True)

            except websockets.exceptions.ConnectionClosed:
                print("\nСоединение закрыто")
                self.running = False
                break
            except Exception as e:
                print(f"\nОшибка получения: {e}")
                self.running = False
                break

    async def run(self, uri):
        try:
            await self.connect(uri)
            await asyncio.gather(
                self.sender(),
                self.receiver()
            )
        except KeyboardInterrupt:
            print("\nВыход...")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()


async def main():
    client = ChatClient()
    await client.run("ws://localhost:8766")


if __name__ == "__main__":
    asyncio.run(main())