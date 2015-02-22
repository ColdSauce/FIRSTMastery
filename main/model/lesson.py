# coding: utf-8

from __future__ import absolute_import

import hashlib

from google.appengine.ext import ndb

from api import fields
import model
import util
import config

class Lesson(model.Base):
  name = ndb.StringProperty(required=True)
  latest_version = ndb.KeyProperty(kind='LessonVersion')
  versions = ndb.KeyProperty(kind='LessonVersion', repeated=True)
  topics = ndb.KeyProperty(kind='Topic', repeated=True)
  contributors = ndb.KeyProperty(repeated=True)
