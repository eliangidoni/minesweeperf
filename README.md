# minesweeper

Minesweeper game implementation as a JSON REST service.
Implemented with Django REST framework and PostgreSQL.

There is a Go client library in https://github.com/eliangidoni/minesweepergo
##Missing features##
- Time tracking.
- Multiple user accounts

##Development environment
Requires Docker and Docker Composer. Scripts to create/start/stop the service are in `/scripts/`

##First Run
```
python manage.py migrate auth
python manage.py migrate
python manage.py createsuperuser
```
##Service start
```
python manage.py runserver
```
