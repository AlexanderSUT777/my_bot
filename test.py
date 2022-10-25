print('a b c')
for a in range(0, 2):
    for b in range(0, 2):
        for c in range(0, 2):
            if a == (b or c) == b:
                print(a, b, c)