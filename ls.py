import select
import socket
import sys

TS_RESPONSE_TIMEOUT = 5


def load_balancer(parameters):
    # Parse the command line arguments
    ls_listen_port = int(parameters[0])
    ts1_hostname = parameters[1]
    ts1_listen_port = int(parameters[2])
    ts2_hostname = parameters[3]
    ts2_listen_port = int(parameters[4])

    # Create the LS socket to listen for incoming client requests
    ls_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls_socket.bind(('', ls_listen_port))
    ls_socket.listen(5)
    print("LS is listening on port {}".format(ls_listen_port))

    # Connect to TS1
    ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts1_socket.connect((ts1_hostname, ts1_listen_port))

    # Connect to TS2 
    ts2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts2_socket.connect((ts2_hostname, ts2_listen_port))

    while True:
        # Wait for incoming client requests
        client_socket, client_address = ls_socket.accept()
        client_socket.setblocking(True)
        print("\nAccepted connection from {}".format(client_address))

        # Receive the domain name query from the client
        while True:
            try:
                query = client_socket.recv(200).decode('utf-8')
                if not query:
                    break
                print("Query received from the client: {}".format(query))
                break
            except socket.error as e:
                print("LS raised exception {}".format(e))
                raise e

        # Send the domain name query to both TS s
        ts1_socket.sendall(query.encode('utf-8'))
        ts2_socket.sendall(query.encode('utf-8'))
        print("Query sent to both TS1 and TS2")

        # Wait for a response from either TS  using select()
        print("Waiting for a response within {} seconds".format(TS_RESPONSE_TIMEOUT))
        ready = select.select([ts1_socket, ts2_socket], [], [], TS_RESPONSE_TIMEOUT)

        if not ready[0]:
            # No response from either TS  within the timeout
            response = "{} - TIMED OUT".format(query)
            print("Response timed out")
        else:
            # Receive the response from the first ready TS 
            ts_socket = ready[0][0]
            response = ts_socket.recv(200).decode('utf-8')
            print("Response received: {}".format(response))

        # Send the response back to the client
        client_socket.sendall(response.encode('utf-8'))
        print("Response sent to client")

        # Clean up the client socket
        client_socket.close()
        print("Client socket closed")

    # Clean up the sockets
    ts1_socket.close()
    ts2_socket.close()
    ls_socket.close()


if __name__ == "__main__":
    load_balancer(sys.argv[1:])
    print("\nDone.")
