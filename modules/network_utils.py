import socket

def is_online(host="8.8.8.8", port=53, timeout=3):
    """
    Checks internet connectivity by trying to connect to a public DNS server.
    Returns True if online, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
