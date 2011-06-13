from views import *
import urllib
import urllib2
import urlparse
from MovieManager import url_fix

@view_config(name='wizard', context='milo_app:resources.Root',
				 renderer='templates/wizard.pt')
@view_config(name='1', context='milo_app:resources.Survey',
				 renderer='templates/step1.pt')
@view_config(name='2', context='milo_app:resources.Survey',
				 renderer='templates/step2.pt')
@view_config(name='3', context='milo_app:resources.Survey',
				 renderer='templates/step3.pt')
@view_config(name='4', context='milo_app:resources.Survey',
				 renderer='templates/step4.pt')
@view_config(name='5', context='milo_app:resources.Survey',
				 renderer='templates/step5.pt')
@view_config(name='finish', context='milo_app:resources.Survey',
				 renderer='templates/finish.pt')                                                          
def survey(request):
	
	#Declare
	rating_finished = None	
    
	#Session: control current step
	session = request.session
	user = None
	email = ''
	key = ''
	message = ''
	
	#Initialize rated movies
	try:
		session['rated_movies']
	except:
		session['rated_movies'] = []
	try:
		session['ratings']
	except:
		session['ratings'] = []
	#max_ratings = 0
	#survey_n_ratings = 0
	#Login in wizard and put user_login inside the session and the users list of the survey
	if 'form.key.submitted' in request.params:
		#Then the user must rate again anyway...
		session['rated_movies'] = []
		session['ratings'] = []
		email = request.params['key_email']
		key = request.params['key_password']
		user = User.objects.filter(email=email).first()
		#For now the key is simply the password:
		if user is not None:
			if user.survey_status == 'submitted':
				message = 'User has already submit this survey'
			if user.survey_status is None:
				if user.password == key:
#TESTAR SE ALGUEM TENTA "CORTAR SESSION"... DEVO ZERAR SESSION: ALERTA! DEPOIS O USER ANTES DEVE REFAZER
#TUDO...#DEVO APAGAR OQ FOI ADICIONADO NO SURVEY? SOH PEGAR ULTIMOS RESULTADOS...
					try:
						session['user']
						if session['user'] != user.email:
							session['concluded_until_step'] = None
							#session['rated_movies'] = []
							session['user'] = email
					except:	
						session['user'] = email
					#Use user in session to filter surveys and find the survey name, algorithm and ratings...
					user_object_list = []
					for item in Survey.objects.all():
						user_object_list = item.users
						for item_user in user_object_list:
							if item_user.email == session['user']:
								sur = Survey.objects.filter(name=item.name).first()
								if sur is not None:
									session['survey']=sur.name
									#Set the number of ratings
									session['max_ratings'] = (int(sur.number_of_ratings))
									session['ratings_executed'] = 0
									#Control until when the user finished the survey
									try:
										session['concluded_until_step']
									except:
										return HTTPFound(location = request.resource_url(request.root, 'Survey', '1'))
									if session ['concluded_until_step'] is not None:
										step_to_go = int(session['concluded_until_step'])+1
										return HTTPFound(location = request.resource_url(request.root, 'Survey', str(step_to_go)))							
									else:
										return HTTPFound(location = request.resource_url(request.root, 'Survey', '1'))
		if message == '':
			message = 'User not registered in any survey or invalid password'
	
	
	#Control if session['max_ratings'] has been defined already (after login) or not
	if request.view_name == 'wizard':
		survey_n_ratings = 0
	else:
		survey_n_ratings = session['max_ratings']
		#Determine the size of the list showed (to be changed...)
		#rated_movies = Movie.objects()[:session['max_ratings']]
		
	#numero di ratings as a query now
	
	if request.GET.get('rating') is not None:
		session['ratings_executed'] = session['ratings_executed'] + 1
		if session['ratings_executed'] == session['max_ratings']:		
			rating_finished=True
			session['concluded_until_step'] = request.view_name
		
		
	
	#Form submission Step 1
	
	if 'form.info.submitted.1' in request.params:
			session['concluded_until_step'] = request.view_name
			user = User.objects.filter(email=session['user']).first()
			age = SurveyAnswer(user = user, key='age', value=request.params['age'])
			gender = SurveyAnswer(user = user, key='gender', value=request.params['sex'])
			education = SurveyAnswer(user = user, key='education_lvl', value=request.params['edu'])
			nationality = SurveyAnswer(user = user, key='nationality', value=request.params['country'])
			avg_movies = SurveyAnswer(user = user, key='avg_movies', value=request.params['avg_movie'])
			sur = Survey.objects.filter(name=session['survey']).first()
			sur.answers.append(age)
			sur.answers.append(gender)
			sur.answers.append(education)
			sur.answers.append(nationality)
			sur.answers.append(avg_movies)
			sur.save()
			return HTTPFound(location=request.resource_url(request.root, 'Survey','2'))
	
	movie_title = request.GET.get('movie_title')
	rating = request.GET.get('rating')
	
	if movie_title is not None:
		#Here we would accept just if the movie hasnt been rated
		#if SurveyAnswer.objects.filter(key=movie_title).first() == None:
#the right is to eliminate the rated movies from the list!
			user = User.objects.filter(email=session['user']).first()
			movie_rated = SurveyAnswer(user = user, key=movie_title, value=rating)
			sur = Survey.objects.filter(name=session['survey']).first()
			sur.answers.append(movie_rated)
			session['ratings'].append(rating)
			sur.save()			
			
#APPEND THE RATED MOVIE TO THE RATED MOVIES LIST
			for item in Movie.objects.all():
					if item == Movie.objects.filter(title=movie_title).first():
						session['rated_movies'].append(item)
			#print 'List after: '+str(session['rated_movies'])
			
#Add RATING IN WHISPERER
#MAYBE THE PROBLEM IS THE SPACING IN movie_title...
			whisperer_url = url_fix('http://whisperer.vincenzo-ampolo.net/item/'+movie_title+'/addRating')
			data = urllib.urlencode({'useremail':session['user'], 'rating':rating})          
			req = urllib2.Request(whisperer_url, data)
#Testing if it works -> should print in the command line the new user email and ID or an error message, if the user already exists (shouldn't be the case...)
			#response = urllib2.urlopen(req)
			#whisperer_page = response.read() 
			#print whisperer_page
			#print whisperer_url
			#print data
			#print req
			#print response
	
	#Questions in step 3 and 4 might not be useful actually.... Should I take the answers?

	#Form submission step 3
	
	specific = ''
	missing = ''
	missing1 = ''
	missing2 = ''
	complete = ''
	if 'form.info.submitted.3' in request.params:
			session['concluded_until_step'] = request.view_name
			user = User.objects.filter(email=session['user']).first()
			specific = SurveyAnswer(user = user, key='specific', value=request.params['specific'])
			missing = SurveyAnswer(user = user, key='missing', value=request.params['missing'])
			missing1 = SurveyAnswer(user = user, key='missing1', value=request.params['missing1'])
			missing2 = SurveyAnswer(user = user, key='missing2', value=request.params['missing2'])
			missing3 = SurveyAnswer(user = user, key='missing3', value=request.params['missing3'])
			complete = SurveyAnswer(user = user, key='complete', value=request.params['complete'])
			sur = Survey.objects.filter(name=session['survey']).first()
			sur.answers.append(missing)
			sur.answers.append(missing1)
			sur.answers.append(missing2)
			sur.answers.append(missing3)
			sur.answers.append(complete)
			sur.save()
			return HTTPFound(location=request.resource_url(request.root, 'Survey','4'))
	
	#Form submission step 4 - I am not getting checklist information now because is actually "fake" questions... Should I?
	
	confuse = ''
	if 'form.info.submitted.4' in request.params:
			session['concluded_until_step'] = request.view_name
			user = User.objects.filter(email=session['user']).first()
			confuse = SurveyAnswer(user = user, key='confuse', value=request.params['confuse'])
			sur = Survey.objects.filter(name=session['survey']).first()
			sur.answers.append(confuse)
			sur.save()
			
#GENERATE THE RECOMMENDATION LIST
			#whisperer_url = url_fix('http://whisperer.vincenzo-ampolo.net/user/'+session['user']+'/getRec')
			#data = urllib.urlencode({'alg':sur.algorithm})
			#req = urllib2.Request(whisperer_url, data)
#Testing if it works -> should print in the command line the new user email and ID or an error message, if the user already exists (shouldn't be the case...)
			#response = urllib2.urlopen(req)
			#whisperer_page = response.read() 
			#print whisperer_page
			
			
			return HTTPFound(location=request.resource_url(request.root, 'Survey','5'))
	
	#Form submission step 5 - loop for all movie list retrieved...
	
	if 'form.info.submitted.5' in request.params:
			session['concluded_until_step'] = request.view_name
			user = User.objects.filter(email=session['user']).first()
			#confuse = SurveyAnswer(user = user, key='confuse', value=request.params['confuse'])
			#sur = Survey.objects.filter(name=session['survey']).first()
			#sur.answers.append(confuse)
			#sur.save()
			return HTTPFound(location=request.resource_url(request.root, 'Survey','finish'))
	
	#Final form submission
	
	if 'form.info.submitted.6' in request.params:
			user = User.objects.filter(email=session['user']).first()
			user.survey_status = 'submitted'
			place = SurveyAnswer(user = user, key='place', value=request.params['place'])
			reason = SurveyAnswer(user = user, key='reason', value=request.params['reason'])
			sur = Survey.objects.filter(name=session['survey']).first()
			sur.answers.append(place)
			sur.answers.append(reason)
			sur.save()
			user.save()
			#Where I will go when i click "continue"
			session['concluded_until_step'] = None
			session['user'] = None
			#Necessary?!
			#session['rated_movies'] = []
			#session['ratings'] = []
			return HTTPFound(location=request.resource_url(request.root, ''))
	
	#Create complete movie list
	main_movies = Movie.objects().order_by('-date')
	
	#The ratings done of ratings done
	ratings = session['ratings']
	
	#Deleting a movie from the list
	deleted_movie = request.GET.get('delete')
	deleted_movie_index = request.GET.get('index')
	if deleted_movie is not None and deleted_movie_index is not None:
		del session['ratings'][int(deleted_movie_index)]
		del ratings[int(deleted_movie_index)]		
		for movie in Movie.objects().order_by('-date'):
				if deleted_movie == movie.title:
					session['rated_movies'].remove(movie)
					session['ratings_executed'] = session['ratings_executed'] - 1
					rating_finished=False
					session['concluded_until_step'] = 1
	
	#Create the list of rated movies
	rated_movies = session['rated_movies']
	
	#Delete the rated movies from the main_list
	if rated_movies is not None:
			main_movies = []
			for movie in Movie.objects().order_by('-date'):
				if movie not in rated_movies:
					main_movies.append(movie)
	
	
	#Filters in step 2
	
	#Title filter
	first_letter = request.GET.get('title')
	if first_letter is not None:
			main_movies = []
			for movie in Movie.objects().order_by('-date'):
				first_char = movie.title[0]
				if first_letter == first_char:
					if rated_movies is not None:
						if movie not in rated_movies:
							main_movies.append(movie)
					else:
						main_movies.append(movie)
	#Genre filter
	genre = request.GET.get('genre')
	if genre is not None:
			#films_not_filtered = False
			main_movies = []
			for movie in Movie.objects().order_by('-date'):
				list_genre = movie.genre
				if genre in list_genre[:]:
					if rated_movies is not None:
						if movie not in rated_movies:
							main_movies.append(movie)
					else:
						main_movies.append(movie)
	
	#Date filter
	date = request.GET.get('date')
	if date is not None:
			#films_not_filtered = False
			main_movies = []
			if int(date) is not 90: 
				if int(date) is not 80:
					for movie in Movie.objects().order_by('-date'):
						if movie.date.year == int(date):
							if rated_movies is not None:
								if movie not in rated_movies:
									main_movies.append(movie)
							else:
								main_movies.append(movie)
			if int(date) is 90:
				years = [1999,1998,1997,1996,1995,1994,1993,1992,1991,1990]
				for movie in Movie.objects.all():
					if movie.date.year in years[:]:
						if rated_movies is not None:
							if movie not in rated_movies:
								main_movies.append(movie)
						else:
							main_movies.append(movie)
			if int(date) is 80:
				years = [1989,1988,1987,1986,1985,1984,1983,1982,1981,1980]
				for movie in Movie.objects.all():
					if movie.date.year in years[:]:
						if rated_movies is not None:
							if movie not in rated_movies:
								main_movies.append(movie)
						else:
							main_movies.append(movie)
	
	#Query Filter
	search_query = request.GET.get('search_query')
	#Search inside title, description, genre
	#in the future also for the actor...
	if search_query is not None:
			capitalized_query = search_query.capitalize()
			#films_not_filtered = False
			main_movies = []
			for movie in Movie.objects().order_by('-date'):
				list_title_strings = movie.title.split()
				list_description_strings = movie.description.split()
				list_strings_movie = []
				for item in list_title_strings:
					list_strings_movie.append(item)
				for item in list_description_strings:
					list_strings_movie.append(item)
				for item in movie.genre:
					list_strings_movie.append(item)
				if search_query in list_strings_movie:
					if rated_movies is not None:
						if movie not in rated_movies:
							main_movies.append(movie)
					else:
						main_movies.append(movie)
				elif capitalized_query in list_strings_movie:
					if rated_movies is not None:
						if movie not in rated_movies:
							main_movies.append(movie)
					else:
						main_movies.append(movie)
	
	#Testing Next/Previous buttons
	page = request.GET.get('page')
	if page is None:
		page = 1
	else:
		page = int(page)
	
	#compute and show pages
	last_page = True if len(main_movies) <= (page-1)*9+9 else False
	movies = dict(movies=main_movies[(page-1)*9:(page-1)*9+9])
	
	return dict(ratings = ratings,survey_n_ratings=survey_n_ratings,message = message, rated_movies = rated_movies, rating_finished = rating_finished, movies=movies, page=page, last_page=last_page)
