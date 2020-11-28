import os
import sys
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from .. import config

Base = declarative_base()
session = None

#########
# Models
#
class StickerSet(Base):
	__tablename__ = 'StickerSet'
	id = Column(Integer, primary_key=True)
	sticker = Column(UnicodeText)

	def __init__(self, id, sticker):
		self.id = id
		self.sticker = str(sticker)

	def __repr__(self):
		return f"<Sticker {self.id}>"

class AnimatedStickerSet(Base):
	__tablename__ = 'AnimatedStickerSet'
	id = Column(Integer, primary_key=True)
	sticker = Column(UnicodeText)

	def __init__(self, id, sticker):
		self.id = id
		self.sticker = str(sticker)

	def __repr__(self):
		return f"<Sticker {self.id}>"

# For PM Permit
# class AuthorizedUsers(Base):
# 	__tablename__ = 'AuthorizedUsers'
# 	id = Column(Integer, primary_key=True)

# For future use to ban users that forward from
# known spam channels in certain chats.
# class BannedForwards(Base):
# 	__tablename__ = 'BannedForwards'
# 	id = Column(Integer, primary_key=True)

# we're british I guess
def innit():
	global session
	# Initialize SQL
	sqlengine = create_engine(config['sql']['uri'])
	Base.metadata.bind = sqlengine
	# Create the tables if they don't already exist
	try:
		Base.metadata.create_all(sqlengine)
	except exc.OperationalError:
		return False

	session = scoped_session(sessionmaker(bind=sqlengine, autoflush=False))
	# Init the tables
	StickerSet.__table__.create(checkfirst=True)
	AnimatedStickerSet.__table__.create(checkfirst=True)
	return True

def get_sticker_set(user_id):
	pass

def get_animated_set(user_id):
	pass

def set_sticker_set(user_id, text):
	pass

def set_animated_set(user_id, text):
	pass

