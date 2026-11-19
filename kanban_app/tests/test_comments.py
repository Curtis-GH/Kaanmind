"""Tests for the comment endpoints."""

# 1. Third-party
from django.urls import reverse

# 2. Local
from kanban_app.models import Comment
from kanban_app.tests.test_boards import BoardAPITestCase


class CommentAPITestCase(BoardAPITestCase):
    """Give every comment test the urls of the example task."""

    def list_url(self, task_id=None):
        """Return the comment list url of a task."""
        return reverse('comment-list', args=[task_id or self.task.pk])

    def delete_url(self, comment_id, task_id=None):
        """Return the delete url of a comment."""
        return reverse(
            'comment-delete', args=[task_id or self.task.pk, comment_id])


class CommentListTests(CommentAPITestCase):
    """Check listing and creating comments."""

    def test_list_needs_login(self):
        """Without a token the answer is 401."""
        self.client.credentials()
        self.assertEqual(self.client.get(self.list_url()).status_code, 401)

    def test_list_shows_author_name(self):
        """The author is shown as full name text."""
        response = self.client.get(self.list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['author'], 'Olga Owner')
        keys = sorted(response.data[0])
        self.assertEqual(keys, ['author', 'content', 'created_at', 'id'])

    def test_list_is_oldest_first(self):
        """The oldest comment comes first."""
        Comment.objects.create(
            task=self.task, author=self.member, content='second')
        response = self.client.get(self.list_url())
        texts = [c['content'] for c in response.data]
        self.assertEqual(texts, ['c', 'second'])

    def test_list_for_stranger_is_forbidden(self):
        """A user outside of the board gets 403."""
        self.login(self.stranger)
        self.assertEqual(self.client.get(self.list_url()).status_code, 403)

    def test_list_of_missing_task_is_404(self):
        """An unknown task gives 404."""
        self.assertEqual(self.client.get(self.list_url(999)).status_code, 404)

    def test_create_comment(self):
        """The author is taken from the token."""
        self.login(self.member)
        response = self.client.post(self.list_url(), {'content': 'Hi'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], 'Max Member')
        self.assertEqual(self.task.comments.count(), 2)

    def test_create_empty_comment_fails(self):
        """An empty content gives 400."""
        response = self.client.post(self.list_url(), {'content': ''})
        self.assertEqual(response.status_code, 400)

    def test_create_for_stranger_is_forbidden(self):
        """A stranger cannot comment."""
        self.login(self.stranger)
        response = self.client.post(self.list_url(), {'content': 'Hi'})
        self.assertEqual(response.status_code, 403)

    def test_create_on_missing_task_is_404(self):
        """An unknown task gives 404."""
        response = self.client.post(self.list_url(999), {'content': 'Hi'})
        self.assertEqual(response.status_code, 404)


class CommentDeleteTests(CommentAPITestCase):
    """Check deleting comments."""

    def test_author_can_delete(self):
        """The author deletes the comment and gets 204."""
        comment = Comment.objects.get()
        response = self.client.delete(self.delete_url(comment.pk))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), 0)

    def test_other_member_cannot_delete(self):
        """A member who is not the author gets 403."""
        self.login(self.member)
        url = self.delete_url(Comment.objects.get().pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)

    def test_missing_comment_is_404(self):
        """An unknown comment gives 404."""
        self.assertEqual(
            self.client.delete(self.delete_url(999)).status_code, 404)

    def test_comment_of_other_task_is_404(self):
        """The comment must belong to the task in the url."""
        comment = Comment.objects.get()
        url = self.delete_url(comment.pk, task_id=999)
        self.assertEqual(self.client.delete(url).status_code, 404)

    def test_delete_needs_login(self):
        """Without a token the answer is 401."""
        self.client.credentials()
        url = self.delete_url(Comment.objects.get().pk)
        self.assertEqual(self.client.delete(url).status_code, 401)
