import random
import ssl

import toml
import socket


def send(irc: ssl.SSLSocket, message: str):
    irc.send(bytes(f'{message}\r\n', 'UTF-8'))


def send_chat(irc: ssl.SSLSocket, message: str, channel: str):
    send(irc, f'PRIVMSG #{channel} :{message}')


def send_pong(irc: ssl.SSLSocket):
    send(irc, 'PONG :tmi.twitch.tv')


def handle_chat(irc: ssl.SSLSocket, raw_message: str):
    components = raw_message.split()

    user, host = components[0].split('!')[1].split('@')
    channel = components[2]
    message = ' '.join(components[3:])[1:]


    if message.startswith('!'):
        message_components = message.split()
        command = message_components[0][1:]

        if command == 'dice':
            random_number = random.randint(1, 6)
            send_chat(irc, f'{user}, deine Zahl ist: {random_number}', channel)


    print(f'user {user} sent message {message}')



if __name__ == '__main__':
    config = toml.load('config.toml')

    bot_username = config['bot_username']
    channel_name = config['channel_name']
    oauth_token = config['oauth_token']

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    irc = context.wrap_socket(socket)

    irc.connect(('irc.chat.twitch.tv', 6697))

    send(irc, f'PASS oauth:{oauth_token}')
    send(irc, f'NICK {bot_username}')
    send(irc, f'JOIN #{channel_name}')

    while True:
        data = irc.recv(1024)
        raw_message = data.decode('UTF-8')

        for line in raw_message.splitlines():
            if line.startswith('PING :tmi.twitch.tv'):
                send_pong(irc)
            else:
                components = line.split()
                command = components[1]

                if command == 'PRIVMSG':
                    handle_chat(irc, line)
