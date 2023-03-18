import socket
import sys

INPUT_FILE_NAME = "PROJ2-HNS.txt"
OUTPUT_FILE_NAME = "RESOLVED.txt"


def client(ls_hostname, ls_port):
    with open(INPUT_FILE_NAME, "r") as input_file, open(OUTPUT_FILE_NAME, "w") as output_file:
        print("Input file name: {}".format(INPUT_FILE_NAME))
        print("Output file name: {}".format(OUTPUT_FILE_NAME))

        for line in input_file:
            query = line.strip()
            print("\nQuery read from file: {}".format(query))

            # Create a socket to connect to the LS 
            ls_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ls_socket.connect((ls_hostname, int(ls_port)))
            print("Connected to LS.")

            # Send the query to the LS 
            ls_socket.sendall(query.encode('utf-8'))
            print("Query sent to LS")

            # Receive the response from the LS 
            response = ls_socket.recv(200).strip().decode('utf-8')
            print("Response received from LS: {}".format(response))

            # Write response to resolved file.
            output_file.write(response.encode('utf-8') + "\n")
            print("Response written to file")

            # Clean up the socket
            ls_socket.close()


if __name__ == "__main__":
    client(sys.argv[1], sys.argv[2])
    print("\nDone.")
