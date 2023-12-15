from marshmallow import Schema, fields


class FolderSchema(Schema):
    id_folder = fields.Str()
    name_folder = fields.Str()

    created_at = fields.Str()
    updated_at = fields.Str()
    created_by = fields.Str()
    updated_by = fields.Str()


class FileSchema(Schema):
    id_file = fields.Str()
    file_name = fields.Str()
    file_name_save = fields.Str()
    id_folder = fields.Str()
    format = fields.Str()
    resolution = fields.Str()
    life_time = fields.Str()

    created_at = fields.Str()
    updated_at = fields.Str()
    created_by = fields.Str()
    updated_by = fields.Str()

