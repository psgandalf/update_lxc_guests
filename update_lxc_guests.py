#!/usr/bin/python3
#
# update_lxc_guests.py
#
# Authors:
# Mikael Eklund <mikael@eklundhome.com
# Based on https://www.stgraber.org/2014/02/05/lxc-1-0-scripting-with-the-api/
# By Stéphane Graber
#
# This program if free software; you can redistribute it and/or
# modify it as you like.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# I have tested it Under Ubuntu 14.04.
#

import lxc, sys, logging, time
logging.basicConfig(filename='lxc_update.log',level=logging.DEBUG)
logging.debug('Starting update of all guests '+ (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M ")))
start = time.time()
for container in lxc.list_containers(as_object=True):
    # Start the container (if not started)
    logging.debug('Guest: ' + container.name+" processed")
    started=False
    if not container.running:
        if not container.start():
            continue
            logging.debug('Could not start guest to update OS')
        started=True
        logging.debug('Guest not started. Starting it to be able to update OS')

    if not container.state == "RUNNING":
        continue

    # Wait for connectivity
    if not container.get_ips(timeout=30):
        continue

    # Run the updates
    logging.debug('Running apt-get update')
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "update"])
    logging.debug('Running apt-get dist-upgrade')
    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "dist-upgrade", "-y"])
    # Shutdown the container
    if started:
        if not container.shutdown(30):
            container.stop()
        logging.debug('Shutting down guest that wasnt runnging when script startes')

    logging.debug(' ')
duration = time.time() - start
logging.debug('Update of ' + str(len(lxc.list_containers(as_object=True))) + ' guests took ' + str(int(duration)) + ' sec')
logging.debug(' ')
logging.debug(' ')
