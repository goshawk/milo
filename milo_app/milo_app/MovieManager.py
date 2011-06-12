from MediaRetriever import MediaRetriever
from resources import *
import urllib
import urllib2
import urlparse
import os
import datetime
from mongoengine import connect

basepath = os.path.join(os.path.split(os.path.abspath( __file__ ))[0], 'static', 'movie_data')

class MovieManager(object):
	def add_movie(self, name=None):
		m = MediaRetriever(name)
		image = m.get_image().get('image')
		d = m.get_info()
		poster = d.get('poster')
		description = d.get('description')
		year = d.get('year')
		title = d.get('title')
		genre = d.get('genre')
		trailer = m.get_trailer().get('trailer')
		if image is not None:
			fi = open(os.path.join(basepath, title+'_image.jpg'), 'w')
			fi.write(urllib.urlopen(image).read())
		if poster is not None:
			fp = open(os.path.join(basepath, title+'_poster.jpg'), 'w')
			fp.write(urllib.urlopen(poster).read())
		if len(Movie.objects(title=title, date=datetime.datetime(year=int(year), month=1, day=1))) == 0:
			movie = Movie(title=title, date=datetime.datetime(year=int(year), month=1, day=1), description=description, image=title+'_image.jpg', poster=title+'_poster.jpg', trailer=trailer, genre=genre)
			print 'saving movie'
			movie.save()
			
			#create a Whisperer Item here - HAVE TO TEST WITH NEW MOVIES =/!
			whisperer_url = 'http://whisperer.vincenzo-ampolo.net/item/add'
			data = urllib.urlencode({'name':title})
			req = urllib2.Request(whisperer_url, data)
			#Testing if it works -> should print in the command line the new user email and ID or an error message, if the user already exists (shouldn't be the case...)
			response = urllib2.urlopen(req)
			whisperer_page = response.read() 
			print whisperer_page
			

#LOOP THROUGH ALL METADATA
#ADD ALL STRINGS IN ONE ONLY LIST THE SPLIT! #DESCRIPTION #TITLE #GENRES #ACTORS #DIRECTORS #YEAR
#DONT DO IT -> THERE IS THE "TYPE" -> better to do a for to each single list....
#URL_FIX =D

#YEAR EXAMPLE
			#Create metadata and add to item -> loop to all metadata! -> example of the release date
			#whisperer_url = url_fix('http://whisperer.vincenzo-ampolo.net/item/'+title+'/addMetadata')
			#print whisperer_url
			#data = urllib.urlencode({'name':year,'type':'year','lang':'eng'})          
			#print data
			#req = urllib2.Request(whisperer_url, data)
			#print req
			##Testing if it works -> should print in the command line the new user email and ID or an error message, if the user already exists (shouldn't be the case...)
##PROBLEM HERE! AGAIN TITLE INVOLVED... MUST BE THE SPACING!
			#response = urllib2.urlopen(req)
			#whisperer_page = response.read() 
			#print whisperer_page

			
			return movie
		return None
		
	def delete_movie(self, name=None):
		m = MediaRetriever(name)
		d = m.get_info()
		print d.get('title')
		print Movie.objects(title=d.get('title'))
		for movie in Movie.objects(title=d.get('title')):
			print movie.genre, movie.title
			movie.save()
			for f_ile in [movie.poster, movie.image]:
				path = os.path.join(basepath, f_ile)
				if os.path.exists(path):
					os.remove(path)
			movie.delete()
	
def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
			
if __name__ == '__main__':
	
	import unittest
	
	class Test_MovieManager(unittest.TestCase):
		def setUp(self):
			connect('milo')
			self.mm = MovieManager()
		
		def test_add_movie(self):
			for movie in ['the notebook', 'rio', 'matrix', 'caimano', 'matrix reload']:
				self.mm.add_movie(name=movie)
				m = MediaRetriever(movie)
				self.assertEqual(len(Movie.objects(title=m.get_info().get('title'))), 1)
		
		@unittest.skip("delete sucks")
		def test_delete_movie(self):
			for movie in ['the notebook', 'rio', 'matrix', 'caimano', 'matrix reload']:
				m = MediaRetriever(movie)
				self.mm.delete_movie(name=movie)
				self.assertEqual(len(Movie.objects(title=m.get_info().get('title'))), 0)
		
		
		def test_import_basic_movies(self):
			#movies = ['rio', 'matrix', 'matrix reloaded',  'matrix revolutions', 'the notebook', 'along came polly',  'vanilla sky', 'batman begins', 'butterfly effect', 'the godfather', 'inception', 'city of god', 'forrest gump', 'finding nemo', 'back to the future', 'gladiator', "the king's speech", 'the milionaire', 'slumdog millionaire', 'kill bill', 'toy story 1', 'toy story 2', 'toy story 3', 'avatar', 'how to train your dragon', 'ratatouille', 'the social network', 'rocky', 'thron legacy', 'letters from iwo jima', 'il caimano', 'shutter island', 'monsters inc', 'v for vendetta', 'amores perros']
			movies = ['thor']
			for movie in movies:
				print 'adding '+movie
				self.mm.add_movie(name=movie)
				
	unittest.main()
