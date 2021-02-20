from fonduer.candidates import CandidateExtractor
from fonduer.candidates import MentionNgrams
from fonduer.candidates import MentionExtractor 

from fonduer.candidates.models import Mention
from fonduer.candidates.models import mention_subclass
from fonduer.candidates.models import candidate_subclass

from fonduer.candidates.matchers import RegexMatchSpan, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union

from fonduer.features import Featurizer
from fonduer.utils.data_model_utils import *
import re
'''
PARAMETERIZE THROTTLER FUNCTIONS

APPROACH 1

def create_a_function(*args, **kwargs):

    def function_template(*args, **kwargs):
        pass

    return function_template

my_new_function = create_a_function()

APPROACH 2
>>> exec("""def a(x):
...   return x+1""")
>>> a(2)
3

SEE THIS SO THREAD: https://stackoverflow.com/questions/11291242/python-dynamically-create-function-at-runtime
'''

'''
FOR NOW, USE THE EXEC APPROACH (2)

'''
def tf_byname(cname):
    
    def data_subject_name_in_same_table_filter(c):
        (data_subject_name_label, data_subject_name) = c
        if same_table((data_subject_name_label, data_subject_name)):
            return (is_horz_aligned((data_subject_name_label, data_subject_name)) or is_vert_aligned((data_subject_name_label, data_subject_name)))
        return False
    
    def data_subject_name_in_same_sentence_filter(c):
        (data_subject_name_label, data_subject_name) = c
        if same_sentence((data_subject_name_label, data_subject_name)):
            return True
        return False
    
    def email_match_filter(c):
        (email_id) = c
        if same_sentence((email_id)):
            return True

    def email_name_same_sentence_filter(c):
        (email_id, data_subject_name) = c
        if same_sentence((email_id, data_subject_name)):
            return True

    def data_subject_email_in_same_tablerow_filter(c):
        (data_subject_name, email_id_label, email_id) = c
        if same_table((data_subject_name, email_id_label, email_id)):
            return (is_horz_aligned((data_subject_name, email_id_label, email_id)) or is_vert_aligned((data_subject_name, email_id_label, email_id)))
        return True
    
    def all_in_same_table_filter(c):
        (data_subject_name, date_of_birth, email_id) = c
        if same_table((data_subject_name, date_of_birth, email_id)):
            return (is_horz_aligned((data_subject_name, date_of_birth, email_id)) or is_vert_aligned((data_subject_name, date_of_birth, email_id)))
        return True
    
    def all_not_in_same_table_filter(c):
        (data_subject_name, date_of_birth, email_id) = c
        if not same_table((data_subject_name, date_of_birth, email_id)):
            if is_horz_aligned((data_subject_name, date_of_birth, email_id)):
                return False
            if is_vert_aligned((data_subject_name, date_of_birth, email_id)):
                return False
        return True

    def all_are_tablular_aligned(c):
        (data_subject_name, date_of_birth, email_id) = c
        if is_tabular_aligned((data_subject_name, date_of_birth, email_id)):
            return True
        if is_tabular_aligned((data_subject_name, email_id)):
            return True
        if is_tabular_aligned((data_subject_name, date_of_birth)):
            return True
        return False
    
    def name_all_over_the_place(c):
        (data_subject_name) = c
        if same_sentence((data_subject_name)):
            return True
        return False

    def dob_anywhere(c):
        (date_of_birth) = c
        if same_sentence((date_of_birth)):
            return True
        return False
    
    def dob_label_anywhere(c):
        (date_of_birth_label) = c
        if same_sentence((date_of_birth_label)):
            return True
        return False
    
    def person_identifier_filter(c):
        (data_subject_name, date_of_birth, email_id) = c
        if same_table((data_subject_name, date_of_birth, email_id)):
            return (is_horz_aligned((data_subject_name, date_of_birth, email_id)) or is_vert_aligned((data_subject_name, date_of_birth, email_id)))
        return True

    def passport_number_match_filter(c):
        (passport_number) = c
        if same_sentence((passport_number)):
            return True

    def aadhaar_number_match_filter_same_sentence(c):
        (u_id) = c
        if same_sentence((u_id)):
            return True

    def phone_number_match_filter_same_sentence(c):
        (phone_number) = c
        if same_sentence((phone_number)):
            return True

    def phone_number_match_filter(c):
        (phone_number) = c
        if phone_number_match_filter_same_sentence and True:
            return True

    def permanent_account_number_match_filter(c):
        (permanent_account_number) = c
        if same_sentence((permanent_account_number)):
            return True

    def aadhaar_number_match_filter(c):
        (u_id) = c
        if aadhaar_number_match_filter_same_sentence and True:
            return True

    def grand_throttler(c):
        if all_not_in_same_table_filter(c):
            return True
        if all_in_same_table_filter(c):
            return True
        if all_are_tablular_aligned(c):
            return True
        if name_all_over_the_place(c):
            return False
        return True
    
    def grand_throttler_for_name(c):
        if data_subject_name_in_same_table_filter(c) or data_subject_name_in_same_sentence_filter(c):
            return True
        return True

    
    throttler_function_strings = {
        
        'data_subject_name_in_same_table_filter' : data_subject_name_in_same_table_filter,

        'data_subject_name_in_same_sentence_filter' :data_subject_name_in_same_sentence_filter ,

        'data_subject_email_in_same_tablerow_filter': data_subject_email_in_same_tablerow_filter,

        'all_in_same_table_filter': all_in_same_table_filter,

        'all_not_in_same_table_filter':    all_not_in_same_table_filter,

        'all_are_tablular_aligned': all_are_tablular_aligned,

        'name_all_over_the_place'  :name_all_over_the_place ,

        'person_identifier_filter': person_identifier_filter,

        'dob_anywhere': dob_anywhere,

        'dob_label_anywhere': dob_label_anywhere,

        'email_match_filter': email_match_filter,

        'email_name_same_sentence_filter': email_name_same_sentence_filter,

        'passport_number_match_filter': passport_number_match_filter,

        'phone_number_match_filter': phone_number_match_filter,

        'u_id_match_filter': aadhaar_number_match_filter,

        'permanent_account_number_match_filter'

        'grand_throttler': grand_throttler,

        'grand_throttler_for_name':grand_throttler_for_name,
    }
    
    return throttler_function_strings.get(cname)

# tf_byname('data_subject_name_in_same_table_filter')