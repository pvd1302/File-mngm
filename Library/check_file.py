import zipfile

from PIL import Image
from bs4 import BeautifulSoup
from flask import Flask, jsonify

def allowed_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'docx', 'xlsx'}

UPLOAD_FOLDER = r'D:\python flask API\file management\data'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


def allowed_file_size(file_size):
    return file_size <= app.config['MAX_CONTENT_LENGTH']


def identify_format_by_part_name(part_name):
    if 'xl' in part_name:
        return 'xlsx'
    elif 'word' in part_name:
        return 'docx'
    else:
        return 'Unknown format'


def identify_format_by_binary(header_bytes):
    if header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'

    elif header_bytes.startswith(b'\xFF\xD8'):
        return 'jpg'
    else:
        return 'Unknown'


def analyze_uploaded_file_application(file):
    # Đọc nội dung của tệp [Content_Types].xml từ file được upload
    with zipfile.ZipFile(file, 'r') as zip_file:
        content_types_bytes = zip_file.read('[Content_Types].xml')
        content_types_xml = content_types_bytes.decode('utf-8')

    # Tạo đối tượng BeautifulSoup
    soup = BeautifulSoup(content_types_xml, 'xml')

    # Tìm tất cả các thẻ <Default> và kiểm tra PartName
    for default_tag in soup.find_all('Override'):
        part_name = default_tag.get('PartName')
        if any(identifier in part_name for identifier in ('xl', 'word')):
            file_format = identify_format_by_part_name(part_name)
            return file_format

    return "No matching part names found."


def analyze_uploaded_media(file_data, num_bytes=16):
    try:
        # Đọc num_bytes đầu tiên từ dữ liệu file
        header_bytes = file_data.read(num_bytes)
        # print(header_bytes)
        file_format = identify_format_by_binary(header_bytes)

        return file_format
    except Exception as e:
        return f'An error occurred: {e}'


def infor_file(file):
    filename = file.filename
    if not allowed_file_extension(filename):
        return 'Invalid file extension'
    real_format = ''
    file_extension = filename.split('.')[-1].lower()
    if file_extension.lower() in ['png', 'jpg']:
        real_format = analyze_uploaded_media(file)
        if real_format.lower() != file_extension.lower():
            return jsonify({"message": "File's format not satisfied !"}), 404

    elif file_extension.lower() in ['docx', 'xlsx']:
        real_format = analyze_uploaded_file_application(file)
        if real_format.lower() != file_extension.lower():
            return jsonify({"message": "File's format not satisfied !"}), 404
    if real_format.lower() in ['png', 'jpg']:
        img = Image.open(file)
        # Lấy độ phân giải
        width, height = img.size
        resolution = f"{width} x {height} px"
    else:
        resolution = None
    return resolution, real_format
