# -*- coding: UTF-8 -*-
'''
* 在 Unix 下写并发服务器的最简单的方法是调用系统内的 fork() 方法
* 当一个进程 fork 了一个新的进程的时候，它就变成了那个新 fork 的子进程的父进程。
* 在调用 fork 后父子进程共享相同的文件描述符。
* 内核使用描述符引用计数来决定是否需要关闭文件/socket
* 服务器的父进程现在只有一个角色，那就是接收一个新的客户端连接， fork 一个新的子进程用来处理这个请求，然后循环以便接收另一个客户端的连接。

* 如果你没有关闭描述符副本，客户端将不会退出，因为客户端连接还没有被关闭。
* 如果你没有关闭描述符副本，你那长时间运行的服务器最终将耗尽所有可用的文件描述符（max open files）。
* 当你 fork 一个子进程然后退出，同时父进程没有等待( wait )子进程完成退出操作，父进程就收集不到子进程的退出状态，子进程最终就会变成一个僵尸进程。
* 如果不管这些僵尸进程的话，你的服务器将最终耗尽所有可用的进程（max user processes）
* 你无法 kill 一个僵尸进程，你需要等( wait )它完成退出操作。
'''
import os
import socket
import time

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(
        'Child PID: {pid}. Parent PID {ppid}'.format(
            pid=os.getpid(),
            ppid=os.getppid(),
        )
    )
    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    time.sleep(60)


def server_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))
    print('Parent PID (PPID): {pid}\n'.format(pid=os.getpid()))

    while True:
        client_connection, client_address = listen_socket.accept()
        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)  # child exits here
        else: # parent
            client_connection.close()  # close parent copy and loop over

if __name__ == '__main__':
    server_forever()
