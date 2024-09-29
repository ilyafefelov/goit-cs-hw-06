import socket
import threading
from datetime import datetime
from pymongo import MongoClient
import ast
import os

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000


def handle_client_connection(client_socket):
    with client_socket:
        data = client_socket.recv(1024)
        if data:
            print(f"Received data: {data}")
            try:
                process_data(data)
                client_socket.sendall(b"OK")
            except Exception as e:
                print(f"Error processing data: {e}")
                client_socket.sendall(b"ERROR")


def process_data(data):
    # Convert byte string to dictionary
    data_str = data.decode("utf-8")
    data_dict = ast.literal_eval(data_str)
    data_dict["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    # Store in MongoDB
    save_to_mongodb(data_dict)


def save_to_mongodb(data):
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["messages_db"]
    collection = db["messages"]
    collection.insert_one(data)
    client.close()
    print("Data saved to MongoDB:", data)


def run_socket_server():
    protocol = os.environ.get("PROTOCOL", "TCP")

    if protocol == "TCP":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Socket server listening on port {PORT}...")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client_connection, args=(conn,)).start()
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            print(f"Socket server listening on port {PORT}...")
            while True:
                data, addr = s.recvfrom(1024)
                if data:
                    print(f"Received data from {addr}: {data}")
                    process_data(data)


if __name__ == "__main__":
    run_socket_server()
