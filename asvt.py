"""Генерирует файл с таблицей истинности, выводит сднф, группировку по весам

Порядок переменных в картах Карно обратный! Тоесть:
   321 000 001 ...
654
000     1   0  ...
001     0   1  ...
...    ... ... ...
сднф = !x1*!x2*!x3*!x4*!x5*!x6 + x1*!x2*!x3*x4*!x5*!x6 + ...
"""

import xlsxwriter
import itertools

carnot_table_raw = '''
00011000
11111111
10100001
10011000
00011001
10100001
10111101
10011001
'''

truth_table = {}

for row_num, row in enumerate(carnot_table_raw.split('\n')[1:-1]):
    for col_num, val in enumerate(row):
        # генерим код грея из номера стоблца, строки и запихуиваем в хэшик со значением val
        truth_table[bin((7 - row_num) ^ ((7 - row_num) >> 1))[2:].zfill(3) + bin((7 - col_num) ^ ((7 - col_num) >> 1))[2:].zfill(3)] = val


workbook = xlsxwriter.Workbook('truth_table.xlsx')
worksheet = workbook.add_worksheet()

for num, key in enumerate(sorted(truth_table)):
    worksheet.write(num, 0, key)
    worksheet.write(num, 1, truth_table[key])

workbook.close()

# x1x2x3x4x5x6
sdnf = []

for key, value in truth_table.items():
    if value == '1':
        sdnf.append(key)

sdnf_str = ""

for term in sdnf:
    for num, val in enumerate(term):
        if val is "1":
            sdnf_str += "x" + str(num)
        else:
            sdnf_str += "!x" + str(num)
    sdnf_str += " + "

print("СДНФ---------------------")
print(sdnf_str[:-3])
print("-------------------------")


group_by_weight = {}

for term in sdnf:
    if term.count('1') not in group_by_weight:
        group_by_weight[term.count('1')] = {term: True}
    else:
        group_by_weight[term.count('1')][term] = True

print("Одинаковые веса:---------")
print("-------------------------")
for key in sorted(group_by_weight):
    print(key, ": (" + " ".join(group_by_weight[key]) + ")")


implicants_levels = [group_by_weight, ]


def one_symb_diff(a, b):
    mask = None
    for i in range(len(a)):
        if a[i] != b[i]:
            if mask is None:
                mask = a[:i] + '~' + a[i + 1:]
            else:
                return None
    return mask


counter = 0
while True:
    new_level = {}
    for k in implicants_levels[counter].keys():
        if k + 1 in implicants_levels[counter]:
            for it in itertools.product(implicants_levels[counter][k].keys(), implicants_levels[counter][k + 1].keys()):
                if one_symb_diff(it[0], it[1]):
                    implicants_levels[counter][k][it[0]] = False
                    implicants_levels[counter][k + 1][it[1]] = False
                    # 01~0101
                    new_imp = one_symb_diff(it[0], it[1])
                    if new_imp.count('1') not in new_level:
                        new_level[new_imp.count('1')] = {new_imp: True}
                    else:
                        new_level[new_imp.count('1')][new_imp] = True
    if not len(new_level):
        break
    implicants_levels.append(new_level)
    counter += 1


result = []
print("Склееные импликанты:----------------")
for level in implicants_levels:
    for k, v in level.items():
        for key, val in v.items():
            if val == True:
                print(key)
                result.append(key)
print("------------------------------------")


def minniterm_check(term, perv):
    for i in range(len(term)):
        if term[i] != '~' and term[i] != perv[i]:
            return False
    return True


workbook2 = xlsxwriter.Workbook('implikant_table.xlsx')
worksheet = workbook2.add_worksheet()

for num, key in enumerate(sdnf):
    worksheet.write(0, num + 1, key)
    for n, k in enumerate(sorted(result)):
        worksheet.write(n + 1, 0, k)
        if minniterm_check(k, key):
            worksheet.write(n + 1, num + 1, "+")

workbook2.close()
