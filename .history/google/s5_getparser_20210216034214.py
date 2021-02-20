import shutil
from fonduer.parser.preprocessors import html_doc_preprocessor
from sqlalchemy import exc
import pdftotree

import re
from sen_parser_usable import *
from config import config

import json

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO
import json
import uuid
import sys
import logging
import errno
from os import walk

from fonduer.parser.models import Document, Sentence, Table
from fonduer.parser.preprocessors import HTMLDocPreprocessor
from fonduer.parser import Parser
from pprint import pprint

from fonduer import Meta, init_logging

from fonduer.candidates import CandidateExtractor
from fonduer.candidates import MentionNgrams
from fonduer.candidates import MentionExtractor 

from fonduer.candidates.models import Mention
from fonduer.candidates.models import mention_subclass
from fonduer.candidates.models import candidate_subclass

from fonduer.candidates.matchers import RegexMatchSpan, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union

from fonduer.features import Featurizer

import inspect

import matchers as matchers

from extract_html import *

PII_KEYLIST = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/model/pii-keylist.json'
PARALLEL = 4  # assuming a quad-core machine
#     ATTRIBUTE = "ns8s_invoice_poc_stage"
# check that the databases mentioned below already exist
getdbref = __import__('s1_2_getdbref') 
# Will return <module '1_2_getdbref' from '/home/dsie/Developer/sandbox/3ray/server/backend/python/kbc_process/1_2_getdbref.py'>

# pdf_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf/'
# docs_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/html/'
# pdf_path = json.loads(sys.argv[1])['pdf_path'] 
# docs_path = json.loads(sys.argv[1])['html_path']
# job_id = json.loads(sys.argv[1])['job_id']

# exc_context = 'email_id'
# doc_context = 'mock'
# exc_context = json.loads(sys.argv[1])['context'] if len(sys.argv) > 0 and json.loads(sys.argv[1])['context'] is not None else None
# doc_context = json.loads(sys.argv[1])['doc_name'] if len(sys.argv) > 0 and json.loads(sys.argv[1])['doc_name'] is not None else None
# exc_context = 'phone_number'

pdf_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/drive_documents/efca2facee5f8df9/pdf/'
docs_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/drive_documents/efca2facee5f8df9/html/'
job_id = 'efca2facee5f8df9'
exc_context = None
doc_context = None



# Configure logging for Fonduer
init_logging(log_dir="logs", level=logging.ERROR)

max_docs = 1000
PARALLEL = 4
doc_preprocessor = None
execution_stack = ["1. Get session object..."]


try:
    session = getdbref.get_session()
    sessType = type(session) # Will return <class 'sqlalchemy.orm.session.Session'>
    execution_stack.append("Done.")
    execution_stack.append("2. Processing layout...")
except Exception as session_exception:
    logging.error(f'{execution_stack}, session = getdbref.get_session(), {session_exception}')
except exc.SQLAlchemyError as sql_exception:
    logging.error(f'{execution_stack}, session = getdbref.get_session(), {sql_exception}')

def do_prepare_mentions_batch(candidate_mentions, config):
    # for index, data in enumerate(config):
    for index, data in config.items():
        mention_subclass_list = list()
        max_ngrams = None
        for key in data.keys():
            if key == 'Candidates':
                for c in data.get(key):
                    if c not in candidate_mentions.keys(): #TODO verify this condition
                         candidate_mentions[c] = {
                             "mention_names": [],
                             "mention_ngrams": [],
                             "mention_matchers": [],
                             "mention_subclass": [],
                             "max_ngrams": [],
                             "throttler_function": []
                         }
                    candidate_mentions[c]['mention_names'].append(data['MentionName'])
                    candidate_mentions[c]['mention_ngrams'].append(data['MentionNGrams'])
                    candidate_mentions[c]['mention_matchers'].append(matchers.matcher[data.get('Context')])
                    if 'mention_subclass' in candidate_mentions[c].keys():
                        candidate_mentions[c]['mention_subclass'].append(mention_subclass(data['MentionName']))              
                    else:
                        candidate_mentions[c]['mention_subclass'] = [mention_subclass(data['MentionName'])]
                    
                    if 'max_ngrams' in candidate_mentions[c].keys():
                        candidate_mentions[c]['max_ngrams'].append(MentionNgrams(n_max=candidate_mentions[c].get('mention_ngrams')))
                    else:   
                        candidate_mentions[c]['max_ngrams'] = [MentionNgrams(n_max=candidate_mentions[c].get('mention_ngrams'))]
                    # candidate_mentions[c]['throttler_function'] = data.get('ThrottlerFunctions')[0].get('tf')
                    candidate_mentions[c]['throttler_function'] = [{data.get('ThrottlerFunctions')[0].get('tf')}]
    return candidate_mentions

def do_prepare_mentions(candidate_mentions, config, context):
    mention_subclass_list = list()
    max_ngrams = None
    ctx = {
            "mention_names": [],
            "mention_ngrams": [],
            "mention_matchers": [],
            "mention_subclass": [],
            "max_ngrams": [],
            "throttler_function": None
        }
    ctx['mention_names'].append(config[context].get('MentionName'))
    ctx['mention_ngrams'].append(config[context]['MentionNGrams'])
    ctx['mention_matchers'].append(matchers.matcher[config[context].get('Context')])
    ctx['mention_subclass'].append(mention_subclass(config[context]['MentionName']))               
    ctx['max_ngrams'].append(MentionNgrams(n_max=config[context].get('MaxNGrams')))
    ctx['throttler_function'] = config[context].get('ThrottlerFunctions')[0].get('tf')
    candidate_mentions[context] = ctx

    return candidate_mentions

def do_train(candidate_mentions):
    from sqlalchemy import desc 
    docs = session.query(Document).order_by(Document.name).all()
    # docs = session.query(Document).order_by(desc(Document.id)).limit(1)
    total_mentions = session.query(Mention).count()

    splits = (1, 0.0, 0.0)
    train_cands = []
    for candidate_key in candidate_mentions.keys():
        train_docs = set()
        dev_docs   = set()
        test_docs  = set()
        '''print('Mention Subclass {}, Ngrams {} and Matchers {}'
                .format(candidate_mentions[candidate_key]['mention_subclass'], 
                        candidate_mentions[candidate_key]['max_ngrams'], 
                        candidate_mentions[candidate_key]['mention_matchers']))
        '''
        mention_extractor = MentionExtractor(session, candidate_mentions[candidate_key]['mention_subclass'], candidate_mentions[candidate_key]['max_ngrams'], candidate_mentions[candidate_key]['mention_matchers'])
        mention_extractor.apply(docs, clear=False, parallelism=PARALLEL, progress_bar=False)

        candidate_mentions[candidate_key]['candidate_subclass'] = candidate_subclass(candidate_key, candidate_mentions[candidate_key].get('mention_subclass'), table_name=candidate_mentions[candidate_key]['mention_names'][0])
        
        candidate_extractor = CandidateExtractor(session, [candidate_mentions[candidate_key]['candidate_subclass']], throttlers=[candidate_mentions[candidate_key]['throttler_function']])
        
        data = [(doc.name, doc) for doc in docs]
        data.sort(key=lambda x: x[0])
        for i, (doc_name, doc) in enumerate(data):
            train_docs.add(doc)
        for i, docs in enumerate([train_docs, dev_docs, test_docs]):
            candidate_extractor.apply(docs, split=i, parallelism=PARALLEL)
        #         train_cands = candidate_extractor.get_candidates(split = 0)
        #         train_cands.append(candidate_extractor.get_candidates(split = 0))
        candidate_mentions[candidate_key]['train_cands'] = candidate_extractor.get_candidates(split = 0)
        for index, item in enumerate(candidate_mentions[candidate_key]['train_cands']):
            if len(item) > 0:
                
                featurizer = Featurizer(session, [candidate_mentions[candidate_key]['candidate_subclass']])
                featurizer.apply(split=0, train=True, parallelism=PARALLEL)
                # %time featurizer.apply(split=0, train=True, parallelism=PARALLEL)
                # %time F_train = featurizer.get_feature_matrices(candidate_mentions[candidate_key]['train_cands'])
            else: 
                candidate_mentions[candidate_key]['train_cands'].pop(index)
        #         candidate[candidate_key]['train_cands'] = train_cands
    return candidate_mentions

def do_process_get_candidates(candidate_mentions=None):
    train_cands = do_train(candidate_mentions)
    return train_cands

def handle_return(generator, func):
    contextInfoDict = yield from generator
    func(contextInfoDict)

def get_context_async(sm, document_context='', search_context=''):
    pass
    # star_char_index = sm.char_start
    # end_char_index = sm.char_end

    # star_char_index = sm['applicant_name_context'].char_start
    # end_char_index = sm['applicant_name_context'].char_end
    # contextInfoDictionary = {
    #     'label': {
    #     #     'spanMention': sm['applicant_name_context'],
    #         'document': sm[search_context].sentence.document.name,
    #         'documentId': sm[search_context].sentence.document.id,
    #         'sentence': sm[search_context].sentence.text,
    #         'contextValue': sm[search_context].sentence.text[star_char_index:end_char_index+1],
    #         'startChar': star_char_index,
    #         'endChar': end_char_index
    #     },
    #     'value': {
    #     #     'spanMention': sm['applicant_name_context'],
    #         'document': sm[search_context].sentence.document.name,
    #         'documentId': sm[search_context].sentence.document.id,
    #         'sentence': sm[search_context].sentence.text,
    #         'contextValue': sm[search_context].sentence.text[star_char_index:end_char_index+1],
    #         'startChar': star_char_index,
    #         'endChar': end_char_index
    #     }
    # }
    # yield contextInfoDictionary

def print_values(value):
    print('returned: {}'.format(json.dumps(value)))

def do_get_docs_values(candidates=None, document_context=None, search_context=None):
    '''
        "<class 'fonduer.parser.models.document.Document'>"
        "<class 'fonduer.parser.models.section.Section'>"
        "<class 'fonduer.parser.models.sentence.Sentence'>"
        "<class 'fonduer.candidates.models.span_mention.SpanMention'>"
        "<class 'fonduer.candidates.models.mention.ApplicationNameLabel'>"
    '''
    train_cands = None
    docs_and_values = []
    all_docs_and_values = []

    search_types = ['all_docs_and_pii', 'all_doc_and_'+search_context, 'all_pii_for_'+document_context, search_context+'_for_'+document_context]

    search_type = ''
    if document_context == None and search_context == None:
        '''Entire KB'''
        search_type = search_types[0]
    elif document_context == None and search_context is not None:
        ''' Send entire KB '''
        search_type = search_types[1]
    elif document_context is not None and search_context == None: 
        ''' Send KB for document'''
        search_type = search_types[2]
    else:
        ''' Send KB for match in Doc'''
        search_type = search_types[3]
    
    for index, item in enumerate(candidates):
        train_cands = candidates.get(item).get('train_cands')
    if train_cands is not None:
        for instances in train_cands:
            for candidate in instances:
                for key, value in enumerate(candidate):
                    all_docs_and_values.append({
                        "documentName": value.context.sentence.document.name,
                        "page": value.context.sentence.page,
                        "piiFound": value.context.sentence.text
                    })

    for item in all_docs_and_values:
        if search_type == 0:
            docs_and_values.append(item)
        elif search_type == 1:
            '''
            search_context is already filtered, hence do not filter any document
            '''
            docs_and_values.append(item)
        elif search_type == 2:
            '''
            only filter document name
            '''
            docs_and_values.append(item) if item.get("documentName") in document_context else None
        else: 
            '''
            search_type is 3
            search_context is already filtered, hence only filter document_name
            '''
            docs_and_values.append(item) if item.get("documentName") in document_context else None

    # logging.info(f'docs_and_values: {docs_and_values}')
    return docs_and_values

def train_and_test_experiment(document_context=None, context_label='', user=0, pdf_path=''):
    '''
    context_value:
    context_label:
    user:
    pdf_path:
    '''
    candidate_mentions = do_prepare_mentions({}, config, context_label)
    candidates = do_process_get_candidates(candidate_mentions)
    results = []
    if candidates is not None:
        span_mention = None
        span_mention_list = do_get_docs_values(candidates, document_context, context_label)
        if len(span_mention_list) > 0:
            span_mention = span_mention_list[0]
            returned_contexts = handle_return(get_context_async(span_mention, document_context, context_label), print_values)
            for x in returned_contexts:
                results.append(x)
        else:
            # TODO
            pass
    return results   

def train_and_test(document_context=None, context_label='', user=0, pdf_path=''):
    '''
    context_value:
    context_label:
    user:
    pdf_path:
    '''
    # candidate_mentions = do_prepare_mentions({}, config, context_label)
    candidate_mentions = do_prepare_mentions_batch({}, config)
    candidates = do_process_get_candidates(candidate_mentions)
    results = []
    if candidates is not None:
        results = do_get_docs_values(candidates, document_context, context_label)
    return results

_, _, filenames = next(walk(pdf_path))
exc_context_list = config.keys()

for fn in filenames:
    for ec in exc_context_list:
        print(filenames, exc_context_list)
# print(json.dumps({"result": train_and_test(document_context=doc_context, context_label=exc_context), "job_id": job_id }))