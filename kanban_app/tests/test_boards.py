"""Tests for the board and email check endpoints."""

# 1. Third-party
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

# 2. Local
from kanban_app.models import Board, Comment, Task


class BoardAPITestCase(APITestCase):
    """Create users, a board and log in the owner."""

    def setUp(self):
        """Create owner, member, stranger, one board and one task."""
        self.owner = self.make_user('owner@mail.de', 'Olga Owner')
        self.member = self.make_user('member@mail.de', 'Max Member')
        self.stranger = self.make_user('stranger@mail.de', 'Sam Stranger')
        self.board = Board.objects.create(title='Project X', owner=self.owner)
        self.board.members.set([self.owner, self.member])
        self.task = Task.objects.create(
            board=self.board, title='Task', due_date='2026-12-01',
            priority='high', assignee=self.member)
        Comment.objects.create(task=self.task, author=self.owner, content='c')
        self.login(self.owner)

    def make_user(self, email, name):
        """Create a user the same way the registration does."""
        return User.objects.create_user(
            username=email, email=email, password='pw', first_name=name)

    def login(self, user):
        """Send the token of the user with every request."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def detail_url(self):
        """Return the detail url of the test board."""
        return reverse('board-detail', args=[self.board.pk])


class BoardListTests(BoardAPITestCase):
    """Check listing and creating boards."""

    def test_list_needs_login(self):
        """Without a token the list answers 401."""
        self.client.credentials()
        response = self.client.get(reverse('board-list'))
        self.assertEqual(response.status_code, 401)

    def test_list_shows_counters(self):
        """The list contains the counters from the endpoint doc."""
        response = self.client.get(reverse('board-list'))
        board = response.data[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(board['member_count'], 2)
        self.assertEqual(board['ticket_count'], 1)
        self.assertEqual(board['tasks_to_do_count'], 1)
        self.assertEqual(board['tasks_high_prio_count'], 1)
        self.assertEqual(board['owner_id'], self.owner.id)

    def test_list_hides_foreign_boards(self):
        """A user only sees boards that he owns or belongs to."""
        self.login(self.stranger)
        response = self.client.get(reverse('board-list'))
        self.assertEqual(response.data, [])

    def test_member_sees_the_board(self):
        """A member sees the board in the list."""
        self.login(self.member)
        response = self.client.get(reverse('board-list'))
        self.assertEqual(len(response.data), 1)

    def test_create_board(self):
        """Creating a board returns 201 and adds the owner as member."""
        data = {'title': 'New', 'members': [self.member.id]}
        response = self.client.post(reverse('board-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['member_count'], 2)
        self.assertEqual(response.data['owner_id'], self.owner.id)

    def test_create_without_title_fails(self):
        """A board needs a title."""
        response = self.client.post(reverse('board-list'), {'members': []})
        self.assertEqual(response.status_code, 400)

    def test_create_without_members_works(self):
        """The members are optional."""
        response = self.client.post(reverse('board-list'), {'title': 'Solo'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['member_count'], 1)


class BoardDetailTests(BoardAPITestCase):
    """Check showing, changing and deleting one board."""

    def test_detail_shows_members_and_tasks(self):
        """The detail has nested members and tasks."""
        response = self.client.get(self.detail_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']), 2)
        task = response.data['tasks'][0]
        self.assertEqual(task['assignee']['fullname'], 'Max Member')
        self.assertEqual(task['comments_count'], 1)

    def test_detail_for_stranger_is_forbidden(self):
        """A user outside of the board gets 403."""
        self.login(self.stranger)
        response = self.client.get(self.detail_url())
        self.assertEqual(response.status_code, 403)

    def test_detail_of_missing_board_is_404(self):
        """An unknown board id gives 404."""
        response = self.client.get(reverse('board-detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_patch_changes_title_and_members(self):
        """A patch returns the new title and the nested people."""
        data = {'title': 'Renamed', 'members': [self.stranger.id]}
        response = self.client.patch(self.detail_url(), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Renamed')
        self.assertEqual(response.data['owner_data']['id'], self.owner.id)
        self.assertEqual(len(response.data['members_data']), 2)

    def test_patch_title_only_keeps_members(self):
        """Without members in the body the members stay as they are."""
        self.client.patch(self.detail_url(), {'title': 'Only title'})
        self.assertEqual(self.board.members.count(), 2)

    def test_patch_for_stranger_is_forbidden(self):
        """A stranger cannot change the board."""
        self.login(self.stranger)
        response = self.client.patch(self.detail_url(), {'title': 'Hack'})
        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete(self):
        """The owner deletes the board and gets 204."""
        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Board.objects.count(), 0)

    def test_member_cannot_delete(self):
        """A normal member may not delete the board."""
        self.login(self.member)
        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Board.objects.count(), 1)


class EmailCheckTests(BoardAPITestCase):
    """Check the search for users by email."""

    def check(self, email=None):
        """Call the email check with an optional email."""
        params = {'email': email} if email else {}
        return self.client.get(reverse('email-check'), params)

    def test_known_email_returns_user(self):
        """An existing email returns id, email and fullname."""
        response = self.check('Member@mail.de')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.member.id)
        self.assertEqual(response.data['fullname'], 'Max Member')

    def test_unknown_email_is_404(self):
        """A valid but unknown email gives 404."""
        self.assertEqual(self.check('nobody@mail.de').status_code, 404)

    def test_missing_or_invalid_email_is_400(self):
        """No email or a wrong format gives 400."""
        self.assertEqual(self.check().status_code, 400)
        self.assertEqual(self.check('no-email').status_code, 400)

    def test_needs_login(self):
        """Without a token the check answers 401."""
        self.client.credentials()
        self.assertEqual(self.check('member@mail.de').status_code, 401)
