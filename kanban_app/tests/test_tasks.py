"""Tests for the task endpoints."""

# 1. Third-party
from django.urls import reverse

# 2. Local
from kanban_app.models import Comment, Task
from kanban_app.tests.test_boards import BoardAPITestCase


class TaskAPITestCase(BoardAPITestCase):
    """Add a valid request body for new tasks."""

    def task_data(self, **changes):
        """Return a valid body for creating a task."""
        data = {
            'board': self.board.id, 'title': 'New task',
            'description': 'Text', 'status': 'to-do', 'priority': 'low',
            'assignee_id': self.member.id, 'reviewer_id': self.owner.id,
            'due_date': '2026-12-24'}
        data.update(changes)
        return data

    def task_url(self):
        """Return the detail url of the test task."""
        return reverse('task-detail', args=[self.task.pk])


class TaskCreateTests(TaskAPITestCase):
    """Check creating tasks."""

    def create(self, **changes):
        """Post a new task."""
        return self.client.post(
            reverse('task-create'), self.task_data(**changes))

    def test_create_needs_login(self):
        """Without a token the answer is 401."""
        self.client.credentials()
        self.assertEqual(self.create().status_code, 401)

    def test_create_task(self):
        """A member creates a task with nested people."""
        response = self.create()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['board'], self.board.id)
        self.assertEqual(response.data['assignee']['id'], self.member.id)
        self.assertEqual(response.data['comments_count'], 0)
        self.assertEqual(Task.objects.get(pk=response.data['id']).created_by,
                         self.owner)

    def test_create_without_people(self):
        """Assignee and reviewer are optional."""
        data = self.task_data()
        del data['assignee_id'], data['reviewer_id']
        response = self.client.post(reverse('task-create'), data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['assignee'])

    def test_create_for_stranger_is_forbidden(self):
        """A user outside of the board gets 403."""
        self.login(self.stranger)
        self.assertEqual(self.create().status_code, 403)

    def test_create_on_missing_board_is_404(self):
        """An unknown board gives 404."""
        self.assertEqual(self.create(board=999).status_code, 404)

    def test_create_with_invalid_board_is_400(self):
        """A board id that is no number gives 400."""
        self.assertEqual(self.create(board='abc').status_code, 400)

    def test_create_with_wrong_status_is_400(self):
        """A status outside of the choices gives 400."""
        self.assertEqual(self.create(status='finished').status_code, 400)

    def test_assignee_must_be_member(self):
        """A person outside of the board cannot be assignee."""
        response = self.create(assignee_id=self.stranger.id)
        self.assertEqual(response.status_code, 400)

    def test_reviewer_must_be_member(self):
        """A person outside of the board cannot be reviewer."""
        response = self.create(reviewer_id=self.stranger.id)
        self.assertEqual(response.status_code, 400)


class TaskUpdateTests(TaskAPITestCase):
    """Check changing and deleting tasks."""

    def test_patch_changes_fields(self):
        """A patch returns the changed task without board."""
        data = {'status': 'done', 'reviewer_id': self.member.id}
        response = self.client.patch(self.task_url(), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'done')
        self.assertEqual(response.data['reviewer']['id'], self.member.id)
        self.assertNotIn('board', response.data)

    def test_patch_can_remove_assignee(self):
        """Sending null removes the assignee."""
        response = self.client.patch(
            self.task_url(), {'assignee_id': None}, format='json')
        self.assertIsNone(response.data['assignee'])

    def test_patch_with_stranger_as_assignee_fails(self):
        """The new assignee must belong to the board."""
        response = self.client.patch(
            self.task_url(), {'assignee_id': self.stranger.id})
        self.assertEqual(response.status_code, 400)

    def test_patch_for_stranger_is_forbidden(self):
        """A stranger cannot change the task."""
        self.login(self.stranger)
        response = self.client.patch(self.task_url(), {'title': 'Hack'})
        self.assertEqual(response.status_code, 403)

    def test_patch_missing_task_is_404(self):
        """An unknown task gives 404."""
        response = self.client.patch(
            reverse('task-detail', args=[999]), {'title': 'x'})
        self.assertEqual(response.status_code, 404)

    def test_board_owner_can_delete(self):
        """The board owner deletes a task of someone else."""
        response = self.client.delete(self.task_url())
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)

    def test_creator_can_delete(self):
        """The creator deletes his own task."""
        self.task.created_by = self.member
        self.task.save()
        self.login(self.member)
        self.assertEqual(self.client.delete(self.task_url()).status_code, 204)

    def test_other_member_cannot_delete(self):
        """A member who is neither creator nor owner gets 403."""
        self.login(self.member)
        self.assertEqual(self.client.delete(self.task_url()).status_code, 403)
        self.assertEqual(Task.objects.count(), 1)


class TaskListTests(TaskAPITestCase):
    """Check the lists of assigned and reviewing tasks."""

    def test_assigned_to_me(self):
        """The assignee sees the task, including the board id."""
        self.login(self.member)
        response = self.client.get(reverse('tasks-assigned'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['board'], self.board.id)

    def test_assigned_list_is_empty_for_others(self):
        """Someone without assigned tasks gets an empty list."""
        response = self.client.get(reverse('tasks-assigned'))
        self.assertEqual(response.data, [])

    def test_reviewing(self):
        """The reviewer sees the task with its comment counter."""
        self.task.reviewer = self.owner
        self.task.save()
        response = self.client.get(reverse('tasks-reviewing'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['comments_count'],
                         Comment.objects.count())

    def test_lists_need_login(self):
        """Without a token both lists answer 401."""
        self.client.credentials()
        for name in ('tasks-assigned', 'tasks-reviewing'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 401)
