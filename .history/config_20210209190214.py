import throttler_functions as tf
import pii_spaces as ps 

config = {
    #data_subject_name_label = mention_subclass("DataSubjectNameLabel") | data_subject_name_label_matcher = RegexMatchSpan(rgx="^\A(NAME OF DATA SUBJECT)$", longest_match_only=False) | data_subject_name_label_ngrams = MentionNgrams(n_max=3)
    'data_subject_name_label': {
        'Context': 'data_subject_name_label',
        'MentionName': 'DataSubjectNameLabel',
        'MentionNameUI': ['NAME OF DATA SUBJECT LABEL'], 
        'MentionValuesOrSampleData': ['NAME OF DATA SUBJECT', 'DATA SUBJECT NAME', ' NAME '], 
        'MentionRegex': "^(NAME OF DATA SUBJECT|DATA SUBJECT NAME|NAME:|NAME :|NAME)$", 
        'MentionNGrams': 3,
        'MaxNGrams': ps.MentionNgrams(3), 
#         'Candidates': ['NameLabel', 'NameFromDocument', 'NameAndDateOfBirth']        
        'Candidates': ['NameFromDocument'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'name_all_over_the_place',
                'tf': tf.tf_byname('name_all_over_the_place')
            }
        ]
    },
    #data_subject_name = mention_subclass("NameOfDataSubject") | data_subject_name_matcher = RegexMatchSpan(rgx="^(?!an|the|of|can|hello|ship|offshore|train|word|Microsoft|word|seaman|birth|place|india|honduras|date|expire|position|applied|vessel|preference|officer|seafarer|nationality|religion|applicant).*([\w'][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:\-,.[\]]{2,})$", longest_match_only=False, ignore_case=True) | data_subject_name_ngrams = MentionNgrams(n_max=3)
    'data_subject_name': {
        'Context': 'data_subject_name',
        'MentionName': 'NameOfDataSubject',
        'MentionNameUI': ['NAME OF DATA SUBJECT'], 
        'MentionValuesOrSampleData': ["Abhijit Kumar Choudhury", "Preethan Pandaradathil", "Michael D\'Souza"], 
        'MentionRegex': "^(?!an|the|of|can|hello|ship|offshore|train|word|Microsoft|word|seaman|birth|place|india|honduras|date|expire|position|applied|vessel|preference|officer|seafarer|nationality|religion|applicant).*([\w'][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:\-,.[\]]{2,})$", 
        'MentionNGrams': 4,
        'MaxNGrams': ps.MentionNgrams(4), 
#         'Candidates': ['NameFromDocument', 'NameAndDateOfBirth']
        'Candidates': ['NameFromDocument'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'name_all_over_the_place',
                'tf': tf.tf_byname('name_all_over_the_place')
            }
        ]
    },
    #date_of_birth_label | date_of_birth_label = mention_subclass("DateOfBirthLabel") | ^(DATE OF BIRTH|BIRTH DATE|DOB|D.O.B.|D.O.B)$
    'date_of_birth_label': {
        'Context': 'date_of_birth_label',
        'MentionName': 'DateOfBirthLabel',
        'MentionNameUI': ['DATE OF BIRTH LABEL'], 
        'MentionValuesOrSampleData': ['DATE OF BIRTH', 'BIRTH DATE', 'DOB', 'D.O.B.', 'D.O.B'], 
        'MentionRegex': "^(DATE OF BIRTH|BIRTH DATE|DOB|D.O.B.|D.O.B)$", 
        'MentionNGrams': 3,
        'MaxNGrams': 3, 
        'Candidates': ['DateOfBirthLabel', 'DateOfBirth', 'NameAndDateOfBirth'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'dob_label_anywhere',
                'tf': tf.tf_byname('dob_label_anywhere')
            }
        ]
    },
    #date_of_birth | date_of_birth = mention_subclass("DateOfBirth") | date_of_birth_matcher = RegexMatchSpan(rgx="^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\\d\\d$", longest_match_only=False) | date_of_birth_ngrams = MentionNgrams(n_max=4)
    'date_of_birth': {
        'Context': 'date_of_birth',
        'MentionName': 'DateOfBirth',
        'MentionNameUI': ['DATE OF BIRTH'], 
        'MentionValuesOrSampleData': ['NAME OF DOCUMENTS', 'DOCUMENT NAME', 'DOCUMENT TITLE'], 
        'MentionRegex': "^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\\d\\d$", 
        'MentionNGrams': ps.MentionNgramsDoB(3, split_tokens=["-", "/"]), ,
        'MaxNGrams': ps.MentionNgramsDoB(3, split_tokens=["-", "/"]), 
        'Candidates': ['DateOfBirth', 'NameAndDateOfBirth'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'dob_anywhere',
                'tf': tf.tf_byname('dob_anywhere')
            }
        ]  
    },
    #email_id_label | email_id_label = mention_subclass("EmailIdLabel") | 
    'email_id_label': {
        'Context': 'email_id_label',
        'MentionName': 'EmailIdLabel',
        'MentionNameUI': ['EMAIL ADDRESS LABEL'], 
        'MentionValuesOrSampleData': ['EMAIL ADDRESS', 'E-MAIL ID', 'EMAIL', 'EMAIL ID', 'EMAIL ID.', 'EMAIL ADDR.', 'EMAIL ADDR'], 
        'MentionRegex': "^(EMAIL ADDRESS|E-MAIL ID|EMAIL|EMAIL ID|EMAIL ID.|EMAIL ADDR.|EMAIL ADDR)$", 
        'MentionNGrams': 3,
        'MaxNGrams': 3, 
        'Candidates': ['EmailIdCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'data_subject_email_in_same_tablerow_filter',
                'tf': tf.tf_byname('data_subject_email_in_same_tablerow_filter')
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
        'MentionNGrams': ps.MentionNgramsPassport(1),
        'MaxNGrams': ps.MentionNgramsPassport(1),
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
        'MentionRegex': "^([2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4})$", 
        'MentionNGrams': 3,
        'MaxNGrams': 3,
        'Candidates': ['AadhaarNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'aadhaar_number_match_filter',
                'tf': tf.tf_byname('aadhaar_number_match_filter')
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
        'Candidates': ['PersonalAccountNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'permanent_account_number_match_filter',
                'tf': tf.tf_byname('permanent_account_number_match_filter')
            }
        ]
                             
    },
    'phone_number': {
        'Context': 'phone_number',
        'MentionName': 'PhoneNumber',
        'MentionNameUI': ['PHONE NUMBER'], 
        'MentionValuesOrSampleData': ['+91 87634 48283', '+91 8765432190', '8765432109'], 
        'MentionRegex': "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", 
        'MaxNGrams': 6,
        'Candidates': ['PhoneNumberCandidate'],
        'ThrottlerFunctions': [ 
            {
                'tf_name': 'phone_number_match_filter',
                'tf': tf.tf_byname('phone_number_match_filter')
            }
        ]
                             
    }
}
# pii_matcher = Union(data_subject_name_matcher, date_of_birth_matcher, email_id_matcher)