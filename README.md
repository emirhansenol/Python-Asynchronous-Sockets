# Python Asynchronous Sockets

Implementation of load balancing across DNS servers using Python language.

------------

This project explores a slightly more sophisticated form of balancing load that also takes into account the need to respond to requests as early as possible.

This project explores request duplication, i.e., sending the same request to two servers, and picking the response that arrives first.  At the cost of using more system resources, this allows the overall system to hide the delay caused by a slow server. In this project, I modelled a slow server in the extreme by implementing servers that do not send any response at all in some cases.

There are four programs in this project: 
- a client
- a load-balancing server (LS) that implements load balancing, and
- two DNS servers TS1 and TS2.

Load balancing across DNS servers is implemented as follows.  
- First, the client sends its DNS query to the load-balancing server LS.
- LS resolves the query on behalf of the client by querying two other DNS servers TS1 and TS2, and returning the response or an error to the client. 

Only TS1 and TS2 store the actual mappings from domain names to IP addresses. LS does not store any name to IP mappings.

The mappings stored by TS1 and TS2 do not overlap with each other. 

Only when a TS server contains a mapping for the queried domain name will it respond to LS; otherwise, that TS sends nothing back. Hence, at most one TS will respond to any query from LS. 

It is also possible that neither TS contains a mapping for the queried domain name. However, LS does not know in advance which TS, if any, will contain the IP address for a given domain name.  Hence, LS must query both TS1 and TS2.

There are three possibilities:
1. TS1 responds
2. TS2 responds or
3. neither TS1 nor TS2 responds within a fixed timeout. 

Note that it is never the case that both TS1 and TS2 respond.

In cases (1) and (2) above, LS must relay the response as is from the server to the client. In case (3), LS returns an error to the client.

Therefore, LS simply implements query resolution on behalf of the  client. That  is,  only LS interacts with the client. The TS servers do not communicate directly with the client.

## Intereaction of Servers and Message Passing
|<img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226136797-8ea82c78-50e2-4620-aab6-a46912b0a6ca.png">|   <img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226136827-182fbbe3-c7ff-4c0a-b877-0fa233f7a1ec.png">|

## Design of the servers

In lieu of the actual DNS protocol, this project uses a simple message format for name queries and response.

In my LS implementation, I have two separate sockets to connect to TS1 and TS2:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226136966-f90c8224-f136-4965-9e22-79c7b6f0efc8.png">

In my TS implementation, the connection from LS to TS is a blocking-connection:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226137421-cc0c9e07-4765-4366-a895-d1ae812233e1.png">

LS sends the query string to both TS1 and TS2:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226137687-3351fca3-a0f5-4b02-9a12-6012b72b987f.png">

Then, the LS waits for a response is waited from any of them as follows:

<img width="500" alt="image" src="https://user-images.githubusercontent.com/107651391/226137811-49ebae48-66de-411e-b3b9-a45dae280e92.png">

The select function is a way to monitor multiple sockets for incoming data, outgoing space availability, or exceptions. It allows to wait for one or more sockets to become ready for I/O, without blocking indefinitely.

The select function takes four arguments:
1. A list of sockets to be monitored for incoming data. In this case, [ts1_socket, ts2_socket] specifies that the LS should monitor both the ts1_socket and ts2_socket for incoming data.
2. A list of sockets to be monitored for space availability for outgoing data. In this case, the list is empty, [], as the LS is only receiving data from the TS servers and not sending any data to them.
3. A list of sockets to be monitored for exceptions. In this case, the list is also empty, [].
4. The timeout value in seconds. In this case, TS_RESPONSE_TIMEOUT, which is set to 5 seconds.

The select function returns a tuple (read_sockets, write_sockets, error_sockets), where read_sockets is a list of sockets that are ready to be read from, write_sockets is a list of sockets that are ready to be written to, and error_sockets is a list of sockets that have raised exceptions.

In this code, the LS is only interested in the read_sockets, as it is only receiving data from the TS servers. If no sockets are ready to be read within the specified timeout, ready[0] will be an empty list, and the response will be set to "TIMED OUT". If one or more sockets are ready to be read, the first socket in the list, i.e. ready[0][0], is selected and its response is received and sent back to the client.

This way LS acts as a load balancing server by distributing the requests between the TS servers and improving the efficiency and reliability of the domain name resolution process.
