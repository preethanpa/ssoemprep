import throttler_functions as tf
import pii_spaces as ps 

config = {
    #date_of_birth | date_of_birth = mention_subclass("DateOfBirth") | date_of_birth_matcher = RegexMatchSpan(rgx="^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\\d\\d$", longest_match_only=False) | date_of_birth_ngrams = MentionNgrams(n_max=4)
    'date_of_birth': {
        'Context': 'date_of_birth',
        'MentionName': 'DateOfBirth',
        'MentionNameUI': ['DATE OF BIRTH'], 
        'MentionValuesOrSampleData': ['NAME OF DOCUMENTS', 'DOCUMENT NAME', 'DOCUMENT TITLE'], 
        'MentionRegex': "^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\\d\\d$", 
        # 'MentionNGrams': ps.MentionNgramsDoB(3, split_tokens=["-", "/"]),
        # 'MaxNGrams': ps.MentionNgramsDoB(3, split_tokens=["-", "/"]), 
        'MentionNGrams': 3,
        'MaxNGrams': 3, 
        'Candidates': ['DateOfBirth', 'NameAndDateOfBirth'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'dob_anywhere',
                'tf': tf.tf_byname('dob_anywhere')
            }
        ]  
    },
    #email_id | email_id = mention_subclass("EmailId") | email_id_matcher = RegexMatchSpan(rgx="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", longest_match_only=False)
    'email_id': {
        'Context': 'email_id',
        'MentionName': 'EmailId',
        'MentionNameUI': ['EMAIL ADDRESS'], 
        'MentionValuesOrSampleData': ['abhi@third-ray.com', 'abhikc@gmail.com', 'abhi@thirdrayai.onmicrosoft.com'], 
        'MentionRegex': "^(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$", 
        'MentionNGrams': 4,
        'MaxNGrams': 6, 
        #ps.MentionNgramsEmail(6, split_tokens=['-', '@', '_', '.']), 
        'Candidates': ['EmailIdCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'email_match_filter',
                'tf': tf.tf_byname('email_match_filter')
            }
        ]
    },
    #document_passport_number	PassportNumber		Z4244577	^([A-Z]\d{7})$	1	QDocNamePassportNumberCandidate
    'passport_number': {
        'Context': 'passport_number',
        'MentionName': 'PassportNumber',
        'MentionNameUI': ['PASSPORT NUMBER'], 
        'MentionValuesOrSampleData': ['Z4244577', 'A1238817'], 
        'MentionRegex': "^([A-Z]\d{7})$", 
        'MentionNGrams': 1,
        'MaxNGrams': 2,
        'Candidates': ['QDocNamePassportNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'passport_number_match_filter',
                'tf': tf.tf_byname('passport_number_match_filter')
            }
        ]
                             
    },
    #document_passport_number	PassportNumber		Z4244577	^([A-Z]\d{7})$	1	QDocNamePassportNumberCandidate
    'u_id': {
        'Context': 'u_id',
        'MentionName': 'UId',
        'MentionNameUI': ['AADHAAR NUMBER', 'UIDAI NUMBER'], 
        'MentionValuesOrSampleData': ['123456481233', '76473425342', '3546 8747 9928'], 
        'MentionRegex': "^([2-9]{1}[0-9]{3}(\s)?[0-9]{4}(\s)?[0-9]{4})$", 
        'MentionNGrams': 3,
        'MaxNGrams': 3,
        'Candidates': ['AadhaarNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'u_id_match_filter',
                'tf': tf.tf_byname('u_id_match_filter')
            }
        ]
                             
    },
    'phone_number': {
        'Context': 'phone_number',
        'MentionName': 'PhoneNumber',
        'MentionNameUI': ['PHONE NUMBER'], 
        'MentionValuesOrSampleData': ['+91 87634 48283', '+91 8765432190', '8765432109'], 
        'MentionRegex': "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", 
        'MentionNGrams': 4,
        'MaxNGrams': 6,
        'Candidates': ['PhoneNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'phone_number_match_filter',
                'tf': tf.tf_byname('phone_number_match_filter')
            }
        ]
                             
    },
    'permanent_account_number': {
        'Context': 'permanent_account_number',
        'MentionName': 'PermanentAccountNumber',
        'MentionNameUI': ['PERMANENT ACCOUNT NUMBER'], 
        'MentionValuesOrSampleData': ['ACGOD1168T', 'ACCAN6749K'], 
        'MentionRegex': "^([A-Z]{5}[0-9]{4}[A-Z]{1})$", 
        'MentionNGrams': 1,
        'MaxNGrams': 1,
        'Candidates': ['PermanentAccountNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'permanent_account_number_match_filter',
                'tf': tf.tf_byname('permanent_account_number_match_filter')
            }
        ]     
    }
}
# pii_matcher = Union(data_subject_name_matcher, date_of_birth_matcher, email_id_matcher)