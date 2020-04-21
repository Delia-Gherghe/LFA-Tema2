import copy

def matrice(L, n):
    M = [[0] * n for i in range(n)]
    for i in L:
        if M[i[0]][i[2]] == 0:
            M[i[0]][i[2]] = i[1]                                # Functie ce returneaza o matrice pe baza unei liste de tupluri
        else:
            if isinstance(M[i[0]][i[2]], list) == False:
                M[i[0]][i[2]] = [M[i[0]][i[2]]]
            M[i[0]][i[2]].append(i[1])
    return M


def multime_tr_caract(M, v, ch, n):
    mult = set()
    for i in v:
        for j in range(n):
            if isinstance(M[i][j], list) == False:              # Functie ce returneaza multimea de stari in care ne putem
                if M[i][j] == ch:                               # duce din multimea de stari v cu caracterul ch
                    mult.add(j)
            elif ch in M[i][j]:
                mult.add(j)
    return mult


def lambdaclosure(M, n):
    LC = [set() for i in range(n)]
    for i in range(n):
        LC[i].add(i)
        LC[i] = LC[i] | (multime_tr_caract(M, [i], '$', n))
    ok = 0
    while ok == 0:                                              # Calculam lambda-inchiderea (multimile de stari in care ne putem
        ok = 1                                                  # duce din fiecare stare cu 0 sau mai multe tranzitii lambda)
        for i in range(n):
            ex = LC[i]
            for j in LC[i]:
                LC[i] = LC[i] | LC[j]
            if ex != LC[i]:
                ok = 0
    return LC


def lnfa_to_nfa(A):
    n = A[0]
    m = A[1]
    c = A[2]
    init = A[3]
    nrfin = A[4]
    fin = A[5]
    L = A[6]

    M = matrice(L, n)                                           # Construirea matricii lambda-NFA

    LC = lambdaclosure(M, n)                                    # Aflarea lambda-inchiderii

    TrC = [[] for i in range(m)]
    for i in range(m):
        for x in LC:                                            # Gasim multimile de stari in care ne putem duce din fiecare multime
            TrC[i].append(multime_tr_caract(M, x, c[i], n))     # de stari a lambda-inchiderii cu fiecare caracter din alfabet

    for i in range(m):
        for j in range(n):
            x = set()
            for k in TrC[i][j]:             # Reunind multimile din lambda-inchidere corespunzatoare fiecarei
                x = x | LC[k]               # stari din multimile de stari obtinem delta*
            TrC[i][j] = x

    for i in range(n):
        if i not in fin:
            for x in fin:
                if x in LC[i]:              # Actualizam starile finale
                    fin.append(i)
                    break
    nrfin = len(fin)

    red = []
    redper = []
    for i in range(n):
        for j in range(i + 1, n):
            if i not in red and j not in red:
                if (i in fin and j in fin) or (i not in fin and j not in fin):      # Gasim starile redundante
                    for k in range(m):
                        if TrC[k][i] != TrC[k][j]:
                            break
                    else:
                        redper.append((i, j))
                        red.append(j)

    if len(red) != 0:
        for i in range(m):
            j = 0
            k = 0
            while j < n:
                if j in red:
                    TrC[i].pop(k)                       # Stergem starile redundante
                else:
                    k = k + 1
                j = j + 1
        for i in fin:
            if i in red:
                fin.remove(i)

        for i in range(m):
            for j in range(n - len(red)):
                for x in redper:
                    if x[1] in TrC[i][j]:               # Inlocuim starile redundante in tabelul de tranzitii
                        TrC[i][j].remove(x[1])
                        if x[0] not in TrC[i][j]:
                            TrC[i][j].add(x[0])

        i = 0
        j = 0
        g = 0
        while i < n:
            if i in red:
                j = j + 1
                g = 1
            if g == 1 and i not in red:
                for x in range(m):
                    for y in range(n - len(red)):       # Renumerotam starile astfel incat sa fie numerotate de la 0 la
                        if i in TrC[x][y]:              # noul numar de stari
                            TrC[x][y].remove(i)
                            TrC[x][y].add(i - j)
                if i in fin:
                    fin.remove(i)
                    fin.append(i - j)
            i = i + 1
        nrfin = len(fin)

        n = n - len(red)

    L = []
    for i in range(m):
        for j in range(n):
            for x in TrC[i][j]:                         # Construim noua lista de tranzitii
                L.append((j, c[i], x))

    return n, m, c, init, nrfin, fin, L


def nfa_to_dfa(A):
    n = A[0]
    m = A[1]
    c = A[2]
    init = A[3]
    nrfin = A[4]
    fin = A[5]
    L = A[6]

    M = matrice(L, n)

    q = [{init}]
    tranz = []

    for x in q:
        for ch in c:
            y = multime_tr_caract(M, x, ch, n)          # Eliminam nedeterminismul afland starile (compuse) in care
            if y != set():                              # putem ajunge cu fiecare caracter
                tranz.append([x, ch, y])
            if y not in q and y != set():
                q.append(y)

    n = len(q)

    for i in range(n):
        for j in range(len(tranz)):
            if tranz[j][0] == q[i]:
                tranz[j][0] = i                         # Renumerotarea starilor de la 0 la noul n
            if tranz[j][2] == q[i]:
                tranz[j][2] = i
    for i in range(len(tranz)):
        tranz[i] = (tranz[i][0], tranz[i][1], tranz[i][2])
    L = copy.deepcopy(tranz)

    newfin = []
    for i in fin:
        for j in range(n):
            if i in q[j] and j not in newfin:           # Actualizarea starilor finale
                newfin.append(j)
    fin = copy.deepcopy(newfin)
    nrfin = len(fin)

    return n, m, c, init, nrfin, fin, L

def dfa_to_dfamin(A):
    n = A[0]
    m = A[1]
    c = A[2]
    init = A[3]
    nrfin = A[4]
    fin = A[5]
    L = A[6]

    M = matrice(L, n)

    complet = 1
    for i in range(n):
        for ch in c:
            if multime_tr_caract(M, [i], ch, n) == set():   # Daca automatul nu este complet, construim automatul
                complet = 0                                 # complet definit echivalent
                L.append((i, ch, n))
    if complet == 0:
        for ch in c:
            L.append((n, ch, n))
        n = n + 1
        M = matrice(L, n)

    T = [[True] * (i) for i in range(n)]                    # La inceput marcam toata matricea cu True

    for i in range(1, n):
        for j in range(i):
            if (i in fin and j not in fin) or (i not in fin and j in fin):  # Marcam cu False perechile (i,j) unde una
                T[i][j] = False                                             # este stare finala si cealalta nefinala

    new = 1
    while new == 1:
        new = 0
        for i in range(1, n):
            for j in range(i):
                if T[i][j] == True:
                    s = []
                    for ch in c:                                            # Marcam cu False starile separabile prin
                        x = list(multime_tr_caract(M, [i], ch, n))          # cel putin un caracter
                        y = list(multime_tr_caract(M, [j], ch, n))
                        if x[0] != y[0]:
                            s.append(T[max(x[0], y[0])][min(x[0], y[0])])
                    if False in s:
                        T[i][j] = False
                        new = 1

    eq = []
    for i in range(1, n):
        for j in range(i):
            if T[i][j] == True:
                for x in eq:
                    if j in x:
                        x.add(i)
                        break                           # Grupam starile echivalente
                else:
                    eq.append({j, i})
    for i in range(n):
        for x in eq:
            if i in x:
                break
        else:
            eq.append({i})
    for i in range(len(eq)):
        for j in range(i + 1, len(eq)):
            if list(eq[i])[0] > list(eq[j])[0]:
                eq[i], eq[j] = eq[j], eq[i]


    L = []
    for i in range(len(eq)):
        for ch in c:
            x = multime_tr_caract(M, eq[i], ch, n)          # Construim lista de tranzitii pe clasele de echivalenta
            for y in eq:
                if list(x)[0] in y:
                    L.append((i, ch, eq.index(y)))

    for x in eq:
        for y in x:
            if y == init:                                   # Actualizam starea initiala
                init = eq.index(x)

    newfin = []
    for x in eq:
        if list(x)[0] in fin:
            newfin.append(eq.index(x))                      # Actualizam starile finale
    fin = copy.deepcopy(newfin)
    nrfin = len(fin)

    n = len(eq)                                             # Actualizam numarul de stari

    Matrice_adiacenta = [[0] * n for i in range(n)]
    for x in L:
        if x[0] != x[2]:                                    # Construim matricea de adiacenta a automatului
            Matrice_adiacenta[x[0]][x[2]] = 1

    vectorviz = []
    for s in range(n):
        viz = [0] * n
        q = []
        q.append(s)
        viz[s] = 1
        while len(q) != 0:
            i = q[0]
            q.pop(0)
            for j in range(n):
                if Matrice_adiacenta[i][j]:     # Pentru fiecare stare vedem in ce stari se poate ajunge plecand din ea
                    if viz[j] == 0:
                        q.append(j)
                        viz[j] = 1
        vectorviz.append(viz)

    elim = []
    for x in vectorviz:
        for i in fin:
            if x[i] == 1:                       # Gasim starile dead - end
                break
        else:
            elim.append(vectorviz.index(x))

    s = init
    viz = [0] * n
    q = []
    q.append(s)
    viz[s] = 1
    while len(q) != 0:
        i = q[0]
        q.pop(0)
        for j in range(n):
            if Matrice_adiacenta[i][j]:             # Vedem in ce stari se poate ajunge plecand din starea initiala
                if viz[j] == 0:
                    q.append(j)
                    viz[j] = 1

    for i in viz:
        if i == 0 and i not in elim:
            elim.append(viz.index(i))               # Adaugam starile neaccesibile

    if len(elim) != 0:
        for x in elim:
            y = 0
            while y < len(L):
                if L[y][0] == x or L[y][2] == x:    # Eliminam starile dead - end sau neaccesibile si toate
                    L.pop(y)                        # tranzitiile din sau spre acestea
                else:
                    y = y + 1

        i = 0
        j = 0
        g = 0
        while i < n:
            if i in elim:
                j = j + 1
                g = 1
            if g == 1 and i not in elim:
                for x in L:
                    if x[0] == i:
                        x[0] = i - j                    # Renumerotam starile astfel incat sa fie numerotate de la 0 la
                    if x[2] == i:                       # noul numar de stari
                        x[2] = i - j
                if i in fin:
                    fin.remove(i)
                    fin.append(i - j)
            i = i + 1
        n = n - len(elim)

    return n, m, c, init, nrfin, fin, L

def citire():
    n = int(f.readline())
    m = int(f.readline())
    c = f.readline().split()
    init = int(f.readline())
    nrfin = int(f.readline())
    fin = [int(x) for x in f.readline().split()]                # Citirea datelor
    l = int(f.readline())
    L = []
    for i in range(l):
        lin = f.readline().split()
        L.append((int(lin[0]), lin[1], int(lin[2])))
    return n, m, c, init, nrfin, fin, L

def afis(A):
    print("Numarul de stari este", A[0])
    print("Numarul de litere din alfabet este", A[1])
    print("Alfabetul este", A[2])
    print("Starea initiala este", A[3])
    print("Numarul de stari finale este", A[4])
    print("Multimea de stari finale este", A[5])
    print("Tranzitiile sunt:")
    for x in A[6]:
        print(x)
    print()

f = open("datetema2.in")
A = citire()
B = citire()
C = citire()
A = lnfa_to_nfa(A)
afis(A)
B = nfa_to_dfa(B)
afis(B)
C = dfa_to_dfamin(C)
afis(C)
f.close()
