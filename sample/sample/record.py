from invenio_records.api import Record
from oarepo_actions.decorators import action
from oarepo_validate import MarshmallowValidatedRecordMixin, SchemaKeepingRecordMixin

from oarepo_documents.api import DocumentRecordMixin

from .constants import SAMPLE_ALLOWED_SCHEMAS, SAMPLE_PREFERRED_SCHEMA
from .marshmallow import SampleSchemaV1


class SampleRecord(SchemaKeepingRecordMixin,
                   MarshmallowValidatedRecordMixin,
                   DocumentRecordMixin,
                   Record):
    ALLOWED_SCHEMAS = SAMPLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = SAMPLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = SampleSchemaV1

    # @classmethod
    # @action(url_path='test', detail=False)
    # def test(cls,  **kwargs):
    #     return {"id": "kch"}
    def validate(self, **kwargs):
        return super().validate(**kwargs)
