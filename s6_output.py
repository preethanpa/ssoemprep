from fonduer.parser.preprocessors import html_doc_preprocessor
from sqlalchemy import exc

from .sen_parser_usable import *
from .config import *

import json

import urllib.request, urllib.parse, urllib.error
import shutil
import re
from io import BytesIO
import json
import uuid
import sys
import logging
import errno

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

from .extract_html import *

# Configure logging for Fonduer
init_logging(log_dir="logs")

PII_KEYLIST = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/model/pii-keylist.json'
PARALLEL = 4  # assuming a quad-core machine
#     ATTRIBUTE = "ns8s_invoice_poc_stage"
# check that the databases mentioned below already exist
getdbref = __import__('s1_2_getdbref') 
# Will return <module '1_2_getdbref' from '/home/dsie/Developer/sandbox/3ray/server/backend/python/kbc_process/1_2_getdbref.py'>

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
    logging.error(f'(get_document_ngrams_api) : Got error fetching document from DB {session_exception}')
except exc.SQLAlchemyError as sql_exception:
    logging.error(f'{execution_stack}, session = getdbref.get_session(), {sql_exception}')

def get_document_ngrams_api(document='', user=0, pdf_path=''):
    doc_name = os.path.splitext(document)[0]
    documents = []
    resultObject = {}
    try:
        documents = session.query(Document).filter(Document.name == doc_name).all()
    except exc.SQLAlchemyError:
        logging.error(f'(get_document_ngrams_api) : Got error fetching document from DB {exc.SQLAlchemyError}')

    if len(documents) > 0:
        resultObject = format_output_structure(documents, doc_name)
    else:
        pass
    return resultObject

## Templated output functions - next stage of the application
#
#
def format_output_structure(documents=None, document=None):
    nop = lambda *a, **k: None
    resultObject = {}
    '''
     for each document
    '''
    
    object = {
        'document_name': document,
        'sentences': [],
        'tables': [],
        'sections': [],
        'labels': []
    }

    if documents and len(documents) > 0:
        sentence_count = session.query(Sentence).filter(Sentence.document_id == documents[0].id).count()
        resultObject['summary'] = { 'document_name': documents[0].name, 'total_sentences': sentence_count }

        sentences = session.query(Sentence).filter(Sentence.document_id == documents[0].id).all()       
        current = ''
        previous = 'nothing'
        previous_table_position = 0
        previous_row_start_position = 0
        previous_col_start_position = 0
        previous_row_mapped_category = ''
        previous_row_mapped_label = ''

        previous_table_id = -1
        current_table_id = -1
        
        current_object = {}
        cache = {}

        previous_id = -1
        pii_keys = {}
        
        with open(PII_KEYLIST) as json_file:
            pii_keys = json.load(json_file)
                
        for sentence in sentences:
            sd = sentence.__dict__
            #logging.info(f'(format_output_structure) : Sentence found = {sd}')

            current = 'table' if sd['table_id'] != None else 'section'
            current_table_id = sd['table_id']
            current_section_id = sd['section_id']
            sd['mapped_kv'] = [{'matched_label': '', 'matched_value': ''}]
            sd['mapped_label'] = ''
            sd['mapped_category'] = ''

            if current == 'table':
                if current_table_id != previous_table_id:
                    cache = {sd['row_start']: {sd['col_start']: { 'mapped_category': None, 'mapped_label': None}}}
                else:
                    if cache[previous_row_start_position] is not None:
                        if cache[previous_row_start_position][sd['col_start']] is not None: 
                            if cache[previous_row_start_position][sd['col_start']]['mapped_category'] is not None:
                                sd['mapped_category'] = cache[previous_row_start_position][sd['col_start']]['mapped_category']
                            else:
                                sd['mapped_category'] = ''
                            if cache[previous_row_start_position][sd['col_start']]['mapped_label'] is not None:
                                sd['mapped_label'] = cache[previous_row_start_position][sd['col_start']]['mapped_label']
                            else:
                                sd['mapped_label'] = ''
            else:
                cache = {sd['row_start']: {sd['col_start']: { 'mapped_category': None, 'mapped_label': None}}}


            sd['text'] = sd.get('text').replace('&amp;', '&').replace('\u2019', '\'').replace(':-', ' ').replace(':', ' ').replace('\\n', '').replace(' \n', ' ').replace('\n', ' ').replace('\n\n\n', ' ').replace('(', '').replace(')', '').replace('\n', ' ')
            # sd.update({'text': sd_text})
            saved_text = sd.get('text')
            prepared_text = sd.get('text').lower()
            logging.debug(f'(format_output_structure) : Prepared text = {prepared_text}')

            for key_category, val_category in pii_keys.items():
                for key_label, val_label in val_category.items():
                    if len(sd['mapped_label']) > 0:
                        break  
                    keys = val_label.get('keys')
                    tokens_matched = find_tokens(keys, prepared_text)
                    if len(tokens_matched) > 0:
                        sd['mapped_kv'] = tokens_matched
                        # sd['mapped_category'] = key_category if sd['mapped_category'] == '' else nop()
                        # sd['mapped_label'] = key_label if sd['mapped_label'] == '' and key_label != '' else nop()
                        sd['mapped_category'] = key_category
                        sd['mapped_label'] = key_label
                        cache[sd['row_start']][sd['col_start']]['mapped_category'] = key_category
                        cache[sd['row_start']][sd['col_start']]['mapped_label'] = key_label
                        # sd['text'] = tokens_matched[0]['matched_value'].strip()
                        logging.debug(f'(format_output_structure) : Keys {keys} matched {prepared_text} giving label={key_label}')
                        break
                if sd['mapped_label'] != '':
                    logging.debug(f'(format_output_structure) : Sentence Dictionary is {sd}')
                    break

            if previous != current or current_table_id != previous_table_id:
                current_object = {}
            else:
                previous_table_id = current_table_id
                previous = current

            if current == 'section':
                section_position = sd['id']
                resultObject['Sentence_'+str(section_position)] = {
                    'Text': sd.get('text'),
                    'mapped_kv': sd.get('mapped_kv'),
                    'mapped_category': sd['mapped_category'],
                    'mapped_label': sd['mapped_label']
                }

                current_object = {
                    'Text': sd.get('text'),
                    'mapped_kv': sd.get('mapped_kv'),
                    'mapped_category': sd['mapped_category'],
                    'mapped_label': sd['mapped_label']
                }
                previous_id = section_position
            elif current == 'table':
                table_position = sd['table_id']
                if sd['table_id'] == previous_table_position:
                    pass
                else:
                    current_object = {}
                    previous_table_position = sentence.__dict__['table_id']
                    previous_id = previous_table_position
                if sd['row_start'] == previous_row_start_position:
                    pass
                else:
                    current_object = {}
                    previous_col_start_position = sd['col_start']
                    previous_row_start_position = sd['row_start']
                row_position = sd['row_start']
                col_position =  sd['col_start']                
                row_key = ''.join(str(row_position))
                col_key = ''.join(str(col_position))
                
                # if cache[previous_col_start_position] is not None:
                #     if cache[previous_row_start_position][sd['col_start']] == previous_col_start_position:
                #         if sd['mapped_label'] == '':
                #             # sd['mapped_label'] = previous_row_mapped_label
                #             sd['mapped_label'] = cache[previous_col_start_position][sd['col_start']]['mapped_label']
                #         if sd['mapped_category'] == '':
                #             # sd['mapped_category'] = previous_row_mapped_category
                #             sd['mapped_category'] = cache[previous_col_start_position][sd['col_start']]['mapped_category']
                # previous_row_mapped_category = current_object['mapped_category']
                # previous_row_mapped_label = current_object['mapped_label']

                current_object['Text'] = sd['text']
                current_object['mapped_kv']= sd.get('mapped_kv')
                current_object['mapped_category'] = sd['mapped_category'],
                current_object['mapped_label'] = sd['mapped_label']

                previous_id = table_position
                if 'Table_'+str(previous_id) in resultObject.keys():
                    if row_key in resultObject['Table_'+str(previous_id)].keys():
                        if len(resultObject['Table_'+str(previous_id)][row_key].keys()) > 0:
                            resultObject['Table_'+str(previous_id)][row_key][col_key] = current_object
                        else:
                                resultObject['Table_'+str(previous_id)][row_key] = {col_key: current_object} 
                    else:
                        resultObject['Table_'+str(previous_id)][row_key] = {col_key: current_object}
                else: 
                    resultObject['Table_'+str(previous_id)] = { row_key: { col_key: current_object} }
    #logging.info(f'(format_output_structure) : Result Object is {resultObject}')
    return resultObject
## Apply templated output in the next stage
def map_result_to_output_template(template, interim_object):
    #logging.info(f'(map_result_to_output_template) : ========== ')
    output_object = {}
    with open(template) as json_file:
        template_object = json.load(json_file)
    for key, value in template_object.items():
        if key != 'sectionHeaderKeys':
            # output_object[key] = [{}]
            output_object[key] = []
            # Use the following as template to determine all keys; Useful when actual data may not have all keys.
            # for l2k, l2value in value.items():
            #     output_object[key][0][l2k] = ''
    #logging.info(f'(map_result_to_output_template) : Output object = {output_object}')

    for key, value in interim_object.items():
        # For each row of the dictionary

        if key.find('Sentence_') > -1:
            # This is a sentence
            for k2, v2 in value.items():
                if k2 == 'mapped_category' and v2 is not None:
                    category = value[k2]
                    label = value['mapped_label']
                    #logging.info(f'(map_result_to_output_template) : value={value}')
                    val = value['mapped_kv'][0]['matched_value']
                    # output_object[category][label] = val
                    output_object = {

                        category: [{
                            label: val
                        }]
                    }
            #logging.info(f'(map_result_to_output_template) : Processed Sentence and Output object = {output_object}')

        elif key.find('Table_') > -1:
            # A table starts here. Iterate through it.
            # #logging.info(f'Got a table')
            category = ''
            rows = []
            new_value = {}
            n_table = value

            try:
                del value["0"]
                # Delete the 0th row as it's only an index. Revisit this when the HTML generation process is modified.
                for row_id, row in value.items():
                    # AKC remove the 0th (first) column as it's only an index. Revisit this when the HTML generation process is modified
                    del row["0"]
                    # Test: item["0"] should exist, should be a serial number column and should be true for all tables
            except (RuntimeError, KeyError):
                pass
            except:
                pass
        
            try:
                for key, item in value.items():
                    item_str = ', '.join("{!s}={!r}".format(k,v) for (k,v) in item.items())
                    if 'mapped_kv' not in item_str:
                        del value[key]
                        ## AKC Test this. Why is 'mapped_kv' not in item_str - note that interim object has all three keys
                        pass
            except RuntimeError:
                pass

            max_keys = 0
            table_columns = {}
            for row_id, row in value.items():
                num_keys = len(row.keys())
                if max_keys <= num_keys:
                    max_keys = num_keys
                # elif max_keys == num_keys:
                    for colk, colv in row.items():
                        if colv['mapped_category'][0] != '':
                            #logging.info(f'(map_result_to_output_template) : mapped_category found in {colv.keys()}')
                            table_columns[colk] = {
                                'mapped_category': colv['mapped_category'][0],
                                'mapped_label': colv['mapped_label']
                            }
                            #logging.info(f'(map_result_to_output_template) : table_columns[colk]={table_columns[colk]}')
                        # else:
                        #     table_columns[colk] = {
                        #         'mapped_category': '',
                        #         'mapped_label': ''
                        #     }
                        # #logging.info(f'(map_result_to_output_template) : mapped_category not found in {colv.keys()}')

            #logging.info(f'(map_result_to_output_template) : Max Keys = {max_keys}, and first row with table_columns={table_columns}')

            try:
                for row_id, row in value.items():
                    for colk, colv in row.items():
                        # if len(colv.keys()) > 1:
                        if len(row.keys()) > 1:
                            if colk in table_columns.keys():
                                colv['mapped_category'] = [table_columns[colk]['mapped_category']]
                                if colv['mapped_label'] == '':
                                    colv['mapped_label'] = table_columns[colk]['mapped_label']
                                colv['mapped_kv'] = [{
                                    'matched_label': colv['Text'],
                                    'matched_text': colv['Text']
                                }]
                            else:
                                # #logging.info(f'(map_result_to_output_template) : colk={colk} was not found in table_columns.keys()={table_columns.keys()}')
                                pass
                    #logging.info(f'(map_result_to_output_template) : Pre')
                    #logging.info(f'(map_result_to_output_template) : This row is now={row}')
                    #logging.info(f'(map_result_to_output_template) : Post')
            except KeyError:
                logging.error(f'(map_result_to_output_template) : Exception {KeyError} in for row_id, row in value.items()')
                pass 
            except:
                logging.error(f'(map_result_to_output_template) : Unknown Exception in for row_id, row in value.items()')
                pass
            
            # All preparations are done, now start mapping

            for rkey, row in value.items():
                # for each row
                try:
                    category = table_columns[list(row.keys())[0]]['mapped_category']
                    #logging.info(f'(map_result_to_output_template) : Output category is now set to {category}')
                except KeyError:
                    logging.error(f'(map_result_to_output_template) : Exception setting output category for final build {KeyError}')
                #logging.info(f'(map_result_to_output_template) : Matched category for final output {category}')
                if category != '':
                    #skip if category not found
                    out_dict = {}
                    for colk, col in row.items():
                        if col['Text'] != '':
                            out_dict[col['mapped_label']] = col['Text']
                            # Output only rows with value from token match
                    if len(out_dict.keys()) > 0:
                        # logging.info(f'(map_result_to_output_template) : output_object={output_object}')
                        # output_object[category].append(
                        #     out_dict
                        # ) 
                        if output_object[category] is None and len(output_object[category]) > 0:
                            output_object[category].append(
                                out_dict
                            ) 
                        else:
                            output_object[category] = [
                                out_dict
                            ]

            '''
            for row_key in value.keys():
                #logging.info(f'(map_result_to_output_template) : for {row_key} in value.keys()={value.keys()}')
                # 0 => key
                for colk, colv in value[row_key].items():
                    #logging.info(f'(map_result_to_output_template) : for {colk} in value[row_key].items()={value[row_key].items()}')
                    # 0 => key
                    if 'mapped_category' in colv.keys():
                        #logging.info(f'(map_result_to_output_template) :found mapped_category  in colv.keys()={colv.keys()}')
                        category = colv['mapped_category'][0]
                    #logging.info(f'(map_result_to_output_template) : Did not find mapped_category  in colv.keys()={colv.keys()}')
                # First get the category of documents
                if category not in output_object.keys():
                # output_object[category] = output_object[category] if output_object[category] is not None else []
                    # #logging.info(f'Adding {category} to {output_object}')
                    output_object[category] = []
                else:
                    # #logging.info(f'output_object has property {category}')
                    pass
                # 
                # iterate column wise within the table using the column count of the first row
                try:
                    for r_key, r_cols in value.items():
                        # for each row of the table
                        this_dict = {}
                        if r_key != '0':
                            # skip the first row
                            for e_key, entry in r_cols.items():
                                # get the columns of this row
                                try:
                                    # this_dict[value['0'][e_key]['mapped_label']] = entry['Text']
                                    value_rkey_ekey_mapped_label = value[r_key][e_key]['mapped_label']
                                    this_dict[value_rkey_ekey_mapped_label] = entry['Text']
                                    #logging.info(f'(map_result_to_output_template) : Adding value_rkey_ekey_mapped_label={value_rkey_ekey_mapped_label} to this_dict={this_dict}')
                                except KeyError:
                                    pass
                            # output_object[category].append(this_dict)                
                except KeyError:
                    logging.error(f'(map_result_to_output_template) : While doing "for r_key, r_cols in value.items():", Found key error={KeyError}')
                except:
                    pass
            output_object[category].append(this_dict)
            '''                
        else:
            pass
    return output_object