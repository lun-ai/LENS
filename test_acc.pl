opt_tests(ex_1, ['d']).
opt_tests(ex_2, ['c', 'd']).
opt_tests(ex_3, ['c']).
opt_tests(ex_4, ['e', 'f', 'g']).
opt_tests(ex_5, ['c']).
opt_tests(ex_6, ['h']).
opt_tests(ex_7, ['j']).
opt_tests(ex_8, ['a', 'b']).
opt_tests(ex_9, ['b']).
opt_tests(ex_10, ['d', 'e']).
opt_tests(ex_11, ['d']).
opt_tests(ex_12, ['c', 'd']).
opt_tests(ex_13, ['d', 'e']).
opt_tests(ex_14, ['f']).

test(Src, Cnt) :-
    atomic_list_concat([Src, '/bk.pl'], SrcPath),
    consult(SrcPath),
    consult('bk.pl'),
    opt_tests(Src, Ts),
    findall(G, gate(G), Gates),
    dnc((Gates, 0, ''), (_, N, Out)),
    length(Gates, L),
    N1 is L - N,
    format("Circuit No. ~w, test: ~w, split: ~w/~w\n", [Src, Out, N, N1]),
    (member(Out, Ts) -> Cnt = 1; Cnt = 0),
    unload_file('bk.pl'),
    unload_file(SrcPath),!.
    

test_acc :-
    findall(Cnt, (opt_tests(Src, _), test(Src, Cnt)), Cnts),
    sum_list(Cnts, Sum),
    length(Cnts, N),
    Acc is Sum / N,
    format("Number of tests: ~d\nNumber of passed tests: ~d\nAccuracy: ~3f", [N, Sum, Acc]).