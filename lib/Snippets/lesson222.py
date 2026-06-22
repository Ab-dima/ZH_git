len_number,numbers  = int(input()),list(map(int, input().split()))


new_lst = [print(numbers.pop(numbers.index(min(numbers))), end=' ') for i in numbers.copy()]
