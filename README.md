# minesweeper

Minesweeper game implementation as a JSON REST service.
Implemented with Flask micro framework and SQLAlchemy.

There is a Go client library in https://github.com/eliangidoni/minesweepergo
## Missing features
- Time tracking.
- Multiple user accounts

## Development environment
Requires Docker and Docker Composer.

## First Run
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
## Service start
```
python run.py 0.0.0.0:8000
```
