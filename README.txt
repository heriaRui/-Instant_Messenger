Instant messenger

This is a project has 2 parts, client.py and server.py,  based on python 3.13, with socket library and TCP protocol.

functionality description:

1.In this project , it has unicast and  broadcast message.
-All the user who connect to the server could send the broadcast , which just type
the message on the terminal  directly who could be seen by everyone , user could
also switch to unicast mode by type `/private [username] [message]` then only the specified user will receive the message.

2.exit functionality :
 -Type `exit`, the user actively disconnects and the server broadcasts a leave notification.	Then the server will keep running.

3.Shared File:
   - List files: Enter `/files` to view all files in the server shared folder.
   - Download files: Enter `/download [filename]` to download the specified files in the shared folder.
   - Upload files (support coming soon): the client can upload files to the server's shared folder.

4.Error / Exception Handling 
-Any errors that can occur on either client or server side should be handled appropriately.
- In case of a crash, attempt to close remaining connections and print an error message in the terminals of all previous connected devices.
- The server  not allow any client to transmit messages without having first set
a username.
- If the server is not available or port/hostname are incorrect , an error message detailing the issue will be printed.

How to use:

run server.py on python:
   ```bash'
  cd- 'the folder location'
python server.py 13000

Then open another terminal:
cd-the folder location
python client.py username 127.0.0.1 13000

Available commands:
    1.Send message: Enter text content directly.
    2.Private chat: Type /private [username] [message]. Example: /private Brian Hi Brian!
   3. List files: Enter" /files.
   4. Download a file: type /download [filename]. Example: /download 'filename'
   5. To exit: type exit.

Notices:

    -Make sure the server-side and client-side versions of Python are the same.
    -The path to the server's shared folder is Shared Files, which needs to be created in advance and put into the test files.
   - Files received by the client will be saved to a folder named after your username.
