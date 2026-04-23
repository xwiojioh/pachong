import csv
from io import BytesIO, StringIO

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

    if export_format == 'csv':
        output = StringIO()
        fieldnames = export_rows[0].keys() if export_rows else ['id']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        if export_rows:
            writer.writerows(export_rows)
        response = make_response(output.getvalue().encode('utf-8-sig'))
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}.csv'
        return response

    dataframe = pd.DataFrame(export_rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}.xlsx'
    return response
