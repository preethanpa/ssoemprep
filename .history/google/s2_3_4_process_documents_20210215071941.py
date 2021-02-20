from fonduer.parser.preprocessors import HTMLDocPreprocessor, CSVDocPreprocessor, TextDocPreprocessor, TSVDocPreprocessor
from fonduer.parser import Parser
import sys
import json
import imp

from pprint import pprint

from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle

class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_python_object': b64encode(pickle.dumps(obj)).decode('utf-8')}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(b64decode(dct['_python_object'].encode('utf-8')))
    return dct

getdbref = __import__('s1_2_getdbref') 
# Will return <module '1_2_getdbref' from '/home/dsie/Developer/sandbox/3ray/server/backend/python/kbc_process/1_2_getdbref.py'>

# pdf_path = json.loads(sys.argv[1])['doc_name'] 
# docs_path = json.loads(sys.argv[1])['html_path']

# pdf_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/pdf/'
# docs_path = '/home/dsie/Developer/sandbox/3ray/3rml/kbc_process/documents/html/'

pdf_path = json.loads(sys.argv[1])['pdf_path'] 
docs_path = json.loads(sys.argv[1])['html_path']
job_id = json.loads(sys.argv[1])['job_id']


max_docs = 1000
PARALLEL = 4
doc_preprocessor = None
execution_stack = {
    "debug": ["1. Get session object..."],
    "job_id": job_id,
    "location": {
        pdf_path: pdf_path,
        d
    }
}

try:
    session = getdbref.get_session()
    sessType = type(session) # Will return <class 'sqlalchemy.orm.session.Session'>
    execution_stack.append("Done.")
    execution_stack.append("2. Processing layout...")
    try:
        doc_preprocessor = HTMLDocPreprocessor(docs_path, max_docs=max_docs)
        execution_stack.append("Processed layout successfully.")
        execution_stack.append("3. Creating parser...")
        corpus_parser = None
        try:
            corpus_parser = Parser(session, structural=True, lingual=True, visual=True, pdf_path=pdf_path)
            execution_stack.append("Created parser successfully.")
            execution_stack.append("4. Applying parser...")
            try:
                corpus_parser.apply(doc_preprocessor, parallelism=PARALLEL)
                execution_stack.append("Applied parser successfully.")
                print(json.dumps(execution_stack))
            except Exception as corpus_parser_apply_exception:
                print(f'{execution_stack}, corpus_parser.apply {corpus_parser_apply_exception}')
        except Exception as corpus_parser_exception:
            print(f'{execution_stack}, corpus_parser = Parser() {corpus_parser_exception}')
    except Exception as doc_preprocessor_exception:
        print(f'{execution_stack}, doc_preprocessor = HTMLDocPreprocessor(), {doc_preprocessor_exception}')
except Exception as session_exception:
    print(f'{execution_stack}, session = getdbref.get_session(), {session_exception}')
