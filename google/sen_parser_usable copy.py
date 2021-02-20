#!/usr/bin/python
import re
from pprint import pprint

def find_tokens(keys,sentence):
    keys_f = []
    value = ""
    key_value = {}
    result_f = []
    sent_l = sentence.lower()
    for eachk in keys:
        indx = -1
        if eachk.find(' ') > -1:
            indx = sent_l.find(eachk.lower())
        else:
            for token in sent_l.split(' '):
                indx = token.find(eachk.lower())
        if indx != -1:
            keys_f.append(eachk)
            ln = len(eachk)
            valuePart = sentence[indx+ln:]
            end_indx = find_value(keys,valuePart)
            if (end_indx == -1):
                value = valuePart[0:len(valuePart)]
            else:
                value = valuePart[0:end_indx]
            key_value = { 
                            "matched_label": eachk,
                             "matched_value": value
                        }
            result_f.append(key_value)
    return result_f
            
def find_value(keys,sentence):
    sent=sentence.lower()
    prev_indx = -1
    for ky in keys:
        indx = sent.find(ky.lower())
        if (prev_indx == -1):
            prev_indx = indx
        if (indx != -1 and indx < prev_indx):
            prev_indx = indx

    return prev_indx


# find_tokens(keys,sen_f)
