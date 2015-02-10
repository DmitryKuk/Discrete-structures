# Author: Dmitry Kukovinets (d1021976@yandex.ru)
# Encoding: UTF-8, Unix
# Indents: tabs, Size: 4

import re


# Функция, получающая данные с клавиатуры. Возвращает словарь:
# 'seq_id' - строка-идентификатор последовательности
# 'ind_id' - строка-идентификатор индекса
# 'pairs' - список пар коэффициент-шаг
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
	
	# Это тоже работает
	# lines = [line for line in text.split('}') if len(line) > 0]
	# pattern = re.compile(r'^(\+\d+|-\d+)(\D)\{(\D)(\+\d+|-\d+)$')
	# groups = [pattern.match(line).groups() for line in lines]
	
	matcher = re.compile(r'(\+\d+|-\d+)(\D)\{(\D)(\+\d+|-\d+)\}').scanner(text)
	groups = []
	while True:
		y = matcher.match()
		if y != None:
			groups.append(y.groups())
		else:
			break
	
	# Печать списка групп
	# i = 0
	# for x in groups:
	# 	print("\t# %2d: %s"% (i, x))
	# 	i += 1
	
	# Список групп для "10 a_{n} + 20 a_{n-1} + 40 a_{n-3} = 0":
	#  0: ('+10', 'a', 'n', '+0')
	#  1: ('+20', 'a', 'n', '-1')
	#  2: ('+40', 'a', 'n', '-3')
	
	return {
		'seq_id': groups[0][1], 'ind_id': groups[0][2],
		'pairs': [[int(g[0]), int(g[3])] for g in groups]
	}


def get_pairs(data):
	pairs = sorted(data['pairs'], key=lambda cs: cs[1], reverse=True)	# Сортируем по шагам
	offset = pairs[0][1]			# Смещение наименьшего шага от нуля
	for x in pairs: x[1] -= offset	# Корректируем шаги
	for i in range(1, len(pairs)):	# Добавляем недостающие пары коэфф.-шаг
		if pairs[i - 1][1] - pairs[i][1] != 1:
			for x in range(pairs[i][1] + 1, pairs[i - 1][1]):
				pairs.insert(i, [0, x])
	return pairs	# Список полон, т.е. нет пропущенных пар с коэфф. = 0


def format_num(num, need_space = True):
	if need_space:
		if num < 0: return '- %d'% (-num)
		else: return '+ %d'% (num)
	else:
		if num < 0: return '%d'% (num)
		else: return '+%d'% (num)


def scalar_mult(coeffs, seq, use_braces = True):
	k = 0		# Количество слагаемых - влияет на необходимость скобок
	s = ''
	for i in range(0, len(coeffs)):
		if isinstance(coeffs[i], int):
			if coeffs[i] != 0:
				if coeffs != 1:
					if len(s) > 0:	s += ' ' + format_num(coeffs[i])	# Не первое слагаемое
					else:			s += '%d'% (coeffs[i])				# Первое число
				if len(seq[i]) > 0: s += ' ' + seq[i]					# Строка ('x^i')
				k += 1
		else:
			if len(coeffs[i]) > 0:
				if len(s) > 0:							# Не первое слагаемое
					s += ' '
					if coeffs[i][0] not in ['+', '-']:	# Добавление '+' перед очередным слагаемым
						s += '+ '
				s += coeffs[i]
				if len(seq[i]) > 0: s += ' ' + seq[i]	# Строка ('x^i')
				k += 1
	if use_braces and k > 1: s = '+ (' + s + ')'		# Добавление скобок
	return s


def print_result(func_id, var_id, seq_id, pairs):
	if len(pairs) == 0:
		print('It\'s nothing let to solve now...')
	elif len(pairs) == 1:
		if pairs[0][0] == 0:	print('$%s(%s) = %s_0$'% (func_id, var_id, seq_id))
		else:					print('$%s(%s) = 0$'% (func_id, var_id))
	else:
		print('$%s(%s) = \\frac{%s}{%s}$'% (
			func_id, var_id,
			
			# Числитель
			scalar_mult(
				# Коэффициенты
				[
					scalar_mult(
						[c[0] for c in pairs[0: i + 1]],
						['%s_%d'% (seq_id, -a[1]) for a in reversed(pairs[0: i + 1])]
					)
						for i in range(0, len(pairs) - 1)
				],
				
				# Ряд x^i
				[
					'' if -p[1] == 0 else var_id if -p[1] == 1 else '%s^%d'% (var_id, -p[1])
						for p in pairs
				],
				
				# Не использовать скобки
				False
			),
			
			# Знаменатель: sum B_i * x^i
			scalar_mult(
				# Список коэффициентов
				[ b[0] for b in pairs ],
				
				# Ряд x^i
				[
					'' if -p[1] == 0 else var_id if -p[1] == 1 else '%s^%d'% (var_id, -p[1])
						for p in pairs
				],
				
				# Не использовать скобки
				False
			)
		))


data = get_data()	# Получаем данные
p = get_pairs(data)	# Получаем коэффициенты:
# b_0 a_{N} + b_1 a_{N-1} + ... + b_k a_{N-k} = 0

# Печать отчёта
print_result('f', 'x', data['seq_id'], p)
