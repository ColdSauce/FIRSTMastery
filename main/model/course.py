# coding: utf-8

from __future__ import absolute_import

import hashlib
import random

from google.appengine.ext import ndb

from api import fields
import model
import util
import config


class Course(model.Base):
  name = ndb.StringProperty(required=True)
  lessons = ndb.KeyProperty(kind='Lesson', repeated=True)
  topics = ndb.KeyProperty(kind='Topic', repeated=True)
  contributors = ndb.KeyProperty(kind='User', repeated=True)
  approved = ndb.BooleanProperty(default=False)
  color = ndb.StringProperty()

  #Generate Color if non already
  def _pre_put_hook(self):
  	if not self.color:
  		r = lambda: random.randint(0,255)
  		self.color = ('#%02X%02X%02X' % (r(),r(),r()))