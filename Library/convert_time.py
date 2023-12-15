from datetime import datetime


def convert_to_datetime(datetime_str):
    try:
        # Định dạng thời gian của chuỗi đầu vào
        input_format = "%d-%m-%Y %H:%M"

        # Chuyển đổi chuỗi thành đối tượng datetime
        datetime_obj = datetime.strptime(datetime_str, input_format)

        return datetime_obj
    except ValueError as e:
        # Xử lý lỗi nếu chuỗi đầu vào không đúng định dạng
        print(f"Error converting datetime: {e}")
        return None
