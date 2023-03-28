
def compare_perft():
    with open("stockfish_output.txt", "r") as s:
        st = sorted([i.replace('\n', '') for i in s.readlines()])
    
    with open("my_output.txt", "r") as m:
        my = sorted([i.replace('\n', '') for i in m.readlines()])
    
    for j in zip(st, my):
        if j[0] != j[1]:
            print(j)

compare_perft()