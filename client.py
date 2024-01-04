import socket
import pickle


def send_configuration(host, port, new_config):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    serialized_config = pickle.dumps(new_config)

    client_socket.sendall(serialized_config)

    acknowledgment = client_socket.recv(1024)
    print("Server response:", acknowledgment.decode())

    client_socket.close()


if __name__ == "__main__":
    server_host = "localhost"
    server_port = 6969

    new_configuration = {"username": "gosholosho"}  # sets the interval to 1 minute
    send_configuration(server_host, server_port, new_configuration)
