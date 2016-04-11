from collections import namedtuple
from couchforms.models import all_known_formlike_doc_types
from dimagi.utils.couch.undo import DELETED_SUFFIX

CASE = 'case'
FORM = 'form'
DOMAIN = 'domain'
META = 'meta'


DocumentType = namedtuple('DocumentType', ['raw_doc_type', 'primary_type', 'subtype', 'is_deletion'])


def get_doc_type_object_from_document(document):
    raw_doc_type = _get_document_type(document)
    if raw_doc_type:
        primary_type = _get_primary_type(raw_doc_type)
        return _make_document_type(raw_doc_type, primary_type, document)


def _get_primary_type(raw_doc_type):
    if raw_doc_type in ('CommCareCase', 'CommCareCase-Deleted'):
        return CASE
    elif raw_doc_type in all_known_formlike_doc_types():
        return FORM
    elif raw_doc_type in ('Domain', 'Domain-Deleted', 'Domain-DUPLICATE'):
        return DOMAIN
    else:
        # at some point we may want to make this more granular
        return META


def _make_document_type(raw_doc_type, primary_type, document):
    if primary_type == CASE:
        return _case_doc_type_constructor(raw_doc_type, document)
    elif primary_type == FORM:
        return _form_doc_type_constructor(raw_doc_type, document)
    elif primary_type == DOMAIN:
        return _domain_doc_type_constructor(raw_doc_type)
    else:
        return DocumentType(
            raw_doc_type, primary_type, None, _is_deletion(raw_doc_type)
        )


def _get_document_type(document_or_none):
    return document_or_none.get('doc_type', None) if document_or_none else None


def _is_deletion(raw_doc_type):
    # can be overridden
    return raw_doc_type.endswith(DELETED_SUFFIX)


def _case_doc_type_constructor(raw_doc_type, document):
    return DocumentType(
        raw_doc_type, CASE, document.get('type', None), _is_deletion(raw_doc_type)
    )


def _form_doc_type_constructor(raw_doc_type, document):
    return DocumentType(
        raw_doc_type, FORM, document.get('xmlns', None), _is_deletion(raw_doc_type)
    )


def _domain_doc_type_constructor(raw_doc_type):
    is_deletion = raw_doc_type == 'Domain-DUPLICATE' or _is_deletion(raw_doc_type)
    return DocumentType(
        raw_doc_type, DOMAIN, None, is_deletion
    )
