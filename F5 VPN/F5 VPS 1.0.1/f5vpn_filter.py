"""Optional client-side APM Virtual Server selection for test and discovery."""


def session_url(host, configured):
    url = host + '/mgmt/tm/apm/access-info'
    if configured and configured.strip():
        url += '?options=all-properties'
    return url


def select_sessions(data, configured):
    """Return (selected payload, summary, error); never broaden an enabled filter."""
    configured = (configured or '').strip()
    if not isinstance(data, dict):
        return {}, '', 'Unsupported access-info response: expected a JSON object.'
    if not configured:
        count = len(data.get('entries', {}))
        return data, 'Total APM sessions: {}'.format(count), ''

    allowed = [name.strip() for name in configured.split(',')]
    if any(not name.startswith('/') or len(name.strip('/').split('/')) < 2
           or any(char.isspace() for char in name) for name in allowed):
        return {}, '', 'Virtual Servers must be comma-separated full paths, for example /Common/Lab_VPN.'
    entries = data.get('entries')
    if not isinstance(entries, dict) or data.get('nextLink'):
        return {}, '', 'Virtual Server filtering requires a complete structured access-info entries response; this response is unsupported or unavailable.'

    selected = {}
    unknown = 0
    for session, record in entries.items():
        nested = record.get('nestedStats') if isinstance(record, dict) else None
        fields = nested.get('entries') if isinstance(nested, dict) else None
        if not isinstance(fields, dict):
            fields = {}
        # REST spelling and TMSH spelling are accepted explicitly, without guessing
        # that a hostname or another session variable represents a Virtual Server.
        values = []
        for key in ('virtualServer', 'virtual-server'):
            value = fields.get(key)
            if isinstance(value, dict):
                value = value.get('description')
            if isinstance(value, str) and value.strip():
                values.append(value.strip())
        if len(set(values)) != 1 or not values[0].startswith('/'):
            unknown += 1
        elif values[0] in allowed:
            selected[session] = record

    summary = 'Total APM sessions: {}; matching Virtual Server sessions: {}'.format(len(entries), len(selected))
    if unknown:
        return {}, summary, ('Cannot apply Virtual Server filter: {} of {} sessions lack an unambiguous full Virtual Server path. '
                             'No sessions were selected. The all-properties response may be unsupported on this BIG-IP version.').format(unknown, len(entries))
    result = dict(data)
    result['entries'] = selected
    return result, summary, ''
