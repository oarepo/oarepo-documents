from invenio_pidstore.providers.recordid import RecordIdProvider


def document_minter(object_uuid, data):

    provider = RecordIdProvider.create(
        object_type='rec',
        object_uuid=object_uuid,
    )
    data['pid'] = provider.pid.pid_value
    print(provider.pid)
    return provider.pid, data