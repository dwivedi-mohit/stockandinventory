from nicegui import ui
from typing import Callable, Optional


def data_table(
    columns: list[dict],
    rows: list[dict],
    searchable: bool = True,
    addable: bool = True,
    on_add: Optional[Callable] = None,
    row_key: str = 'id',
    title: str = '',
):
    with ui.card().classes('w-full p-4'):
        if title:
            ui.label(title).classes('text-xl font-semibold mb-4')

        with ui.row().classes('w-full items-center justify-between mb-4'):
            if searchable:
                search = ui.input('Search...').props('outlined dense').classes('w-72')
            if addable and on_add:
                ui.button('Add New', on_click=on_add, color='#1A73E8').props('dense')

        table = ui.table(
            columns=columns,
            rows=rows,
            row_key=row_key,
            pagination={'rowsPerPage': 25},
        ).classes('w-full')

        if searchable:
            def filter_table(text: str):
                if not text:
                    table.set_rows(rows)
                    return
                filtered = [r for r in rows if any(
                    str(r.get(c['field'], '')).lower().find(text.lower()) >= 0
                    for c in columns if c.get('field')
                )]
                table.set_rows(filtered)
            search.on_value_change(filter_table)

    return table
