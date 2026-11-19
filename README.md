# KanMind Backend

REST API for KanMind, a Kanban board application. Users can register,
create boards, share them with other users, manage tasks and comment on them.
The frontend is **not** part of this repository.

## Requirements

- Python 3.12 or newer
- pip

## Setup

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set the environment variables (see `.env.example`):

   | Variable | Description | Default (development only) |
   |---|---|---|
   | `DJANGO_SECRET_KEY` | Secret key of the Django project | insecure dev key |
   | `DJANGO_DEBUG` | `True` or `False` | `True` |

   The project does not load a `.env` file by itself. Export the values in
   your shell before starting the server.

5. Create the database, the guest user and start the server:

   ```bash
   python manage.py migrate
   python manage.py create_guest_user
   python manage.py runserver
   ```

6. Optional: create test accounts with an example board (see
   [Test accounts](#test-accounts)):

   ```bash
   python manage.py create_demo_data
   ```

The API is available at `http://127.0.0.1:8000/api/`.

## Guest user

The frontend has a guest login button with fixed credentials. The command
`python manage.py create_guest_user` creates this user (email
`kevin@kovacsi.de`). Running it more than once changes nothing.

## Test accounts

`python manage.py create_demo_data` creates three users with the password
`testpass123` (`alice@test.de`, `bob@test.de`, `carol@test.de`) and a demo
board owned by Alice with Bob as member, three tasks and one comment. Running
it more than once changes nothing. Use these accounts only for development.

## Frontend and CORS

The frontend is served separately (for example with the VS Code Live Server
extension). Requests from `127.0.0.1` and `localhost` on the ports `5500`
and `5501` are allowed by the CORS settings in `core/settings.py`.

## Authentication

Every endpoint except registration and login requires a token:

```
Authorization: Token <your-token>
```

## Endpoints

All paths start with `/api/`. Endpoints marked with a lock need the token.

| Method | Path | Description | Lock |
|---|---|---|---|
| POST | `registration/` | Register a user (201) | no |
| POST | `login/` | Log in and get a token (200) | no |
| GET | `boards/` | Boards of the user with counters | yes |
| POST | `boards/` | Create a board (201) | yes |
| GET | `boards/{id}/` | Board with members and tasks | yes |
| PATCH | `boards/{id}/` | Change title and members | yes |
| DELETE | `boards/{id}/` | Delete a board, owner only (204) | yes |
| GET | `email-check/?email=` | Find a user by email | yes |
| POST | `tasks/` | Create a task (201) | yes |
| PATCH | `tasks/{id}/` | Change a task | yes |
| DELETE | `tasks/{id}/` | Delete a task, creator or board owner (204) | yes |
| GET | `tasks/assigned-to-me/` | Tasks assigned to the user | yes |
| GET | `tasks/reviewing/` | Tasks the user has to review | yes |
| GET | `tasks/{id}/comments/` | Comments of a task, oldest first | yes |
| POST | `tasks/{id}/comments/` | Add a comment (201) | yes |
| DELETE | `tasks/{id}/comments/{comment_id}/` | Delete a comment, author only (204) | yes |

Typical errors: `400` invalid data, `401` no or wrong token, `403` not allowed
(for example a user who is not a member of the board), `404` not found.

## Project structure

| Folder | Purpose |
|---|---|
| `core/` | Project settings and central URL routing |
| `auth_app/` | Registration and login |
| `kanban_app/` | Boards, tasks and comments |

Each app keeps its API code in an `api/` folder (serializers, views,
permissions, urls).

## Development

```bash
python manage.py test      # run the tests
coverage run manage.py test
coverage report            # test coverage
flake8                     # code style check
```
