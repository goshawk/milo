from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from resources import *
from datetime import datetime
from pyramid.security import authenticated_userid
import random

@view_config(context='milo_app:resources.Root',
             renderer='templates/base.pt')
@view_config(name='Latest', context='milo_app:resources.Root',
             renderer='templates/movie_list.pt')
@view_config(name='Recommended', context='milo_app:resources.Root',
             renderer='templates/movie_list.pt')
@view_config(name='Popular', context='milo_app:resources.Root',
             renderer='templates/movie_list.pt')                                       
def main(request):
	rand = random.randint(0, Movie.objects().count()-10)
	new_rec = None
	rating_finished = None
	slider_movies = None
	right_movies = dict(movies=Movie.objects()[rand+5:rand+10], title="More Top Movies")
	wizard_movie = False
	session = request.session
	
	if request.GET.get('wizard_movie') == 'details':
		wizard_movie == True
        	
	#Testing Next/Previous buttons
	page = request.GET.get('page')
	if page is None:
		page = 1
	else:
		page = int(page)
	
	
	num_ratings = request.GET.get('num_ratings')
	
	if num_ratings is None:
		num_ratings = 1
	else:
		num_ratings = int(num_ratings)
		rating_finished=False
		
	if num_ratings == 6:
		rating_finished=True
	
	if request.GET.get('rec') == 'new':
		main_movies = Movie.objects().order_by('-date')
		slider_movies = main_movies[:5]
		category = 'Recommended Movies'	
		new_rec=True		
		
	elif not authenticated_userid(request):
		main_movies = Movie.objects().order_by('-date')
		category = 'All Movies'
	else:
		main_movies = Movie.objects().order_by('date')
		slider_movies = main_movies[:5]
		category = 'Recommended Movies'
		right_movies['title']="More Recommendations"
	
	main_movies_title = 'Last updates'
	#compute and show pages
	last_page = True if len(main_movies) <= (page-1)*9+9 else False
	movies = dict(movies=main_movies[(page-1)*9:(page-1)*9+9], title=main_movies_title)
	rated_movies = Movie.objects()[:num_ratings]
	# the upper two lines are magic
	slider_movies = slider_movies if slider_movies else Movie.objects()[rand:rand+5]
	return dict(rated_movies = rated_movies, wizard_movie = wizard_movie, num_ratings = num_ratings, rating_finished=rating_finished, movies=movies, slider_movies=slider_movies, right_movies=right_movies, category=category, page=page, last_page=last_page, new_rec=new_rec)

@view_config(name='about', context='milo_app:resources.Root',
				 renderer='templates/about.pt')
def about(request):
	return dict()


@view_config(name='categories', context='milo_app:resources.Root',
				 renderer='templates/categories.pt')
def categories(request):
	return dict()

@view_config(name='profile', context='milo_app:resources.Root',
				 renderer='templates/profile.pt')
def profile(request):
	return dict()

@view_config(name='add_algorithm', context='milo_app:resources.Root',
				 renderer='templates/add_algorithm.pt')
@view_config(name='add_survey', context='milo_app:resources.Root',
				 renderer='templates/add_survey.pt')
@view_config(name='admin', context='milo_app:resources.Root',
				 renderer='templates/admin.pt')
def admin(request):
	return dict()

@view_config(context='milo_app:resources.Movie',
				 renderer='templates/movie.pt')
def movie(context, request):
	
	if context.__parent__.__name__ == 'wizard_movie':
		request.override_renderer = 'templates/wizard_movie.pt'
	rand = random.randint(0, Movie.objects().count()-5)
	slider_movies = dict(movies=Movie.objects()[rand:rand+3], title='Related Movies')
	right_movies = dict(movies=Movie.objects()[rand+5:rand+10], title='Recommended by Friends')
	
	return dict(movie=context, slider_movies=slider_movies, right_movies=right_movies)

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
	session['step'] = request.view_name
	
	email = ''
	#Login in wizard session -> for now im just testing with the registered user 'test', and will be also stored in the session
	if 'form.key.submitted' in request.params:
		email = request.params['key_email']
		key = request.params['key_password']
		user = User.objects.filter(email=email).first()
		if user is not None and user.password == key:
			survey = Survey(email=email)
			survey.save()
			session['user'] = email
			return HTTPFound(location = request.resource_url(request.root, 'Survey','1'))
	
	#Testing Next/Previous buttons
	page = request.GET.get('page')
	if page is None:
		page = 1
	else:
		page = int(page)
	
	#Set the number of ratings
	max_ratings = 6	
	#numero di ratings as a query now
	num_ratings = request.GET.get('num_ratings')
	if num_ratings is None:
		num_ratings = 1
	else:
		num_ratings = int(num_ratings)
		rating_finished=False
	
	if num_ratings == max_ratings:
		rating_finished=True
		
	#Get objects of DB to retrieve the movie catalogue
	main_movies = Movie.objects().order_by('-date')
	
	#compute and show pages
	last_page = True if len(main_movies) <= (page-1)*9+9 else False
	movies = dict(movies=main_movies[(page-1)*9:(page-1)*9+9])
	#Show the list of rated movies in step 2
	rated_movies = Movie.objects()[:num_ratings]
	
	survey_user = Survey.objects.filter(email=session['user']).first()
	
	#Initialize the Step 1 inputs
	#Form submission step 1
	
	if 'form.info.submitted.1' in request.params:
			age = request.params['age']
			gender = request.params['sex']
			nationality = request.params['country']
			avg_movies = request.params['avg_movie']
			survey_user.age = age
			survey_user.gender = gender
			survey_user.nationality = nationality
			survey_user.avg_movies = avg_movies
			survey_user.save()
			return HTTPFound(location=request.resource_url(request.root, 'Survey','2'))
			
	return dict(rated_movies = rated_movies, num_ratings = num_ratings,rating_finished = rating_finished, movies=movies, page=page, last_page=last_page)
