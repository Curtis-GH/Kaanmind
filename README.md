# KanMind Backend

REST API for KanMind, a Kanban board application. Users can register,
create boards, share them with other users, manage tasks and comment on them.
The frontend is **not** part of this repository.

> Work in progress: the endpoints are added step by step.

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

5. Create the database and start the server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/api/`.

## Frontend and CORS

The frontend is served separately (for example with the VS Code Live Server
extension). Requests from `127.0.0.1` and `localhost` on the ports `5500`
and `5501` are allowed by the CORS settings in `core/settings.py`.

## Authentication

Every endpoint except registration and login requires a token:

```
Authorization: Token <your-token>
```

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
