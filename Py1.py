# Author: Dmitry Kukovinets (d1021976@yandex.ru)
# Encoding: UTF-8, Unix
# Indents: tabs, Size: 4

import sys
import re
from fractions import Fraction


# Функция, получающая данные с клавиатуры. Возвращает словарь:
# 'seq_id' - строка-идентификатор последовательности
# 'ind_id' - строка-идентификатор индекса
# 'coeffs' - список коэффициентов
# 'steps'  - список шагов
def get_data():
	# Выражение на входе: "a_{N-2} - a_{N} = 0", упрощаем его:
	text = str(input())									# Получение данных
	text = text[:-4].replace(' ', '').replace('_', '')	# Удаление " = 0", пробелов и подчёркиваний
	if text[0] not in ['-', '+']: text = '+' + text		# Добавление знака первого коэффициента
	text = re.sub(r'\{(\+|\-)(\D)', '{\g<2>', text)		# Удаление знаков у индексов
	text = re.sub(r'\{(\D)\}', '{\g<1>+0}', text)		# Добавление "+0" к индексу в "a{N}"
	text = re.sub(r'(\+|\-)(\D)', '\g<1>1\g<2>', text)	# Добавление пропущенных единиц
	# Получили выражение: "+1a{N-2}-1a{N+0}"
	
	# Разбиение полученных данных на группы по шаблону:
	# (\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\}
	# └────┬─────┘└┬─┘├┘└─┬─┘└─────┬─────┘├┘
	#      │       │  │   │        │      └ Конец индекса
	#      │       │  │   │        └ Шаг в индексе (± цифры)
	#      │       │  │   └ Идентификатор индекса (один не цифровой символ)
	#      │       │  └ Начало индекса
	#      │       └ Идентификатор последовательности (один не цифровой символ)
	#      └ Коэффициент перед слагаемым (± цифры)
	# -- и так от 1 до 4 групп. Конструкция (...){1,4} почему-то не разбивает на группы как надо,
	# игнорируя начало. Пришлось делать: "(...)(...)?(...)?".
	
	matched = re.compile(
		r'''^((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})
			 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?
			 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?
			 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?$''',
		re.VERBOSE).match(text)
	if matched is None: return
	else: groups = matched.groups()
	
	# Печать списка групп
	#i = 0
	#for x in groups:
	#	print("\t# %2d: \'%s\'"% (i, x))
	#	i += 1
	
	# Список групп для "1 a_{n-1} + 2 a_{n-2} + 3 a_{n-3} + 4 a_{n-4} = 0":
	#  0: '+1a{n-1}'
	#  1: '+1'			<- coeff 1
	#  2: 'a'			<- seq_id
	#  3: 'n-1'
	#  4: 'n'			<- ind_id
	#  5: '-1'			<- step 1
	#  6: '+2a{n-2}'
	#  7: '+2'			<- coeff 2
	#  8: 'a'
	#  9: 'n-2'
	# 10: 'n'
	# 11: '-2'			<- step 2
	# 12: '+3a{n-3}'
	# 13: '+3'			<- coeff 3
	# 14: 'a'
	# 15: 'n-3'
	# 16: 'n'
	# 17: '-3'			<- step 3
	# 18: '+4a{n-4}'
	# 19: '+4'			<- coeff 4
	# 20: 'a'
	# 21: 'n-4'
	# 22: 'n'
	# 23: '-4'			<- step 4
	
	return {
		'seq_id': '' if groups[2] is None else groups[2],	# ID последовательности
		'ind_id': '' if groups[4] is None else groups[4],	# ID индекса
		'coeffs': [											# Коэффициенты
			int(0 if groups[ 1] is None else groups[ 1]),
			int(0 if groups[ 7] is None else groups[ 7]),
			int(0 if groups[13] is None else groups[13]),
			int(0 if groups[19] is None else groups[19]) ],
		'steps' : [											# Шаги
			int(0 if groups[ 5] is None else groups[ 5]),
			int(0 if groups[11] is None else groups[11]),
			int(0 if groups[17] is None else groups[17]),
			int(0 if groups[23] is None else groups[23]) ]
	}
	
	# История "открытий" мной регулярных выражений:
	# CORRECT:	r'''^((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})
	# 				 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?
	# 				 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?
	# 				 ((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\})?$'''
	# ALMOST CORRECT: ^((\+\d+|-\d+)(\D)\{((\D)(\+\d+|-\d+))\}){1,4}$
	# WITHOUT ±STEP in indexes: ^((\+\d*|-\d*)(\D)\{(\D)\}){1,4}$
	# OLD: '^((((\+|\-)? ?\d+)? (\D)_\{(\D) ?((\+|\-) ?\d+)?\} ?){1,4})= 0$'


def get_coeffs(data):
	pairs = []		# Список пар коэфф.-шаг
	if data['coeffs'][0] != 0: pairs.append([ data['coeffs'][0], data['steps'][0] ])
	if data['coeffs'][1] != 0: pairs.append([ data['coeffs'][1], data['steps'][1] ])
	if data['coeffs'][2] != 0: pairs.append([ data['coeffs'][2], data['steps'][2] ])
	if data['coeffs'][3] != 0: pairs.append([ data['coeffs'][3], data['steps'][3] ])
	pairs.sort(key=lambda cs: cs[1])	# Сортируем по шагам
	
	coeffs = [ 0, 0, 0, 0 ]		# Список коэффициентов
	offset = pairs[0][1]		# Смещение наименьшего шага от нуля
	for x in pairs:
		x[1] -= offset			# Корректируем шаги
		coeffs[x[1]] = x[0]		# Заполняем список коэффициентов в правильном порядке
	coeffs.reverse()			# Переворачиваем: d +...+ ax^3  ->  ax^3 +...+ d
	return coeffs


def solve_linear_equation(a, b):
	# ax + b = 0
	if a == 0:
		if b == 0: return { 'flag': -1 }	# Любой x - решение
		else: return { 'flag': 0 }			# Решений нет
	return {
		'flag': 1,						# Единственное решение
		1: '\\frac{%d}{%d}'% (-b, a)	# Решение
	}


def solve_quardatic_equation(a, b, c):
	# ax^2 + bx + c = 0
	if a == 0: return solve_linear_equation(b, c)
	
	D = b ** 2 - 4 * a * c
	
	if D == 0:
		return {
			'flag': 3,	# 3: Одно решение кратности 2
			1: '\\frac{%s}{%s}'% (-b, 2 * a)
		}
	if D > 0:	D_str = '\\sqrt{%d}'% (b ** 2 - 4 * a * c)
	else:		D_str = 'i\\sqrt{%d}'% (- (b ** 2 - 4 * a * c))
	
	return {
		'flag': 2,		# 2: Два корня
		1: '\\frac{%d + %s}{%d}'% (-b, D_str, 2 * a),
		2: '\\frac{%d - %s}{%d}'% (-b, D_str, 2 * a)
	}


def solve_cubic_equation(a, b, c, d):
	# ax^3 + bx^2 + cx + d = 0  ->  y^3 + py + q = 0
	if a == 0: return solve_quardatic_equation(b, c, d)
	
	p = Fraction(3 * a * c - b ** 2, 3 * a ** 2)
	p_3_str = '\\frac{%d}{%d}'% (3 * a * c - b ** 2, 9 * a ** 2)
	
	q = Fraction(2 * (b ** 3) - 9 * a * b * c + 27 * (a ** 2) * d, 27 * (a ** 3))
	q_2_str = '\\frac{%d}{%d}'% (2 * (b ** 3) - 9 * a * b * c + 27 * (a ** 2) * d, 54 * (a ** 3))
	
	Q = (p / 3) ** 3 + (q / 2) ** 2
	Q_str = '(%s)^3 + (%s)^2'% (p_3_str, q_2_str)
	
	alpha_str = '\\sqrt[3]{-%s + \\sqrt{%s}}'% (q_2_str, Q_str)
	beta_str  = '\\sqrt[3]{-%s - \\sqrt{%s}}'% (q_2_str, Q_str)
	
	# x = y - b / (3 * a)
	if b == 0: x_suffix = ''
	elif b < 0: x_suffix = ' + \\frac{%d}{%d}'% (-b, 3 * a)
	else: x_suffix = '- \\frac{%d}{%d}'% (b, 3 * a)
	
	x_1_str = '%s + %s %s'% (alpha_str, beta_str, x_suffix)
	x_2_str = '-\\frac{1}{2} (%s + %s) + \\frac{i\\sqrt{3}}{2} (%s - %s)%s'% (alpha_str, beta_str, alpha_str, beta_str, x_suffix)
	x_3_str = '-\\frac{1}{2} (%s + %s) - \\frac{i\\sqrt{3}}{2} (%s - %s)%s'% (alpha_str, beta_str, alpha_str, beta_str, x_suffix)
	
	if Q < 0:			# 4: Три вещественных корня
		return {
			'flag': 4,
			1: x_1_str,
			2: x_2_str,
			3: x_3_str
		}
	elif Q > 0:			# 7: Один вещественный и два сопр. компл. корня
		return {
			'flag': 7,
			1: x_1_str,
			2: x_2_str,
			3: x_3_str
		}
	elif p == q == 0:	# 6: Один трёхкратный вещественный корень
		return {
			'flag': 6,
			1: x_1_str
		}
	else:				# 5: Один однократный и один двукратный вещественные корни
		return {
			'flag': 5,
			1: x_1_str,
			2: x_2_str
		}


data = get_data()
if data is None:
	print("Incorrect input!")
	sys.exit(1)

coeffs = get_coeffs(data)	# Получаем корректные коэффициенты
eq_sols = solve_cubic_equation(coeffs[0], coeffs[1], coeffs[2], coeffs[3])

# Печать отчёта
# -1: Любой x - решение
#  0: Решений нет
#  1: Один корень
#  2: Два корня
#  3: Один двукратный корень
#  4: Три вещественных корня
#  5: Один однократный и один двукратный
#  6: Один трёхкратный корень
#  7: Один вещественный и два сопр. компл.
seq_id = data['seq_id'];  ind_id = data['ind_id']	# Идентификаторы
flag = eq_sols['flag']
if flag == 0: print('$There is not any solutions.$')
elif flag == -1:
	 print('$%s_%s = const_1$'% (seq_id, ind_id))
elif flag == 1:
	 print('$%s_%s = const_1\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		eq_sols[1], ind_id
	))
elif flag == 2:
	 print('$%s_%s = const_1\\cdot (%s)^%s + const_2\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		eq_sols[1], ind_id,
		eq_sols[2], ind_id
	))
elif flag == 3:
	 print('$%s_%s = (const_1 + const_2\\cdot %s)\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		ind_id, eq_sols[2], ind_id
	))
elif flag == 4:
	 print('$%s_%s = const_1\\cdot (%s)^%s + const_2\\cdot (%s)^%s + const_3\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		eq_sols[1], ind_id,
		eq_sols[2], ind_id,
		eq_sols[3], ind_id
	))
elif flag == 5:
	 print('$%s_%s = const_1\\cdot (%s)^%s + (const_2 + const_3\\cdot %s)\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		eq_sols[1], ind_id,
		ind_id,
		eq_sols[2], ind_id
	))
elif flag == 6:
	 print('$%s_%s = (const_1 + const_2\\cdot %s + const_3\\cdot %s^2)\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		ind_id, ind_id, eq_sols[1], ind_id
	))
elif flag == 7:
	 print('$%s_%s = const_1\\cdot (%s)^%s + const_2\\cdot (%s)^%s + const_3\\cdot (%s)^%s$'% (
		seq_id, ind_id,
		eq_sols[1], ind_id,
		eq_sols[2], ind_id,
		eq_sols[3], ind_id
	))
