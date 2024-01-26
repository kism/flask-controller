#!/usr/bin/env python3

import socket
import pyautogui

pyautogui.PAUSE = 1/120

SERVER = None
HOST = "localhost"
PORT = 5001


# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((HOST, PORT))

# Set the maximum number of queued connections
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")


def iterate_bits(num):
    """Make a gross dict representing 10 bits"""
    inputarray = []
    binary_representation = bin(num)[2:]  # Convert the integer to binary and remove the '0b' prefix
    binary_representation = binary_representation.zfill(10)  # Assuming 32-bit integers for illustration

    for bit_position, bit_value in enumerate(binary_representation[::-1]):
        # print(f'Bit at position {bit_position}: {bit_value}')
        if bit_value == "0":
            bit_value = False
        else:
            bit_value = True
        inputarray.append(bit_value)

    return inputarray



def press_buttons(indata):
    """Bitwise compare to the socked and press/release depending"""

    myint = int.from_bytes(indata, "little")

    inputarray = iterate_bits(myint)

    # print(inputarray)


    # print("New input: " + str(int.from_bytes(indata)))

    if inputarray[9]:
        pyautogui.keyDown("q")
    else:
        pyautogui.keyUp("q")

    if inputarray[8]:
        pyautogui.keyDown("w")
    else:
        pyautogui.keyUp("w")

    if inputarray[7]:
        pyautogui.keyDown("e")
    else:
        pyautogui.keyUp("e")

    if inputarray[6]:
        pyautogui.keyDown("r")
    else:
        pyautogui.keyUp("r")

    if inputarray[5]:
        pyautogui.keyDown("t")
    else:
        pyautogui.keyUp("t")

    if inputarray[4]:
        pyautogui.keyDown("y")
    else:
        pyautogui.keyUp("y")

    if inputarray[3]:
        pyautogui.keyDown("u")
    else:
        pyautogui.keyUp("u")

    if inputarray[2]:
        pyautogui.keyDown("i")
    else:
        pyautogui.keyUp("i")

    if inputarray[1]:
        # print("pressing")
        pyautogui.keyDown("o")
    else:
        # print("releasing")
        pyautogui.keyUp("o")

    if inputarray[0]:
        pyautogui.keyDown("p")
    else:
        pyautogui.keyUp("p")


while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    try:
        while True:
            # Receive and print data from the client
            data = client_socket.recv(2)
            # print(f"Received data: {data}")
            press_buttons(data)
    except:
        pass

    # Close the connection with the client
    client_socket.close()
