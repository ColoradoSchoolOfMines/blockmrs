"""Symptom controller module"""

from tg import expose, request, abort, redirect, predicates
from xml.etree import ElementTree as ET
import uuid

from blockmrs.lib.base import BaseController
from blockmrs.model import DBSession, User, PrivateKey
from blockmrs.lib.renderpr import match_field
from blockmrs.lib.records import retrieve_record, store_record


__all__ = ['SymptomController']


class SymptomController(BaseController):
    allow_only = predicates.not_anonymous()

    @expose('blockmrs.templates.symptoms')
    def index(self):
        return dict()

    @expose('blockmrs.templates.diagnosis')
    def diagnosis(self):
        print('ohea')
        return dict()
