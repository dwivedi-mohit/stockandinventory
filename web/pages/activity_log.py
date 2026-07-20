from nicegui import ui
from web.auth import WebAuth, get_db
from web.components.layout import page_container
from inventory.services.activity_service import ActivityService


def activity_log_page():
    if not WebAuth.is_authenticated() or not WebAuth.has_permission('admin'):
        ui.navigate.to('/dashboard')
        return

    page_container()

    try:
        db = get_db()
        service = ActivityService(db)
        action_types = service.get_action_types()
    except Exception as e:
        ui.notify(f'Failed to load: {e}', type='negative')
        return

    with ui.column().classes('w-full p-6'):
        ui.label('Activity Log').classes('text-2xl font-bold text-gray-800 mb-4')

        with ui.row().classes('w-full gap-4 items-end'):
            days = ui.input('Days', value='30').props('outlined dense').classes('w-24')
            action_select = ui.select(['All'] + action_types, label='Action', value='All').classes('w-48').props('outlined')
            refresh_btn = ui.button('Refresh', color='#1A73E8')

        table_container = ui.column().classes('w-full mt-4')

        def load_log():
            table_container.clear()
            try:
                rows = service.get_all(
                    limit=int(days.value or 30) * 100,
                    action=action_select.value if action_select.value and action_select.value != 'All' else None,
                    days=int(days.value or 30),
                )
                columns = [
                    {'name': 'created_at', 'label': 'Timestamp', 'field': 'created_at'},
                    {'name': 'username', 'label': 'User', 'field': 'username'},
                    {'name': 'action', 'label': 'Action', 'field': 'action'},
                    {'name': 'entity_type', 'label': 'Entity', 'field': 'entity_type'},
                    {'name': 'entity_id', 'label': 'ID', 'field': 'entity_id'},
                    {'name': 'details', 'label': 'Details', 'field': 'details'},
                ]
                with table_container:
                    ui.table(columns=columns, rows=rows, pagination={'rowsPerPage': 25}).classes('w-full')
            except Exception as e:
                ui.notify(f'Failed to load log: {e}', type='negative')

        refresh_btn.on_click(load_log)
        load_log()
