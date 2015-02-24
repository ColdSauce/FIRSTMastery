# coding: utf-8

from flask.ext import wtf
import flask
import wtforms

import auth
import config
import model
import util
import task
import urlparse
##import cgi

##import gdata.service
##import gdata.youtube
##import gdata.youtube.service
##import gdata.media
##import gdata.geo
##import gdata.alt.appengine

from main import app


###############################################################################
# Lesson View
###############################################################################
@app.route('/lesson/<lesson_id>/v/<version_id>')
@app.route('/lesson/<lesson_id>')
@app.route('/course/<course_id>/l/<lesson_id>')
def lesson(lesson_id, version_id, course_id):

  #set default lesson version key to the retrieved lesson's key
  #if there is a version key then set the lesson version key to it
  if version_id:
    lesson_version_id = version_id
  #Set a condition to verify there is a course. 
  #In order to activate the next and previous lesson button in the view

  return flask.render_template(
      'lesson/lesson.html',
      title=lesson['name'],
      html_class='lesson-view',
      lesson_version_id=lesson_version_id,
      lesson=lesson,
    )


@app.route('/lesson_version/<version_id>')
def render_lesson_version(version_id):  
  return flask.render_template(
      'lesson/lesson_version.html',
      title='',
      html_class='lesson_version',
    )


###############################################################################
# New Lesson
###############################################################################
class NewLessonForm(wtf.Form):
  name = wtforms.StringField(
      'Name',
      [wtforms.validators.required()], filters=[util.strip_filter],
    )
  topics = wtforms.StringField(
      'Topics', [wtforms.validators.Length(min=2, max=25)],
    )
  description = wtforms.TextField(
      'Description', [wtforms.validators.Length(min=2, max=25)]
    )
  ##video_thumnail = wtforms.FileField('Video Thumbnail Image')
  ##video_file = wtforms.FileField('Video File')
  video_url = wtforms.StringField('Video Link')


@app.route('/new-lesson/', methods=['GET','POST'])
@auth.login_required
def new_lesson():
  lesson = model.Lesson(contributors = [auth.current_user_key()])
  vote = model.Vote()
  form = NewLessonForm()
  print flask.request.data
  if flask.request.method == 'POST':
    vote = vote.put()
    lesson = lesson.put()
    topics = []
    for topic in form.topics.data.split(","):
      t = model.Topic(name=topic.strip().capitalize())
      t = t.put()
      topics.append(t)

    lesson_version = model.LessonVersion(data= reform_data_scheme(form.video_url.data),
                   name=form.name.data,
                   description=form.description.data,
                   topics = topics,
                   vote = vote,
                   contributor = auth.current_user_key(),
                   lesson = lesson,
                   )
    lesson_version = lesson_version.put()
    if lesson_version:
      lesson = lesson.get()
      lesson.lesson_versions.append(lesson_version)
      lesson.put()
      return flask.jsonify(lesson_id = lesson_version.id())
    else:
      vote.delete()
      lesson.delete()
      for topic in topics:
          topic.delete()
      return flask.jsonify(error = 'The Lesson was not created because of some errors.')

  return flask.render_template(
      'lesson/new_lesson.html',
      title='New Lesson',
      form=form,
      html_class='lesson',
      requestt=flask.request.method,
    )

@app.route('/propose_update/lesson/<lesson_id>', methods=['GET','POST'])
@auth.login_required
def new_lesson_version(lesson_id):
  user_db = auth.current_user_db()
  lesson_version = LessonVersion()

  form = NewLessonForm(obj=lesson_version)

  return flask.render_template(
      'lesson/new_lesson.html',
      title='Lesson Proposal',
      form=form,
      html_class='lesson-version',
    )
##No Longer Doing Video Uploads for the time being because of this article
## http://apiblog.youtube.com/2012/02/video-uploads-from-your-sites-community.html
## Considering implementing AuthSub to allow users to upload their own account instead.
##@app.route('/video_meta_check/', methods=['POST'])
##@auth.login_required
##def process_video_meta():
##  client = gdata.youtube.service.YouTubeService()
##  gdata.alt.appengine.run_on_appengine(client)
##
##  video_title = cgi.escape(flask.request.args.get('video_title'))
##  video_description = cgi.escape(flask.request.args.get('video_description'))
##  video_category = cgi.escape(flask.request.args.get('video_category'))
##  video_tags = cgi.escape(flask.request.args.get('video_tags'))
##  my_media_group = gdata.media.Group(
##        title = gdata.media.Title(text=video_title),
##        description = gdata.media.Description(description_type='plain',
##                                            text=video_description),
##        keywords = gdata.media.Keywords(text=video_tags),
##        category = gdata.media.Category(
##          text=video_category,
##          scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
##          label=video_category),
##      player=None
##      )
##  video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
##  
##  try:
##      server_response = client.GetFormUploadToken(video_entry)
##  except gdata.service.RequestError, request_error:
##    return
##
##  post_url = server_response[[]0]
##  youtube_token = server_response[[]1]
##
##  return flask.render_template(
##      'lesson/lesson.html',
##      title=lesson['name'],
##      html_class='lesson-version-view',
##      lesson=lesson,
##    )


###############################################################################
# Lesson Creation Helpers
###############################################################################
## Data scheme for LessonVersion Data
DATASCHEME = { 'fields': ['service_type'],
                'service_type':'',
              }
def reform_data_scheme(video_link):
    url_data = urlparse.urlparse(video_link)
    if url_data.netloc == 'www.youtube.com':
      query = urlparse.parse_qs(url_data.query)
      DATASCHEME['video_id'] = query["v"][0]
      DATASCHEME['fields'].append('video_id')
      DATASCHEME['service_type'] = 'youtube'
    if url_data.netloc == 'www.vimeo.com':
      DATASCHEME['video_id'] = url_data.path.lstrip("/")
      DATASCHEME['fields'].append('video_id')
      DATASCHEME['service_type'] = ('vimeo')
    return DATASCHEME