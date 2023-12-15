import redis


def Delete_redis_keys_with_prefix(prefix):
    # Kết nối đến Redis server
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Sử dụng SCAN để lấy danh sách tất cả các key có tiền tố
    keys = []
    cursor = 0
    while True:
        cursor, partial_keys = r.scan(cursor, f"{prefix}*")
        keys.extend(partial_keys)
        if cursor == 0:
            break

    # Xóa các key tìm thấy
    for key in keys:
        r.delete(key)


# Sử dụng hàm để xóa các key có tiền tố "files_karina1104"
# Delete_redis_keys_with_prefix('files_karina1104')
