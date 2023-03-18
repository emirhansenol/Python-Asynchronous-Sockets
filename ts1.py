import socket
import sys

INPUT_FILE_NAME = "PROJ2-DNSTS1.txt"


def read_dns_table(file_name):
    new_dns_table = {}
    with open(file_name, 'r') as f:
        for line in f:
            domain, ip, record_type = line.strip().split()
            new_dns_table[domain.lower()] = (ip, record_type)
    return new_dns_table


def lookup(lookup_dns_table, domain_name):
    domain_name = domain_name.lower()
    if domain_name in lookup_dns_table:
        ip, record_type = lookup_dns_table[domain_name]
        return "{} {} A IN".format(domain_name, ip)
    else:
        return None


if __name__ == '__main__':
    dns_table = read_dns_table(INPUT_FILE_NAME)
    listen_port = int(sys.argv[1])

    ts_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts_socket.bind(('', listen_port))
    ts_socket.listen(1)
    print("TS1 is listening on port {}".format(listen_port))

    while True:
        ls_socket, ls_address = ts_socket.accept()
        ls_socket.setblocking(True)
        print("\nAccepted connection from LS {}".format(ls_address))

        while True:
            # Receive the domain name query from the LS 
            query = ls_socket.recv(200).strip().decode('utf-8')
            if not query:
                break
            print("\tQuery received from LS: {}".format(query))

            # Lookup in query in the DNS table
            response = lookup(dns_table, query)
            if response:
                ls_socket.sendall(response.encode('utf-8'))
                print("\t\tResponse sent to LS: {}".format(response.encode('utf-8')))
            else:
                print("\t\tNot found.")

        # Clean up the socket
        ls_socket.close()
        print("Connection closed.")
        break

    print("\nDone.")
