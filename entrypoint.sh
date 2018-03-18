#!/bin/bash
set -e


#if [ -z "$TAIGA_SKIP_DB_CHECK" ]; then
DB_CHECK_STATUS=$(python3.6 /scripts/checkdb.py)


if [[ $DB_CHECK_STATUS == "missing_flask_users" ]]; then
  # Setup database automatically if needed
  echo "Configuring initial database"
  python3.6 wsgi.py deploy
fi
#fi

# # Look for static folder, if it does not exist, then generate it
# if [ "$(ls -A /home/taiga/static 2> /dev/null)" == "" ]; then
#   python /home/taiga//taiga-back/manage.py collectstatic --noinput
# fi

gunicorn --workers=3 wsgi:app -b 0.0.0.0:5000

exec "$@"
