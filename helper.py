# import's:
import pygame
import os
# import one code:
import mainClass


# take inputs and call the matching class
def inputs_for_cmd() -> None:
    """
    will create and call a object Chess Server/Client
    """
    is_host: bool
    number_of_equals: int = 50

    try:
        print('=' * number_of_equals)

        # Server or Client
        is_host_i: str = input('|| Start a game OR join an existing game -> [s/j]').lower()
        if not is_host_i: inputs_for_cmd()
        if is_host_i not in 'sj': inputs_for_cmd()

        is_host = True if is_host_i == 's' else False

        # HOST
        _host: str = input('|| Host: str => ')
        HOST = None if _host == "" else _host

        # PORT
        _port: str = input('|| Port: int => ')
        PORT = None if _port == "" else int(_port)

        print('=' * number_of_equals)

        """
        Prevents creating a object with not set variables
        might be referenced before assignment
        """
        if HOST is None or PORT is None:
            # create targeted object
            xx = mainClass.ServerClass() if is_host else mainClass.ClientClass()
            # call created object
            xx()

        else:
            # create targeted object
            xx = mainClass.ServerClass(HOST, PORT) if is_host else mainClass.ClientClass(HOST, PORT)
            # call created object
            xx()

    except ValueError as err:
        print(f'Value Error. Error: {err}')


# take inputs and call the matching class
def inputs_from_gui(host: str, port: int, is_host: bool) -> None:
    try:
        if not isinstance(host, str) and not isinstance(port, int) and not isinstance(is_host, bool):
            raise Exception('input error')

        xx = mainClass.ServerClass(host, port) if is_host else mainClass.ClientClass(host, port)
        xx()
    except Exception as err:
        print(f"Wrong input. Error: {err}")


# pygame
def load_images(IMAGES: dict, FIELD: int) -> None:
    """
    load the images which are used for displaying the pieces
    IMAGES['wP'] will reverence the image wP.png
    :type IMAGES: dict
    :type FIELD: int
    """
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(os.path.join("resources-images", f"{piece}.png")),
                                               (FIELD, FIELD))


# pygame
class Move:
    _start_sq: tuple
    _end_sq: tuple
    _board: list

    def __repr__(self) -> dict:
        """
        :return: a dict with a tuple of the starting square ending square and the move notation
        """
        return dict(
            start_sq=(self.start_row, self.start_col),
            end_sq=(self.end_row, self.end_col),
            notation=self.notation
        )

    def __init__(self, _start_sq, _end_sq, _board):
        """
        stores the information of the current move
        :param _start_sq: tuple which contain the x and y coordinates of the start square (from location)
        :param _end_sq: tuple which contain th x and y coordinates of the end square (to location)
        :param _board: the current board as a nested list (matrix)
        """
        self.start_row = _start_sq[0]
        self.start_col = _start_sq[1]
        self.end_row = _end_sq[0]
        self.end_col = _end_sq[1]
        self.piece_moved = _board[self.start_row][self.start_col]
        self.piece_captured = _board[self.end_row][self.end_col]
        
    @property
    def notation(self) -> str:
        """
        will create a matching notation for the current move
        the notation will be a str because it simplifies sending it via a socket connection
        example: "2|1#3|1"
        :return: str notation
        """
        return "{0}|{1}#{2}|{3}".format(self.start_row, self.start_col, self.end_row, self.end_col)


# pygame
def make_move(board: list, _move: object) -> list:
    """
    update the current board by manipulating it with the current move object
    :param board: current board (nested list)
    :param _move: object move contains the current move
    :return: the current game-board as a nested list (matrix)
    """
    # started location is mow empty
    board[_move.start_row][_move.start_col] = "--"

    # target should now be overwritten by the pic
    board[_move.end_row][_move.end_col] = _move.piece_moved

    return board


# pygame
def redraw_window(WINDOW, DIMENSIONS: int, FIELD: int, IMAGES: dict, GAME_BOARD: list) -> None:
    """
    updates the window after a move was made
    - put the FIELDS on the gui
    - put the game pieces on the FIELDS at there current location
    :param IMAGES: list of all pic images
    :param FIELD: size of a field
    :param DIMENSIONS: number of board dimensions
    :param WINDOW: gui of pygame
    :param GAME_BOARD: the current game board
    """
    # you can either go with color names or with there rgb values
    colors = [pygame.Color(255, 255, 255, 255), pygame.Color('gray')]

    for x in range(DIMENSIONS):
        for y in range(DIMENSIONS):

            # draw square
            color = colors[((x + y) % 2)]
            pygame.draw.rect(WINDOW, color, pygame.Rect(y * FIELD, x * FIELD, FIELD, FIELD))

            # draw pieces
            game_piece = GAME_BOARD[x][y]
            if game_piece != "--":
                WINDOW.blit(IMAGES[game_piece], pygame.Rect(y * FIELD, x * FIELD, FIELD, FIELD))

    pygame.display.update()


# socket
def send_massage(txt: str, socket_connection) -> None:
    """
    sends the massage txt to the opponent via a socket connection
    it will contain the current move information -> see above Move.notation
    :param socket_connection: socket connection object
    :param txt: massage which will be send via the socket connection
    """
    socket_connection.send(txt.encode('utf-8'))


# socket
def received_massage(socket_connection, buffer: int) -> list:
    """
    revive the current move of the opponent
    it will be formatted like this -> '3|2#4|5' -> see above Move.notation
    :param socket_connection: socket connection object
    :type buffer: int  witch resembles the max traffic the server can/will handle at ones
    :return: the current move as a list of tuples start end square withe (x,y)
    """
    # get the massage
    received_str_massage = socket_connection.recv(buffer).decode('utf-8')
    received_list_massage = received_str_massage.split('#')

    # format the massage in a list of two tuples
    return_value_list = [tuple([int(e) for e in received_list_massage[0].split("|")]),
                         tuple([int(e) for e in received_list_massage[1].split("|")])]

    return return_value_list
