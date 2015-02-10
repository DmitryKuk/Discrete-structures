# Author: Dmitry Kukovinets (d1021976@yandex.ru)
# Encoding: UTF-8, Unix
# Indents: tabs, Size: 4

cache = {}	# Кеш для p(m)

def p(m):	# Собственно, количество разбиений
	# Проверка на корректность и граничные случаи
	if m < 0: return 0
	elif m == 0 or m == 1: return 1
	elif m in cache: return cache[m]
	
	# Формула для вычисления:
	# p(m) = sum[(-1)^(k + 1) * (p_1 + p_2), k > 0]
	# p_1 = p(m - (3k^2 - k) / 2)
	# p_2 = p(m - (3k^2 + k) / 2)
	
	# Будем суммировать с p_1 и p_2, пока (m - (3k^2 + k) / 2) > 0,
	# затем с p_1, пока (m - (3k^2 - k) / 2) > 0.
	# Промежуточные результаты будут храниться в словаре cache:
	# 	cache[m] = p(m)
	
	res = 0		# Собственно, сумма
	k = 1		# Индекс суммирования, убегающий в бесконечность
	
	while True:		# Суммирование с обоими слагаемыми
		m_2 = m - int(k * (3 * k + 1) / 2)
		if m_2 < 0:		# Проверка на отпадание второго слагаемого
			break
		
		if m_2 in cache: p_2 = cache[m_2]	# Попытка поиска в кеше
		else: cache[m_2] = p_2 = p(m_2)
		
		m_1 = m - int(k * (3 * k - 1) / 2)
		if m_1 in cache: p_1 = cache[m_1]	# Попытка поиска в кеше
		else: cache[m_1] = p_1 = p(m_1)
		
		if k % 2 == 0: res -= p_1 + p_2		# Чётное k:
		else: res += p_1 + p_2				# 	+= (-1)^(k + 1)
		k += 1
	
	while True:		# Суммирование с одним слагаемым
		m_1 = m - int(k * (3 * k - 1) / 2)
		if m_1 < 0:		# Проверка на отпадание первого слагаемого
			break
		
		if m_1 in cache: p_1 = cache[m_1]	# Попытка поиска в кеше
		else: cache[m_1] = p_1 = p(m_1)
		
		if k % 2 == 0: res -= p_1			# Чётное k:
		else: res += p_1					# 	+= (-1)^(k + 1)
		k += 1
	cache[m] = res
	return res


print("Enter integer n (n >= 0)...")
n = int(input())
if n < 0: print("Incorrect input: n must be more than 0!")
else: print("p(", n, ") =", p(n))

# Раскомментируйте строку ниже, чтобы получить
# все промежуточные результаты
#print(cache)
