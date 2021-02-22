# import's:
from socket import socket as sock_class, AF_INET as IPv4, SOCK_STREAM as TCP, error as sock_err
import pygame
# import one code:
import helper

pygame.init()

BOARD_DIMENSIONS = 8
WIDTH = HEIGHT = 400  # ideally a multiple of BOARD_DIMENSIONS
FIELD = WIDTH // BOARD_DIMENSIONS
IMAGES = {}  # dict of all game characters


class MainChessClass:
    host: str  # server_ipv4
    port: int  # server_port

    @property
    def __repr__(self) -> dict:
        return self.__dict__

    def __init__(self, host='127.0.0.1', port=9090):
        # socket
        self.host = host
        self.port = port
        self._buffer = 1024

        # pygame
        self._fps = 1
        self._clock = pygame.time.Clock()
        self._window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.move_history = []

        # prepare pygame
        pygame.display.set_caption("Chess - by Felix-py - v1.0.0")
        helper.load_images(IMAGES, FIELD)

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        """
        check whether the ip is formatted correctly
        :param value: ip_v4 address as a str
        :return: None
        """
        ip_v4_int_list = [int(e) for e in value.split(".")]
        ip_v4_int_list.sort(reverse=True)

        if len(ip_v4_int_list) == 4 and ip_v4_int_list[0] <= 255:
            self._host = value
        else:
            raise ValueError('%s is not a valid ip_v4 address' % value)

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int) -> None:
        """
        check if the port is a valid port
        :param value: port
        """
        _well_known_ports = 1023
        if isinstance(value, int) and value > _well_known_ports:
            self._port = value
        else:
            raise ValueError('%s is either a well known port or has a wrong format' % value)

    def gameplay(self, _socket_object: object) -> None:
        """
        the gameplay will handle the game gui, it will draw the window, handle the user interactions and then
        communicate withe the opponent via a socket connection
        :param _socket_object: the socket connection object of the current player
        :return: None
        """
        print('gameplay...')
        # to  keep track of the selected fields the user selected in the gui
        selected_field = ()
        fields_list = []

        game_over = False
        while not game_over:
            # start the clock to keep track of the fps
            self._clock.tick(self._fps)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    game_over = True
                    continue

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # get the location of mouse
                    print("recognised a mouse click...")
                    location = pygame.mouse.get_pos()
                    selected_col = location[0] // FIELD
                    selected_row = location[1] // FIELD

                    if selected_field == (selected_row, selected_col):
                        # if the current and last field selected are identical -> reset
                        selected_field = ()
                        fields_list = []
                    else:
                        # add the selected field to the tuple and list
                        selected_field = (selected_row, selected_col)
                        fields_list.append(selected_field)

                    if len(fields_list) > 1:
                        # make the move if two fields selected
                        current_move = helper.Move(fields_list[0], fields_list[1], self.board)
                        self.board = helper.make_move(self.board, current_move)

                        # reset the selected field tuple and list
                        selected_field = ()
                        fields_list = []

                        # send the move to the opponent
                        helper.send_massage(current_move.notation, _socket_object)
                        helper.redraw_window(self._window, BOARD_DIMENSIONS, FIELD, IMAGES, self.board)

                        # receive the move of the opponent
                        received_list = helper.received_massage(_socket_object, self._buffer)

                        # make the opponents move
                        opponent_move = helper.Move(received_list[0], received_list[1], self.board)
                        self.board = helper.make_move(self.board, opponent_move)

            # keep track of the fps
            self._clock.tick(self._fps)
            helper.redraw_window(self._window, BOARD_DIMENSIONS, FIELD, IMAGES, self.board)
            pygame.display.flip()


class ServerClass(MainChessClass):
    _host: str  # server_ipv4
    _port: int  # server_port

    @property
    def __repr__(self) -> dict:
        return self.__dict__

    def __init__(self, host: str = '127.0.0.1', port: int = 9090):
        # __init__ of the parent class
        super(ServerClass, self).__init__(host, port)
        self._server_socket = self.socket_connection()

    def socket_connection(self) -> object:
        if server := sock_class(IPv4, TCP): server.bind((self.host, self.port))
        server.listen(1)  # chess is a 1v1 game so the server only accept one client at a time
        print('Listening for an inbound connection ...')
        client, address = server.accept()
        print(f'Connected to: {address}.')

        return client

    def __call__(self, *args, **kwargs):
        self.gameplay(self._server_socket)


class ClientClass(MainChessClass):
    _host: str  # server_ipv4
    _port: int  # server_port

    @property
    def __repr__(self) -> dict:
        return self.__dict__

    def __init__(self, host: str = '127.0.0.1', port: int = 9090):
        # init of parent class
        super(ClientClass, self).__init__(host, port)
        self._client_socket = self.socket_connection()

    def socket_connection(self) -> object:
        if client := sock_class(IPv4, TCP): client.connect((self.host, self.port))
        return client

    def __call__(self, *args, **kwargs):
        """
        because the server/host makes the first move the client hase to wait and react to that first move
        before entering the game mode
        """
        # get the first move of opponent before entering the gameplay loop underneath
        received_list = helper.received_massage(self._client_socket, self._buffer)
        opponent_move = helper.Move(received_list[0], received_list[1], self.board)
        self.board = helper.make_move(self.board, opponent_move)

        # enter the gameplay state
        self.gameplay(self._client_socket)
