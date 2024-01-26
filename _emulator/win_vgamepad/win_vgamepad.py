#!/usr/bin/env python3

import socket
import vgamepad as vg

gamepad = vg.VX360Gamepad()
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


def checkbit(inindata, mask):
    """Do a bitwise"""


    inindata = int.from_bytes(inindata)

    # mybytes = bytes([inindata[0] | mask[0]])
    # mask = bytes(mask)
    # print(myint)

    result = inindata & mask

    print("bytes in: " + str(inindata) + " Mask: " + str(mask) + " Result: " + str(result))

    return result


def press_buttons(indata):
    """Bitwise compare to the socked and press/release depending"""




    print("New input: " + str(int.from_bytes(indata)))

    if checkbit(indata, 512):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)

    if checkbit(indata, 256):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

    if checkbit(indata, 128):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

    if checkbit(indata, 64):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)

    if checkbit(indata, 32):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)

    if checkbit(indata, 16):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

    if checkbit(indata, 8):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)

    if checkbit(indata, 4):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)

    if checkbit(indata, 2):
        # print("pressing")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    else:
        # print("releasing")
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

    if checkbit(indata, 1):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)


while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    while True:
        # Receive and print data from the client
        data = client_socket.recv(2)
        # print(f"Received data: {data}")
        press_buttons(data)

    # Close the connection with the client
    client_socket.close()
