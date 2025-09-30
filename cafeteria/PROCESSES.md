## Update OS packages
1. `sudo apt update`
2. `sudo apt dist-upgrade`
3. it's a good idea to reboot the server at this point `sudo shutdown -r now`
4. `sudo apt autoremove`
5. `sudo apt autoclean`

## Updating dependencies
1. cd into the lunch-server/KnightsLunchManager directory `cd lunch-server/KnightsLunchManager`
2. run `git pull`
3. cd into the lunch-server directory `cd ..`
4. activate the virtual environment `source ./bin/activate`
5. update dependencies with `pip install --upgrade -r KnightsLunchManager/requirements.txt`
6. deactivate the virtual environment `deactivate`
7. restart services
    - `sudo service gunicorn restart`
    - `sudo service nginx restart`

## End of year process
This should be completed after PowerSchool is rolled over to the upcoming school year. In the Lunch Management portal, ensure the Current School Year, under General Settings, is set to the year that was just completed.
1. perform a full database backup `sh ./scripts/db_backup.sh`
2. cd into db_backups `cd db_backups`
3. verify a new backup has been created `ls -lh`
4. cd into the lunch-server directory `cd ..`
5. activate the virtual environment `source ./bin/activate`
6. cd into the KnightsLunchManager directory `cd KnightsLunchManager`
7. sync with powerschool `python manage.py sync_powerschool`
8. run the EOY process `python manage.py process_eoy`
9. mark students as inactive `python manage.py mark_inactive`
