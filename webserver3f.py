# -*- coding: UTF-8 -*-
'''
* 如果你 fork 了一个子进程，但是却没有 wait 它，它就会变成一个僵尸进程。
* 使用 SIGCHLD 事件处理器来异步 wait 终止的子进程以便收集它的终止状态。
* 当使用事件处理器的时候，你需要考虑到系统可能会中断，这样的话你就需求为这个场景做些准备。
'''
import errno
import os
import signal
import socket

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def grim_reaper(signum, frame):
    pid, status = os.wait()
    print(
        'Child {pid} terminated with status {status}'
        '\n'.format(pid=pid, status=status)
    )


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK
Hello, World!
"""
    client_connection.sendall(http_response)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    signal.signal(signal.SIGCHLD, grim_reaper)

    while True:
        try:
            '''
            如果不用try块包裹，并用continue重新触发的话
            当子进程退出并导致SIGCHLD事件时，父进程在accept调用中被阻塞，SIGCHLD事件又激活了信号处理程序，并且当信号处理程序完成accept系统调用时被中断
            '''
            client_connection, client_address = listen_socket.accept()  # 阻塞的
        except IOError as e:
            code, msg = e.args
            # restart 'accept' if it was interrupted
            if code == errno.EINTR:
                continue
            else:
                raise

        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)
        else:  # parent
            client_connection.close()


if __name__ == '__main__':
    serve_forever()
