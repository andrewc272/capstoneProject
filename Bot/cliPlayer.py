from bot import Bot

class cliClient(Bot):
    def get_message(self, chats=[]) -> str:
        # show the user the chats
        for chat in chats:
            print(chat)
        # Promt to respond
        message = input("What would you like to send (or hit enter to skip)?")

        if message == "":
            return None
        return message


if __name__ == '__main__':
    client = cliClient("cli")
    client.run()
