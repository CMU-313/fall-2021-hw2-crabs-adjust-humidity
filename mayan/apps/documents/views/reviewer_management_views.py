import logging

from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.common.classes import ModelQueryFields
from mayan.apps.views.generics import (
    MultipleObjectFormActionView, SingleObjectDetailView,
    SingleObjectEditView, SingleObjectListView
)

from ..events import event_document_viewed
from ..forms.document_forms import DocumentForm, DocumentPropertiesForm
from ..forms.document_type_forms import DocumentTypeFilteredSelectForm
from ..icons import icon_document_list
from ..models.document_models import Document
from ..permissions import (
    permission_document_properties_edit, permission_document_view
)

from .document_version_views import DocumentVersionPreviewView

__all__ = (
    'ReviewerManagementView'
)
logger = logging.getLogger(name=__name__)


class ReviewerManagementView(SingleObjectListView):
    object_permission = permission_document_view

    def get_context_data(self, **kwargs):
        try:
            return super().get_context_data(**kwargs)
        except Exception as exception:
            messages.error(
                message=_(
                    'Error retrieving document list: %(exception)s.'
                ) % {
                    'exception': exception
                }, request=self.request
            )
            self.object_list = Document.valid.none()
            return super().get_context_data(**kwargs)

    def get_document_queryset(self):
        return Document.valid.all()

    def get_extra_context(self):
        return {
            'hide_links': True,
            'hide_object': True,
            'list_as_items': True,
            'no_results_icon': icon_document_list,
            'no_results_text': _(
                'This could mean that no documents have been uploaded or '
                'that your user account has not been granted the view '
                'permission for any document or document type.'
            ),
            'no_results_title': _('No documents available'),
            'title': _('Reviewer Management'),
        }

    def get_source_queryset(self):
        queryset = ModelQueryFields.get(model=Document).get_queryset()
        return self.get_document_queryset().filter(pk__in=queryset)

