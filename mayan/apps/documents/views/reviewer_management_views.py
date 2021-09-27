import logging

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from mayan.apps.common.classes import ModelQueryFields
from mayan.apps.views.generics import SingleObjectDropdownListView
from mayan.apps.user_management.api_views import APIUserListView
from ..icons import icon_document_list
from ..models.document_models import Document
from ..permissions import permission_document_view

__all__ = ('ReviewerManagementView')

logger = logging.getLogger(name=__name__)


class ReviewerManagementView(SingleObjectDropdownListView):
    object_permission = permission_document_view

    def get_context_data(self, **kwargs):
        context = None
        try:
            context =  super().get_context_data(**kwargs)
        except Exception as exception:
            messages.error(
                message=_(
                    'Error retrieving document list: %(exception)s.'
                ) % {
                    'exception': exception
                }, request=self.request
            )
            self.object_list = Document.valid.none()
            context = super().get_context_data(**kwargs)
            
        context['users'] = list(get_user_model().objects.filter(is_superuser=False).order_by('username'))
        #get all user that is not admin, and order them by username
        return context

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