from django.conf.urls import url

from .api_views import (
    APIDocumentTagAttachView, APIDocumentTagRemoveView,
    APIDocumentTagListView, APITagDocumentListView, APITagListView,
    APITagDetailView
)
from .views import (
    DocumentTagListView, TagAttachActionView, TagCreateView,
    TagDeleteActionView, TagEditView, TagListView, TagRemoveActionView,
    TagDocumentListView, DocumentReviewerListView, ReviewerAttachActionView,
    ReviewerCreateView, ReviewerDeleteActionView, ReviewerEditView, ReviewerListView,
    ReviewerRemoveActionView, ReviewerDocumentListView
)

urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/tags/$',
        name='document_tag_list', view=DocumentTagListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/tags/multiple/attach/$',
        name='tag_attach', view=TagAttachActionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/tags/multiple/remove/$',
        name='single_document_multiple_tag_remove',
        view=TagRemoveActionView.as_view()
    ),
    url(
        regex=r'^documents/multiple/tags/multiple/remove/$',
        name='multiple_documents_selection_tag_remove',
        view=TagRemoveActionView.as_view()
    ),
    url(
        regex=r'^documents/multiple/tags/multiple/attach/$',
        name='multiple_documents_tag_attach',
        view=TagAttachActionView.as_view()
    ),
    url(regex=r'^tags/$', name='tag_list', view=TagListView.as_view()),
    url(
        regex=r'^tags/create/$', name='tag_create',
        view=TagCreateView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_id>\d+)/delete/$', name='tag_delete',
        view=TagDeleteActionView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_id>\d+)/edit/$', name='tag_edit',
        view=TagEditView.as_view()
    ),
    url(
        regex=r'^tags/(?P<tag_id>\d+)/documents/$', name='tag_document_list',
        view=TagDocumentListView.as_view()
    ),
    url(
        regex=r'^tags/multiple/delete/$', name='tag_multiple_delete',
        view=TagDeleteActionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/reviewers/$',
        name='document_reviewer_list', view=DocumentReviewerListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/reviewers/multiple/attach/$',
        name='reviewer_attach', view=ReviewerAttachActionView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/reviewers/multiple/remove/$',
        name='single_document_multiple_reviewer_remove',
        view=ReviewerRemoveActionView.as_view()
    ),
    url(
        regex=r'^documents/multiple/reviewers/multiple/remove/$',
        name='multiple_documents_selection_reviewer_remove',
        view=ReviewerRemoveActionView.as_view()
    ),
    url(
        regex=r'^documents/multiple/reviewers/multiple/attach/$',
        name='multiple_documents_reviewer_attach',
        view=ReviewerAttachActionView.as_view()
    ),
    url(regex=r'^reviewers/$', name='reviewer_list', view=ReviewerListView.as_view()),
    url(
        regex=r'^reviewers/create/$', name='reviewer_create',
        view=ReviewerCreateView.as_view()
    ),
    url(
        regex=r'^reviewers/(?P<tag_id>\d+)/delete/$', name='reviewer_delete',
        view=ReviewerDeleteActionView.as_view()
    ),
    url(
        regex=r'^reviewers/(?P<tag_id>\d+)/edit/$', name='reviewer_edit',
        view=ReviewerEditView.as_view()
    ),
    url(
        regex=r'^reviewers/(?P<tag_id>\d+)/documents/$', name='reviewer_document_list',
        view=ReviewerDocumentListView.as_view()
    ),
    url(
        regex=r'^reviewers/multiple/delete/$', name='reviewer_multiple_delete',
        view=ReviewerDeleteActionView.as_view()
    )
]

api_urls = [
    url(regex=r'^tags/$', view=APITagListView.as_view(), name='tag-list'),
    url(
        regex=r'^tags/(?P<tag_id>[0-9]+)/$', view=APITagDetailView.as_view(),
        name='tag-detail'
    ),
    url(
        regex=r'^tags/(?P<tag_id>[0-9]+)/documents/$',
        view=APITagDocumentListView.as_view(), name='tag-document-list'
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/tags/$',
        view=APIDocumentTagListView.as_view(), name='document-tag-list'
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/tags/attach/$',
        name='document-tag-attach', view=APIDocumentTagAttachView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/tags/remove/$',
        name='document-tag-remove', view=APIDocumentTagRemoveView.as_view()
    ),
]
