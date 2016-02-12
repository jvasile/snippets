#!/usr/bin/env python

"""fetch_gcal.py
Copyright 2016 James Vasile <james@jamesvasile.com>
Published under the terms of the Affero GPL, version 3 or later

You will need the private url, which you can get from a calendar's
details settings page in the "Private Address" section.  Note that if
you do not see a "Private Address" section on the details settings
page for the calendar you want to share, it might need to be enabled
in admin.  I have google apps for your domain and had to go to
admin.google.com and change the calendar app settings to allow
external sharing of information.  The default is to hide event
details.  Then I reloaded the calendar and the settings page had a
"Private Address" section.  I clicked on the Ical button to see the
private url.

Call from crontab to keep calendar updated.

You'll want the ical2org in this repo, not the awk one mentioned at
http://orgmode.org/worg/org-tools/index.html, as I've fixed some bugs
in it.  If anybody knows where upstream to submit those bug fixes,
please let me know.  I haven't tried the Ruby version.
"""

config_fname = "~/.config/jamesvasile.com/fetch_gcal"

import certifi
import datetime
from fabric.api import hide, local
import logging
import os
import sys
import time
import urllib3

import util as u

logger = u.make_logger("fetch_gcal", "INFO")

class GCalFetcher():
    def __init__(self, config_fname):
        self.config = u.fetch_json(config_fname)

        # set default prefix
        if not "prefix" in self.config or not self.config['prefix']:
            self.config['prefix'] = "gcal_"

        # self.calendars is the dict that holds information about all the calendars we know about.
        self.calendars = self.config['calendars']

    def fetch_cals(self, cals=None):
        """
        Download calendars to disk.
    
        cals is a list of the calendars we should process.  Just ignore the others.
        """
        # Turn cals in to a dict of calendars hashed to URLs
        cals = { k: v for k, v in self.calendars.items() if k in cals }

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        for name, url in cals.items():
            fname = os.path.join(self.config['ics dir'], self.config['prefix']+name+".ics")
            org_fname = os.path.join(self.config['org dir'], self.config['prefix']+name+".org")

            # Be polite, don't fetch more than once every 10 minutes
            if os.path.exists(fname):
                mtime = os.stat(fname).st_mtime
                t = datetime.datetime.strptime(time.ctime(mtime), "%a %b %d %H:%M:%S %Y")
                now = datetime.datetime.now()
                delta = now - t
                logger.debug("{0}: {1}".format(fname, delta))
                if delta.seconds < 60*10:
                    if logger.getEffectiveLevel() > logging.DEBUG:
                        # be polite, unless we're debugging, in which case, be ruthless
                        continue

            # Fetch calendar
            logger.info("Fetching " + name)
            r = http.request('GET', url)
            if r.status != 200:
                # TODO: send me an email telling me the calendar system is broken if we have net connectivity right now
                pass

            if r.data:
                if os.path.exists(fname) and self.remove_dtstamp(u.slurp(fname))==self.remove_dtstamp(r.data):
                    ## Mark the data files with current time so we know they're up to date
                    with hide("running", "output"):
                        logger.debug("Updating timestamp for " + fname)
                        local("touch " + fname)
                        logger.debug("Updating timestamp for " + fname)
                        local("touch " + org_fname)
                    continue

                # Back up the ical file before we blow it away.
                if logger.getEffectiveLevel() <= logging.INFO:
                    logger.debug("Backing up {0} to {0}".format(fname))
                    with hide("running", "output"):
                        local('cp {0} {0}.bak'.format(fname))

                with open (fname, 'w') as OUTF:
                    logger.info('Writing ' + fname)
                    OUTF.write(r.data)
            else:
                logger.error("ICS calendar data fetch came back blank for {0}?\n".format(name))

    def remove_dtstamp(self, gcal):
        return "\n".join([l for l in gcal.split("\n") if not l.startswith("DTSTAMP:")])

    def convert_to_org(self, cals):
        for name in cals:
            ics_fname = os.path.join(self.config['ics dir'], self.config['prefix']+name+".ics")
            org_fname = os.path.join(self.config['org dir'], self.config['prefix']+name+".org")
            if u.time_to_build(ics_fname, org_fname):
                with hide("running", "output"):
                    logger.info("Writing " + org_fname)
                    local("{3} -v category={2} < {0} 2>/dev/null 1> {1}".format(ics_fname, org_fname, name, self.config['ical2org']))

def main():
    gcf = GCalFetcher(config_fname)
    config = u.fetch_json(config_fname)
    calendars = config['calendars']

    cals = gcf.calendars.keys()
    if len(sys.argv) > 1:
        cals = sys.argv[1:]
    
    gcf.fetch_cals(cals)
    gcf.convert_to_org(cals)

if __name__ == "__main__":
    main()
