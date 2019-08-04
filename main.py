import nltk
# from nltk.book import *
from nltk.corpus import gutenberg
# from nltk.corpus import brown
from nltk_functions import *
from my_python_functions import *
import re
import os
import sys
import pprint












def getParaIndex(p, lines_list):
    for i, l in enumerate(lines_list):
        if p == l:
            return i#


def printJudgement(judgement_bits):

    # para_counter = 1
    # for jb in judgement_bits:
    #     if 'para' in jb['types']:
    #         print('[' + str(para_counter) + '] ' + jb['text'])
    #         para_counter += 1

    for jb in judgement_bits:
        print()
        print("----")
        print(jb["text"])


def printJudgementFullData(judgement_bits):
    for jb in judgement_bits:
        print(jb)
        print()



def getPossibleHeadings(judgement_bits):
    possible_headings = []
    for i, jb in enumerate(judgement_bits):
        x = trueIfPossibleHeading(jb['text'])
        if x:
            x['index'] = i
            possible_headings.append(x)
    return possible_headings


def getPossibleOrdinalTypes(ordinal):
    possible_types = []
    if re.match(r'^\d+$', ordinal):
        possible_types.append("numeric_integer")
    if re.match(r'^\d+\.\d+$', ordinal):
        possible_types.append("numeric_decimal")
    if re.match(r'^\d+(\.\d+){2,}$', ordinal):
        possible_types.append("numeric_decimal_mult")
    if re.match(r'^[IVXLCDM]$', ordinal, re.I):
        possible_types.append("letter")
        possible_types.append("roman_numeral")
    elif re.match(r'^[A-Z]$', ordinal, re.I):
        possible_types.append("letter")
    elif re.match(r'^[IVXLCDM]{2,}$', ordinal, re.I):
        possible_types.append("roman_numeral")
    elif re.match(r'^[A-Z]{2,}$', ordinal, re.I):
        possible_types.append("letter")
    return possible_types


rn_letter_values = {
    "i": 1,
    "v": 5,
    "x": 10,
    "l": 50,
    "c": 100,
    "d": 500,
    "m": 1000
}


def convertRNtoNum(roman_numeral):
    total = 0
    last_letter_val = 0
    for letter in roman_numeral:
        val = rn_letter_values[letter.lower()]
        if val > last_letter_val:
            total -= 2 * last_letter_val
        last_letter_val = val
        total += val
    return total


alphabet = "abcdefghijklmnopqrstuvwxyz"


def trueIfPossibleHeading(jb_text):
    phm = re.match(
        r'^(?:\[\d+]\s*)?(?:([A-Za-z0-9\.]{1,6})\.|\(([A-Za-z0-9\.]{1,6})\)|([A-Za-z0-9\.]{1,6})\s*[-–—]|\(([A-Za-z0-9\.]{1,6})\)\s*[-–—])\s+[\"“\'‘]?\w+',
        jb_text)
    if not phm:
        return False

    if phm[1]:
        format = "normal"
        separator = "period"
        ordinal = phm[1]
    elif phm[2]:
        format = "paren"
        separator = "none"
        ordinal = phm[2]
    elif phm[3]:
        format = "normal"
        separator = "dash"
        ordinal = phm[3]
    elif phm[4]:
        format = "paren"
        separator = "dash"
        ordinal = phm[4]

    ordinal_types = getPossibleOrdinalTypes(ordinal)

    possible_nums = []
    if "letter" in ordinal_types:
        possible_nums.append((alphabet.index(ordinal.lower()) + 1, "letter"))
    if "roman_numeral" in ordinal_types:
        possible_nums.append((convertRNtoNum(ordinal), "roman_numeral"))
    if "numeric_integer" in ordinal_types:
        possible_nums.append((int(ordinal), "numeric_integer"))

    ph = {
        'ordinal': ordinal,
        'ordinal_types': ordinal_types,
        'possible_nums': possible_nums,
        'format': format,
        'separator': separator
    }

    return ph


def getHeadingGroups(possible_headings):

    heading_groups = []
    for i, ph in enumerate(possible_headings):

        if len(ph['possible_nums']) == 1 and ph['possible_nums'][0][0] == 1:
            ph['num'] = 1
            heading_groups.append([ph])
            continue

        if i == 0:
            ph['num'] = 1
            heading_groups.append([ph])
            continue

        found_a_hg = False
        for i2, hg in enumerate(heading_groups):
            # if found_a_hg:
            #     break
            if ph['format'] == hg[0]['format'] and ph['separator'] == hg[0]['separator']:
                for pn in ph['possible_nums']:
                    if pn[0] == hg[-1]['num'] + 1:
                        if found_a_hg:
                            print("ERROR: Found a hg")
                            break
                        ph['num'] = pn[0]
                        heading_groups[i2].append(ph)
                        found_a_hg = True
                        break

        if not found_a_hg and 1 in [pn[0] for pn in ph['possible_nums']]:
            ph['num'] = 1
            heading_groups.append([ph])
    return heading_groups


def markParas(judgement_bits):
    for jb in judgement_bits:
        jb_m = re.match(r'^\[\d+]\s+', jb['text'])
        if jb_m:
            jb['types'].append("para")
            jb['text'] = jb['text'][len(jb_m[0]):]


def getNumParasBetween2Indexes(i1, i2, judgement_bits):
    num_interim_paras = 0
    for interim_jb in judgement_bits[i1 + 1:i2]:
        if "para" in interim_jb['types']:
            num_interim_paras += 1
    return num_interim_paras


def extract1ItemHeadingGroups(heading_groups):
    hg_indexes_to_delete = []
    for i, hg in enumerate(heading_groups):
        if len(hg) == 1:
            hg_indexes_to_delete.append(i)
    hg_indexes_to_delete = sorted(hg_indexes_to_delete, reverse=True)
    for i in hg_indexes_to_delete:
        del heading_groups[i]


def checkHeadingGroupIndexes(heading_groups, list_groups, judgement_bits):
    list_hg_indexes = []
    # hg_indexes_to_delete = []
    for i1, hg in enumerate(heading_groups):
        num_interim_paras_list = []
        for i2, ph in enumerate(hg):
            if i2 == 0:
                continue
            i3 = hg[i2 - 1]['index']
            i4 = hg[i2]['index']
            num_interim_paras = getNumParasBetween2Indexes(i3, i4, judgement_bits)
            num_interim_paras_list.append(num_interim_paras)
        # avg_num_interim_paras = avg_num_interim_paras
        num_0_interim_paras = len([n for n in num_interim_paras_list if n == 0])
        ratio = num_0_interim_paras / len(hg)
        if ratio > 0.4:
            # hg_indexes_to_delete.append(i1)
            list_hg_indexes.append(i1)
    list_hg_indexes = sorted(list_hg_indexes, reverse=True)
    for i in list_hg_indexes:
        list_groups.append(heading_groups[i])
        del heading_groups[i]


def markHeadings(heading_groups, judgement_bits):
    for i, hg in enumerate(heading_groups):
        for h in hg:
            judgement_bits[h['index']]['types'].append("heading")
            judgement_bits[h['index']]['data']['heading_data'] = {
                'rank': i,
                'ordinal': h['ordinal'],
                'ordinal_types': h['ordinal_types'],
                'possible_nums': h['possible_nums'],
                'format': h['format'],
                'separator': h['separator'],
                'num': h['num']
            }


def markLists(list_groups, judgement_bits):
    for i, lg in enumerate(list_groups):
        for li in lg:
            judgement_bits[li['index']]['types'].append("list")
            judgement_bits[li['index']]['data']['list_data'] = {
                'rank': i,
                'ordinal': li['ordinal'],
                'ordinal_types': li['ordinal_types'],
                'possible_nums': li['possible_nums'],
                'format': li['format'],
                'separator': li['separator'],
                'num': li['num']
            }


# ---------- MAIN ----------:

this_txt = open('TCCtxts/1997/152633 Canada Inc. v. The Queen (1997-11-18).txt').read()

# Clean the txt:
lines = re.split(r'\n+', this_txt)
lines2 = [l for l in lines if not re.match(r'^\[(OFFICIAL ENGLISH )?TRANSLATION\]$', l)]
para1_index = -1
paras = [(l, int(re.match(r'^\[(\d+)]', l)[1])) for l in lines2 if re.match(r'^\[\d+]', l)]

para_groups = []
this_para_group = []
for i, p in enumerate(paras):
    if i == len(paras) - 1:
        this_para_group.append(p)
        para_groups.append(this_para_group)
    elif i == 0:
        this_para_group.append(p)
    elif paras[i - 1] and p[1] == paras[i - 1][1] + 1:
        this_para_group.append(p)
    else:
        para_groups.append(this_para_group)
        this_para_group = [p]
max_pg_len = max(len(pg) for pg in para_groups)
main_para_group = [pg for pg in para_groups if len(pg) == max_pg_len][0]

first_para_index = getParaIndex(main_para_group[0][0], lines2)
last_para_index = getParaIndex(main_para_group[-1][0], lines2)

judgement_bits0 = lines2[first_para_index:last_para_index + 1]

judgement_bits = [{'text': b, 'types': [], 'data': {}} for b in judgement_bits0]

possible_headings = getPossibleHeadings(judgement_bits)

heading_groups = getHeadingGroups(possible_headings)

markParas(judgement_bits)

single_item_heading_groups = [hg for hg in heading_groups if len(hg) == 1]
extract1ItemHeadingGroups(heading_groups)

list_groups = []
checkHeadingGroupIndexes(heading_groups, list_groups, judgement_bits)

markHeadings(heading_groups, judgement_bits)
markLists(list_groups, judgement_bits)

untyped_bits = [jb for jb in judgement_bits if len(jb['types']) == 0]
# for ub in untyped_bits:
#     print(ub)

# for ph in possible_headings:
#     print("---")
#     print(ph)
# for hg in heading_groups:
#     print("---")
#     for ph in hg:
#         print(ph)

printJudgement(judgement_bits)
# printJudgementFullData(judgement_bits)






# jb_sents = [mySentTokenize(jb['text']) for jb in judgement_bits]
# jb_words = []
# jb_pos_tagged = []
# for jbs in jb_sents:
#     print()
#     print("=====")
#     for i, s in enumerate(jbs):
#         print(str(i+1) + ":", s)
#         tokens = nltk.word_tokenize(s)
#         jb_words.append(tokens)
#         tagged = nltk.pos_tag(tokens)
#         jb_pos_tagged.append(tagged)
# for j in jb_pos_tagged:
#     print(j)


# for jb in judgement_bits:
#     jb_sents = nltk.sent_tokenize(jb['text'])
#     print()
#     print("=====")
#     for i, s in enumerate(jb_sents):
#         print(str(i+1) + ":", s)

# sys.exit()

# ---------- RUNNING IT ON MANY CASES: ----------


# # GET TCC CORPUS
# path = "TCCtxts/1997"
# for filename in os.listdir(path):
#     print(filename)
#
#     this_txt = open(path + "/" + filename).read()
#
#     # print([this_txt])
#
#     # Clean the txt:
#     lines = re.split(r'\n+', this_txt)
#     lines2 = [l for l in lines if not re.match(r'^\[(OFFICIAL ENGLISH )?TRANSLATION\]$', l)]
#     para1_index = -1
#     paras = [(l, int(re.match(r'^\[(\d+)]', l)[1])) for l in lines2 if re.match(r'^\[\d+]', l)]
#
#     para_groups = []
#     this_para_group = []
#     for i, p in enumerate(paras):
#         if i == len(paras) - 1:
#             this_para_group.append(p)
#             para_groups.append(this_para_group)
#         elif i == 0:
#             this_para_group.append(p)
#         elif paras[i - 1] and p[1] == paras[i - 1][1] + 1:
#             this_para_group.append(p)
#         else:
#             para_groups.append(this_para_group)
#             this_para_group = [p]
#     max_pg_len = max(len(pg) for pg in para_groups)
#     main_para_group = [pg for pg in para_groups if len(pg) == max_pg_len][0]
#
#     first_para_index = getParaIndex(main_para_group[0][0], lines2)
#     last_para_index = getParaIndex(main_para_group[-1][0], lines2)
#
#     judgement_bits0 = lines2[first_para_index:last_para_index + 1]
#
#     judgement_bits = [{'text': b, 'types': [], 'data': {}} for b in judgement_bits0]
#
#     possible_headings = getPossibleHeadings(judgement_bits)
#
#     heading_groups = getHeadingGroups(possible_headings)
#
#     markParas(judgement_bits)
#
#     single_item_heading_groups = [hg for hg in heading_groups if len(hg) == 1]
#     extract1ItemHeadingGroups(heading_groups)
#
#     list_groups = []
#     checkHeadingGroupIndexes(heading_groups, list_groups, judgement_bits)
#
#     markHeadings(heading_groups, judgement_bits)
#     markLists(list_groups, judgement_bits)
#
#     untyped_bits = [jb for jb in judgement_bits if len(jb['types']) == 0]
#     # for ub in untyped_bits:
#     #     print(ub)
#
#     # for ph in possible_headings:
#     #     print("---")
#     #     print(ph)
#     # for hg in heading_groups:
#     #     print("---")
#     #     for ph in hg:
#     #         print(ph)
#
#     printJudgement(judgement_bits)
#     printJudgementFullData(judgement_bits)
#
#     # jb_sents = [mySentTokenize(jb['text']) for jb in judgement_bits]
#     # jb_words = []
#     # jb_pos_tagged = []
#     # for jbs in jb_sents:
#     #     print()
#     #     print("=====")
#     #     for i, s in enumerate(jbs):
#     #         print(str(i+1) + ":", s)
#     #         tokens = nltk.word_tokenize(s)
#     #         jb_words.append(tokens)
#     #         tagged = nltk.pos_tag(tokens)
#     #         jb_pos_tagged.append(tagged)
#     # for j in jb_pos_tagged:
#     #     print(j)
#
#     # for jb in judgement_bits:
#     #     jb_sents = nltk.sent_tokenize(jb['text'])
#     #     print()
#     #     print("=====")
#     #     for i, s in enumerate(jb_sents):
#     #         print(str(i+1) + ":", s)
#
#     sys.exit()



# fdist1 = FreqDist(text1)
# print(fdist1)
# print(fdist1.most_common(50))
# print(fdist1['whale'])
#
# print(text4.collocations())

