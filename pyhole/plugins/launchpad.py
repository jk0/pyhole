#   Copyright 2011-2016 Paul Voccio
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pyhole Launchpad Plugin"""

import time
import json

from launchpadlib.launchpad import Launchpad as LP
from launchpadlib.credentials import Credentials
from lazr.restfulclient.errors import HTTPError

from pyhole.core import plugin
from pyhole.core import utils

CONF = utils.get_config("Launchpad")



class Launchpad(plugin.Plugin):
    """Provide access to the Launchpad API."""

    def __init__(self, session):
        self.session = session
        self.nick_cache = {}
        # {'nick': 'launchpad-username',...}
        self.nick_cache_file = CONF.get("nick_cache")
        self.token_cache_file = CONF.get("token_cache")
        self.name = self.__class__.__name__
        
        self.auth_app_name = "{nick}@{app}".format(nick=self.session.nick,
                                                   app=CONF.get("app_name"))
        self.service_root = CONF.get("service_root")
        self.target = CONF.get("target")
        self.delay_between = CONF.get("delay_between", type="int")
        self.contact = CONF.get("contact")  # whos being represented by the bot
        self.credentials = Credentials(self.auth_app_name)  # "bot@pyhole"
        self._authed = False
    
    @property
    def authed(self):
        return self._authed

    def persist_token(self):
        if self.authed:
            token = self.credentials.access_token
            try:
                with open(self.token_cache_file, 'w') as outfile:
                    outfile.write(token)
            except:
                self.session.privmsg(self.contact,
                                     "Problem persisting token")

    def retrieve_token(self):
        if self.authed:
            return True  # already authed
        token = None
        try:
            with open(self.token_cache_file, 'r') as infile:
                token = infile.readline().strip()
        except:
            self.session.privmsg(self.contact,
                                 "Problem retrieving token")
            return False
        self.credentials = Credentials(self.auth_app_name)
        self.credentials.access_token = token
        return True

    @plugin.hook_add_command("lauth")
    @utils.admin
    @utils.spawn
    def authenticate(self, message, params=None, **kwargs):
        try:
            auth_delay = CONF.get("auth_delay", type="int")
            req_token_info = self.credentials.get_request_token(
                web_root='production')
            msg = ('Authenticate {app} as READ ANYTHING at: {token_info} '
                    'within {delay} seconds'.format(app=self.auth_app_name,
                                                    token_info=req_token_info,
                                                    delay=auth_delay))
            self.session.privmsg(self.contact, msg)
            # Get back a string that looks like 
            # 'https://launchpad.net/+authorize-token?oauth_token=...'
            # This is the URL your end-user needs to visit in order to
            # authorize your token.
            # Give the user a moment to authorize the application
            time.sleep(auth_delay)
            try:
                if not self.credentials.access_token:
                    self.credentials.exchange_request_token_for_access_token(
                        web_root=self.target)
                self.launchpad = LP(self.credentials, None, None,
                                    service_root='production')
                self.session.privmsg(self.contact, "Launchpad authenticated.")
                self._authed = True
            except HTTPError:
                # user hasn't authorized the token yet.
                msg = "Not approved in the alloted time of %s seconds."
                self.session.privmsg(self.contact, msg % auth_delay)
                self.launchpad = LP.login_anonymously(
                    self.app_name, self.target, utils.get_directory(self.name))
        except AssertionError, e:
            self.session.privmsg(self.contact, str(e.message))
        except Exception, e:
            self.session.privmsg(
                self.contact, "Unhandled error authenticating"
                              " Launchpad: %s" % e.message)
            raise

    def update_nick_cache(self, person, nick):
        self.nick_cache[nick.lower()] = person.name
        try:
            with open(self.nick_cache_file, 'w') as outfile:
                json.dump(self.nick_cache, outfile)
        except:
            raise

    def search_nick_cache(self, person_or_nick):
        try:
            with open(self.nick_cache_file, 'r') as infile:
                self.nick_cache = json.load(infile)
        except ValueError, e:
            self.session.privmsg(self.contact,
                                 "Error opening %s" % self.nick_cache_path)
        if person_or_nick.lower() in self.nick_cache.keys():
            return self.nick_cache[person_or_nick.lower()]
        return None
 
    @plugin.hook_add_command("l411")
    @utils.require_params
    @utils.spawn
    def l411(self, message, params=None, **kwargs):
        """Launchpad person contact info (ex: .l411 <user>).
        person: ['self_link', 'web_link', 'resource_type_link', 'http_etag', 
        'date_created', 'description', 'display_name', 'hide_email_addresses',
        'homepage_content', 'is_probationary', 'is_team',
        'is_ubuntu_coc_signer', 'is_valid', 'karma', 'latitude', 'longitude',
        'mailing_list_auto_subscribe_policy', 'name', 'private', 'time_zone',
        'visibility']
        """
        if not self.authed:
            message.dispatch("Must authenticate first, ex: .lauth")
            return
        _person_name = params
        _just_cache_nicks = False
        message.dispatch(u"Looking up '%s'" % _person_name)
        try:
            noise = 0
            t = ''
            skipped = []
            cached_nick = self.search_nick_cache(_person_name)
            if cached_nick:
                # we know exactly who to search for
                t = u"{un} might be ".format(un=_person_name,
                                                p=cached_nick)
                all_people = self.launchpad.people.find(
                    text=cached_nick)
            else:
                all_people = self.launchpad.people.find(text=_person_name)
            for _i, person in enumerate(all_people):
                if person.karma < 1:
                    if _i > 5:
                        skipped.append(person)
                        continue  # skip sleep
                else:
                    if noise > 5:
                        message.dispatch("... there are more matches for '{n}'"
                                         ". Narrow the results by being more "
                                         "specific.".format(n=_person_name))
                        # TODO: throw large results in a gist and PM it
                        _just_cache_nicks = True
                    msg = (t+ u"{dn} | username: {un} | email: {e} | nicks: {n} "
                            "| karma: {k} | web link: {w} | date created: "
                            "{dc} | valid: {v} | tz: {tz}")
                    _nicks = self._make_nicks(person)
                    if not _just_cache_nicks:
                        _emails = self._make_emails(person)
                        _full_message = msg.format(
                                dn=person.display_name,
                                un=person.name,
                                e=_emails,
                                n=_nicks,
                                k=person.karma,
                                w=person.web_link,
                                dc=person.date_created,  # TODO: relative
                                v=person.is_valid,
                                tz=person.time_zone)
                        message.dispatch(_full_message)
                        noise += 1
                        time.sleep(self.delay_between)
            if len(skipped) > 0:
                message.dispatch("Skipped %s with < 1 karma" % len(skipped))
        except KeyError:
            msg = u"Unable to find user '%s' in Launchpad."
            message.dispatch(msg % _person_name)
        message.dispatch(u"No more matches for '%s'" % _person_name)

    def _make_nicks(self, person):
        t = '{nick} on {network} '
        ret = ''
        if person.irc_nicknames:
            for _i, _nick in enumerate(person.irc_nicknames):
                if _i < 5:
                    ret += t.format(nick=_nick.nickname,
                                    network=_nick.network)
                self.update_nick_cache(person, _nick.nickname)
        return ret

    def _make_emails(self, person):
        t = '{e} '
        ret = ''
        ret += "*" + t.format(e=person.preferred_email_address_link.split('/')[-1:][0])
        for addr in person.confirmed_email_addresses[:5]:
            ret += t.format(e=addr.email)
        return ret

