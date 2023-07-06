#!/usr/bin/python
from __future__ import annotations

import socket
import threading
from settings import Data, Instructions, PORT, END

class Board:
    ...

    def serialize(self) -> bytes:
        ...

    @property
    def is_mate(self) -> bytes:
        ...

    @property
    def white_won(self) -> bytes:
        ...

board = Board()
client_lock = threading.Lock()
clients_connected: list[socket.socket] = []


def broadcast(data: Data) -> None:
    [ client.send(data.serialize()) for client in clients_connected]

def validate_move(move: str) -> bool:
    ...

def perform_move(board: Board, move: str) -> None:
    ...

def handle_client(client_socket: socket.socket, client_address: ...) -> None:
    with client_lock:
        clients_connected.append(client_socket)

    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        packet = Data.deserialize(data)
        print(packet.data)
        if packet.instructions == Instructions.CHAT:
            broadcast(packet)
            print('sending')

        if packet.instructions == Instructions.MOVE:
            move = packet.data.decode()
            if not validate_move(move):
                print(f'invalid move: {move}')
                response = Data(Instructions.INVALID_MOVE, b"invalid move")
                client_socket.send(response.serialize())
                pass

            perform_move(board, move)
            if board.is_mate:
                broadcast(Data(Instructions.MATE, (END.WHITE_MATE if board.white_won else END.BLACK_MATE).to_bytes()))
            else:
                broadcast(Data(Instructions.BOARD, board.serialize()))

    with client_lock:
        clients_connected.remove(client_socket)
        print(f'client with ip: {client_address} has been disconnected')

    client_socket.close()

def make_socket_run(port: int = PORT) -> None:
    print('starting...')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(10)
    while True:
        client_connection, client_address = server_socket.accept()
        thread = threading.Thread(target = handle_client, args=[client_connection, client_address])
        thread.start()


if __name__ == "__main__":
    make_socket_run()
