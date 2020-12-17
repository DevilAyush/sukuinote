import logging
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, UnicodeText, Boolean
from sqlalchemy import ext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from . import Base

# For PM Permit
class AuthorizedUsers(Base):
	__tablename__ = 'AuthorizedUsers'
	# The user id
	id = Column(Integer, primary_key=True)
	# If they're approved
	approved = Column(Boolean)
	# If they've been warned already
	warned = Column(Boolean)
	# Whether they requested my attention
	requested = Column(Boolean)
	# The spam score they have
	retardlevel = Column(Integer)

	def __init__(self, id, approved, warned, requested):
		self.id = id
		self.approved = approved
		self.warned = warned
		self.requested = requested
		self.retardlevel = 0
	
	def __repr__(self):
		return f"<AuthorizedUsers id={self.id} warned={self.warned} approved={self.approved} retardlevel={self.retardlevel}>"


def get_authorized(user_id):
	from . import session
	try:
		return session.query(AuthorizedUsers).get(user_id)
	except:
		logging.exception("Failure in get_authorized")
		session.rollback()
		return None
