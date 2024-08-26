from pyzbar.pyzbar import ZBarSymbol

# Сортируем и сохраняем результат в переменной
sorted_symbols = sorted(ZBarSymbol.__members__.keys())

# Выводим результат
print(sorted_symbols)