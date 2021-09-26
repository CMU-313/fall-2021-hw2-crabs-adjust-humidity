import logging

from django.shortcuts import reverse
from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.classes import ModelQueryFields
from mayan.apps.documents.models import Document
from mayan.apps.documents.views.document_views import DocumentListView
from mayan.apps.views.generics import (
    MultipleObjectFormActionView, MultipleObjectConfirmActionView,
    SingleObjectCreateView, SingleObjectEditView, SingleObjectListView
)
from mayan.apps.views.mixins import ExternalObjectViewMixin

from .forms import TagMultipleSelectionForm, ReviewerMultipleSelectionForm
from .icons import icon_menu_tags, icon_document_tag_remove_submit
from .links import link_document_tag_multiple_attach, link_tag_create, link_document_reviewer_multiple_attach, link_reviewer_create
from .models import DocumentTag, Tag
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

logger = logging.getLogger(name=__name__)


class TagAttachActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    object_permission = permission_tag_attach
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid
    success_message_single = _(
        'Tags attached to document "%(object)s" successfully.'
    )
    success_message_singular = _(
        'Tags attached to %(count)d document successfully.'
    )
    success_message_plural = _(
        'Tags attached to %(count)d documents successfully.'
    )
    title_single = _('Attach tags to document: %(object)s')
    title_singular = _('Attach tags to %(count)d document.')
    title_plural = _('Attach tags to %(count)d documents.')

    def get_extra_context(self):
        context = {
            'submit_label': _('Attach'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def get_form_extra_kwargs(self):
        kwargs = {
            'help_text': _('Tags to be attached.'),
            'permission': permission_tag_attach,
            'queryset': Tag.objects.all(),
            'user': self.request.user
        }

        if self.object_list.count() == 1:
            kwargs.update(
                {
                    'queryset': Tag.objects.exclude(
                        pk__in=self.object_list.first().tags.all()
                    )
                }
            )

        return kwargs

    def get_post_action_redirect(self):
        if self.object_list.count() == 1:
            return reverse(
                viewname='tags:document_tag_list', kwargs={
                    'document_id': self.object_list.first().pk
                }
            )
        else:
            return super().get_post_action_redirect()

    def object_action(self, form, instance):
        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=(permission_tag_attach,),
                user=self.request.user
            )

            tag._event_actor = self.request.user
            tag.attach_to(document=instance)


class TagCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create tag')}
    fields = ('label', 'color')
    model = Tag
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')
    view_permission = permission_tag_create

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class TagDeleteActionView(MultipleObjectConfirmActionView):
    error_message = _('Error deleting tag "%(instance)s"; %(exception)s')
    model = Tag
    object_permission = permission_tag_delete
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')
    success_message_single = _('Tag "%(object)s" deleted successfully.')
    success_message_singular = _('%(count)d tag deleted successfully.')
    success_message_plural = _('%(count)d tags deleted successfully.')
    title_single = _('Delete tag: %(object)s.')
    title_singular = _('Delete the %(count)d selected tag.')
    title_plural = _('Delete the %(count)d selected tags.')

    def get_extra_context(self):
        context = {
            'delete_view': True,
            'message': _('Will be removed from all documents.'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def object_action(self, instance, form=None):
        instance.delete()


class TagEditView(SingleObjectEditView):
    fields = ('label', 'color')
    model = Tag
    object_permission = permission_tag_edit
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit tag: %s') % self.object,
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class TagListView(SingleObjectListView):
    object_permission = permission_tag_view
    tag_model = Tag

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_menu_tags,
            'no_results_main_link': link_tag_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Tags are color coded properties that can be attached or '
                'removed from documents.'
            ),
            'no_results_title': _('No tags available'),
            'title': _('Tags'),
        }

    def get_source_queryset(self):
        queryset = ModelQueryFields.get(model=self.tag_model).get_queryset()
        return queryset.filter(pk__in=self.get_tag_queryset())

    def get_tag_queryset(self):
        return Tag.objects.all()


class TagDocumentListView(ExternalObjectViewMixin, DocumentListView):
    external_object_class = Tag
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'tag_id'

    def get_document_queryset(self):
        return Document.valid.filter(
            pk__in=self.get_tag().get_documents(
                permission=permission_tag_view, user=self.request.user
            ).values('pk')
        )

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'object': self.get_tag(),
                'title': _('Documents with the tag: %s') % self.get_tag(),
            }
        )
        return context

    def get_tag(self):
        return self.external_object


class DocumentTagListView(ExternalObjectViewMixin, TagListView):
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid
    tag_model = DocumentTag

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_main_link': link_document_tag_multiple_attach.resolve(
                    context=RequestContext(
                        self.request, {'object': self.external_object}
                    )
                ),
                'no_results_title': _('Document has no tags attached'),
                'object': self.external_object,
                'title': _(
                    'Tags for document: %s'
                ) % self.external_object,
            }
        )
        return context

    def get_tag_queryset(self):
        return self.external_object.get_tags(
            permission=permission_tag_view, user=self.request.user
        )


class TagRemoveActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    object_permission = permission_tag_remove
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid
    success_message_single = _(
        'Tags removed from document "%(object)s" successfully.'
    )
    success_message_singular = _(
        'Tags removed from %(count)d document successfully.'
    )
    success_message_plural = _(
        'Tags removed from %(count)d documents successfully.'
    )
    title_single = _('Remove tags from document: %(object)s')
    title_singular = _('Remove tags from %(count)d document.')
    title_plural = _('Remove tags from %(count)d documents.')

    def get_extra_context(self):
        context = {
            'submit_icon': icon_document_tag_remove_submit,
            'submit_label': _('Remove'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def get_form_extra_kwargs(self):
        kwargs = {
            'help_text': _('Tags to be removed.'),
            'permission': permission_tag_remove,
            'queryset': Tag.objects.all(),
            'user': self.request.user
        }

        if self.object_list.count() == 1:
            kwargs.update(
                {
                    'queryset': self.object_list.first().tags.all()
                }
            )

        return kwargs

    def get_post_action_redirect(self):
        if self.object_list.count() == 1:
            return reverse(
                viewname='tags:document_tag_list', kwargs={
                    'document_id': self.object_list.first().pk
                }
            )
        else:
            return super().get_post_action_redirect()

    def object_action(self, form, instance):
        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=(permission_tag_remove,),
                user=self.request.user
            )

            tag._event_actor = self.request.user
            tag.remove_from(document=instance)

class ReviewerAttachActionView(MultipleObjectFormActionView):
    form_class = ReviewerMultipleSelectionForm
    object_permission = permission_tag_attach
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid
    success_message_single = _(
        'Reviewers assigned to document "%(object)s" successfully.'
    )
    success_message_singular = _(
        'Reviewers assigned to %(count)d document successfully.'
    )
    success_message_plural = _(
        'Reviewers assigned to %(count)d documents successfully.'
    )
    title_single = _('Assign reviewers to document: %(object)s')
    title_singular = _('Assign reviewers to %(count)d document.')
    title_plural = _('Assign reviewers to %(count)d documents.')

    def get_extra_context(self):
        context = {
            'submit_label': _('Assign'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def get_form_extra_kwargs(self):
        kwargs = {
            'help_text': _('Reviewers to be assigned.'),
            'permission': permission_tag_attach,
            'queryset': Tag.objects.all(),
            'user': self.request.user
        }

        if self.object_list.count() == 1:
            kwargs.update(
                {
                    'queryset': Tag.objects.exclude(
                        pk__in=self.object_list.first().tags.all()
                    )
                }
            )

        return kwargs

    def get_post_action_redirect(self):
        if self.object_list.count() == 1:
            return reverse(
                viewname='tags:document_reviewer_list', kwargs={
                    'document_id': self.object_list.first().pk
                }
            )
        else:
            return super().get_post_action_redirect()

    def object_action(self, form, instance):
        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=(permission_tag_attach,),
                user=self.request.user
            )

            tag._event_actor = self.request.user
            tag.attach_to(document=instance)


class ReviewerCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create reviewer')}
    fields = ('label', 'color')
    model = Tag
    post_action_redirect = reverse_lazy(viewname='tags:reviewer_list')
    view_permission = permission_tag_create

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class ReviewerDeleteActionView(MultipleObjectConfirmActionView):
    error_message = _('Error deleting reviewer "%(instance)s"; %(exception)s')
    model = Tag
    object_permission = permission_tag_delete
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:reviewer_list')
    success_message_single = _('Reviewer "%(object)s" deleted successfully.')
    success_message_singular = _('%(count)d reviewer deleted successfully.')
    success_message_plural = _('%(count)d reviewers deleted successfully.')
    title_single = _('Delete reviewer: %(object)s.')
    title_singular = _('Delete the %(count)d selected reviewer.')
    title_plural = _('Delete the %(count)d selected reviewers.')

    def get_extra_context(self):
        context = {
            'delete_view': True,
            'message': _('Will be removed from all documents.'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def object_action(self, instance, form=None):
        instance.delete()


class ReviewerEditView(SingleObjectEditView):
    fields = ('label', 'color')
    model = Tag
    object_permission = permission_tag_edit
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:reviewer_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit reviewer: %s') % self.object,
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class ReviewerListView(SingleObjectListView):
    object_permission = permission_tag_view
    tag_model = Tag

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_menu_tags,
            'no_results_main_link': link_reviewer_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Reviewers can be assigned or removed from documents.'
            ),
            'no_results_title': _('No reviewers available'),
            'title': _('Reviewers'),
        }

    def get_source_queryset(self):
        queryset = ModelQueryFields.get(model=self.tag_model).get_queryset()
        return queryset.filter(pk__in=self.get_tag_queryset())

    def get_tag_queryset(self):
        return Tag.objects.all()


class ReviewerDocumentListView(ExternalObjectViewMixin, DocumentListView):
    external_object_class = Tag
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'tag_id'

    def get_document_queryset(self):
        return Document.valid.filter(
            pk__in=self.get_tag().get_documents(
                permission=permission_tag_view, user=self.request.user
            ).values('pk')
        )

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'object': self.get_tag(),
                'title': _('Documents with the reviewer: %s') % self.get_tag(),
            }
        )
        return context

    def get_tag(self):
        return self.external_object


class DocumentReviewerListView(ExternalObjectViewMixin, ReviewerListView):
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid
    tag_model = DocumentTag

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_main_link': link_document_reviewer_multiple_attach.resolve(
                    context=RequestContext(
                        self.request, {'object': self.external_object}
                    )
                ),
                'no_results_title': _('Document has no reviewers assigned'),
                'object': self.external_object,
                'title': _(
                    'Reviewers for document: %s'
                ) % self.external_object,
            }
        )
        return context

    def get_tag_queryset(self):
        return self.external_object.get_tags(
            permission=permission_tag_view, user=self.request.user
        )


class ReviewerRemoveActionView(MultipleObjectFormActionView):
    form_class = ReviewerMultipleSelectionForm
    object_permission = permission_tag_remove
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid
    success_message_single = _(
        'Reviewers removed from document "%(object)s" successfully.'
    )
    success_message_singular = _(
        'Reviewers removed from %(count)d document successfully.'
    )
    success_message_plural = _(
        'Reviewers removed from %(count)d documents successfully.'
    )
    title_single = _('Remove reviewers from document: %(object)s')
    title_singular = _('Remove reviewers from %(count)d document.')
    title_plural = _('Remove reviewers from %(count)d documents.')

    def get_extra_context(self):
        context = {
            'submit_icon': icon_document_tag_remove_submit,
            'submit_label': _('Remove'),
        }

        if self.object_list.count() == 1:
            context.update(
                {
                    'object': self.object_list.first(),
                }
            )

        return context

    def get_form_extra_kwargs(self):
        kwargs = {
            'help_text': _('Reviewers to be removed.'),
            'permission': permission_tag_remove,
            'queryset': Tag.objects.all(),
            'user': self.request.user
        }

        if self.object_list.count() == 1:
            kwargs.update(
                {
                    'queryset': self.object_list.first().tags.all()
                }
            )

        return kwargs

    def get_post_action_redirect(self):
        if self.object_list.count() == 1:
            return reverse(
                viewname='tags:document_reviewer_list', kwargs={
                    'document_id': self.object_list.first().pk
                }
            )
        else:
            return super().get_post_action_redirect()

    def object_action(self, form, instance):
        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=(permission_tag_remove,),
                user=self.request.user
            )

            tag._event_actor = self.request.user
            tag.remove_from(document=instance)