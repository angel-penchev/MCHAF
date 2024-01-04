import logging
import socket
import pickle
import threading


def start_server_thread(address, port, app):
    server_thread = threading.Thread(target=start_server, args=(address, port, app))
    server_thread.start()
    return server_thread


def start_server(address, port, app):
    logging.info("[START] Configuration socket server.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((address, port))
    server_socket.listen(1)

    logging.info(f"Server listening on {address}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        logging.info(f"Accepted connection from {client_address}")

        handle_client(client_socket, app)


def reconfigure_app(app, new_config):
    if "username" in new_config:
        app.set_username(new_config["username"])
        logging.info("Username updated to %s.", app.username)

    if "password" in new_config:
        app.set_password(new_config["password"])
        logging.info("Password updated to %s.", app.password)

    if "moodle_domain" in new_config:
        app.set_moodle_domain(new_config["moodle_domain"])
        logging.info("Moodle domain updated to %s.", app.moodle_domain)

    if "course_id" in new_config:
        app.set_course_id(new_config["course_id"])
        logging.info("Course id updated to %d.", app.course_id)

    if "choice_title_regex" in new_config:
        app.set_choice_title_regex(new_config["choice_title_regex"])
        logging.info("Choice title regex updated to %s.", app.choice_title_regex)

    if "notification_level" in new_config:
        app.set_notification_level(new_config["notification_level"])
        logging.info("Notification level updated to %d.", app.notification_level)


def handle_client(client_socket, app):
    logging.info("[START] Handle client connection.")
    while True:
        data = client_socket.recv(1024)
        if not data:
            logging.info("Client sent EOF.")
            break

        new_config = pickle.loads(data)
        logging.info("Received new configuration: %s", new_config)

        reconfigure_app(app, new_config)

        logging.info("[START] Sending confirmation to client.")
        client_socket.sendall(b"Configuration updated successfully")
        logging.info("[END] Sending confirmation to client.")

    client_socket.close()
    logging.info("Closed client connection.")
    logging.info("[END] Handle client connection.")
