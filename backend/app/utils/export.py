import csv
from io import BytesIO, StringIO
from urllib.parse import quote

import pandas as pd
from flask import make_response


def flatten_export_rows(rows):
    flattened = []
    extra_keys = set()

    for row in rows:
        extra = row.get('extra') or {}
        extra_keys.update(extra.keys())

    ordered_extra_keys = sorted(extra_keys)

    for row in rows:
        base = {
            'id': row.get('id'),
            'task_id': row.get('task_id'),
            'task_name': row.get('task_name'),
            'title': row.get('title'),
            'content': row.get('content'),
            'url': row.get('url'),
            'created_at': row.get('created_at'),
        }
        for key in ordered_extra_keys:
            base[f'extra_{key}'] = (row.get('extra') or {}).get(key, '')
        flattened.append(base)

    return flattened


def build_export_response(rows, export_format, filename_prefix='crawler_data'):
    export_rows = flatten_export_rows(rows)
    content_disposition = build_content_disposition(filename_prefix, 'csv' if export_format == 'csv' else 'xlsx')

    if export_format == 'csv':
        output = StringIO()
        fieldnames = export_rows[0].keys() if export_rows else ['id']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        if export_rows:
            writer.writerows(export_rows)
        response = make_response(output.getvalue().encode('utf-8-sig'))
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = content_disposition
        return response

    dataframe = pd.DataFrame(export_rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = content_disposition
    return response


def build_content_disposition(filename_prefix, extension):
    safe_prefix = str(filename_prefix or 'crawler_data').strip() or 'crawler_data'
    ascii_name = ''.join(
        char if char.isascii() and char not in {'"', '\\', '/', '\r', '\n', ';'} else '_'
        for char in safe_prefix
    ).strip('._ ')
    if not ascii_name:
        ascii_name = 'crawler_data'

    encoded_name = quote(f'{safe_prefix}.{extension}')
    return f"attachment; filename=\"{ascii_name}.{extension}\"; filename*=UTF-8''{encoded_name}"
