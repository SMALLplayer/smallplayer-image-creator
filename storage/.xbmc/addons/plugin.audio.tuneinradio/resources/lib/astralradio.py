#/*
# *
# * TuneIn Radio: TuneIn add-on for XBMC.
# *
# * Copyright (C) 2012 Brian Hornsby
# *	
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *	
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *	
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import simplejson
import urllib2

class AstralRadio:
	def __init__(self, url):
		self.__url__ = url
		return

	def get_stream_url(self):
		if not self.__url__:
			return None
		# Workout json config path
		f = urllib2.urlopen(self.__url__)
		html = f.read()
		start = html.find('jsonConfigPath:')
		end = html.find('\n', start)
		configpath = html[start:end]
		start = configpath.find('"')
		end = configpath.find('"', start+1)
		configpath = configpath[start+1:end]
		
		# Read json config for station
		f = urllib2.urlopen(self.__url__ + configpath)
		config = simplejson.load(f)
		# Create rtmp stream url
		if config.has_key('akamaiAudio_serverMount'):
			rtmpurl = 'rtmp://%s/%s' % (config['akamaiAudio_serverMount'][0], config['AAC_Audio_stream'])
			swfurl = config['player_siteBase']
			return '%s swfurl=%s/ swfvfy=true pageurl=%s/ live=true' % (rtmpurl, swfurl, swfurl)
		else:
			return None