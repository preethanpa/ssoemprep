from fonduer.candidates.matchers import LambdaFunctionFigureMatcher, RegexMatchSpan, DictionaryMatch, LambdaFunctionMatcher, Intersect, Union

invoice_number_rgx = r"(ATPL\/1920\/EXP\/)[0-9]{1,3}"
amount_rgx = r"[,]?(\$([1-9][0-9]{0,1},)?[0-9]{3}(\.[0-9]{0,2}){0,1})[,]?"
passport_rgx = r"[,]?([A-Z]\d{7})[,]?"
dob_rgx = r"(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\\d\\d[,]?"
name_rgx = r"(?!an|the|of|can|hello|ship|offshore|train|word|Microsoft|word|seaman|birth|place|india|honduras|date|expire|position|applied|vessel|preference|officer|seafarer|nationality|religion|applicant).*([\w'][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:\-,.[\]]{2,})[,]?"
email_rgx = r"(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])[,]?"
pan_rgx = r"([A-Z]{5}[0-9]{4}[A-Z]{1})[,]?"
uid_rgx = r"[,]?([2-9]{1}\d{3}\s*\d{4}\s*\d{4})[,]?"
phone_rgx = r"[,]?((\+\d{1,2}(\s)?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}|(\+\d{1,2}(\s)?)?\(?[\s.-]?\d{5}\)?[\s.-]?\d{5})[,]?"

amount_rgx_matcher = RegexMatchSpan(rgx=amount_rgx, longest_match_only=True)

name_rgx_matcher = RegexMatchSpan(rgx=name_rgx, longest_match_only=True)

passport_rgx_matcher = RegexMatchSpan(rgx=passport_rgx, longest_match_only=True)

pan_rgx_matcher = RegexMatchSpan(rgx=pan_rgx, longest_match_only=True)

dob_rgx_matcher = RegexMatchSpan(rgx=dob_rgx, longest_match_only=True)

data_subject_name_label = RegexMatchSpan(rgx=name_rgx, longest_match_only=True)

email_rgx_matcher = RegexMatchSpan(rgx=email_rgx, longest_match_only=True)

uid_rgx_matcher = RegexMatchSpan(rgx=uid_rgx, longest_match_only=True)

phone_rgx_matcher = RegexMatchSpan(rgx=phone_rgx, longest_match_only=True)

invoice_number_matcher = RegexMatchSpan(rgx=phone_rgx, longest_match_only=True)


unified_matcher_example = Union(invoice_number_rgx, amount_rgx_matcher)


matcher = {
    'data_subject_name_label': data_subject_name_label,
    'data_subject_name': name_rgx_matcher,
    'date_of_birth_label': '',
    'date_of_birth': dob_rgx_matcher,
    'email_id_label': data_subject_name_label,
    'email_id': email_rgx_matcher,
    'passport_number': passport_rgx_matcher,
    'permanent_account_number': pan_rgx_matcher,
    'u_id': uid_rgx_matcher,
    'phone_number': phone_rgx_matcher
}
