def allow(client, key, limit, window):
    if client.set(key, 1, ex=window, nx=True):
        return True
    cnt = client.incr(key)
    return cnt <= limit
