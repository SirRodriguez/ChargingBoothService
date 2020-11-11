def ceildiv(a, b):
	return -(-a // b)

def get_iter_pages(page, pages, left_edge=2, left_current=2, right_current=5, right_edge=2):
	last = 0
	for num in range(1, pages + 1):
		if num <= left_edge or (num > page - left_current - 1 and num < page + right_current) or num > pages - right_edge:
			if last + 1 != num:
				yield None
			yield num
			last = num