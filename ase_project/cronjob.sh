#!/bin/bash
while true;
do python manage.py runcrons;
sleep 30;
done
