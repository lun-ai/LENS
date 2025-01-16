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

concat_bk(ExNums) :-
    tell('all_bk.pl'),
    forall(member(N, ExNums), concat_bk_1(N)),
    forall(member(N, ExNums), concat_bk_2(N)),
    told.

concat_bk_1(N) :-
    atomic_list_concat(['ex_', N, '/bk.pl'], SrcPath),
    consult(SrcPath),
    forall(gate(G), (NewG is N * 100 + G, write(gate(NewG)), writeln('.'))),
    unload_file(SrcPath).
concat_bk_2(N) :-
    atomic_list_concat(['ex_', N, '/bk.pl'], SrcPath),
    consult(SrcPath),
    forall((is_connected(X, Y), gate(X), gate(Y)), (NewX is N * 100 + X, NewY is N * 100 + Y, write(is_connected(NewX, NewY)), writeln('.'))),
    unload_file(SrcPath).

test(Src, Cnt) :-
    atomic_list_concat([Src, '/bk.pl'], SrcPath),
    consult(SrcPath),
    consult('bk.pl'),
    opt_tests(Src, Ts),
    findall(G, gate(G), Gates),
    select_test(Gates, N, G),
    length(Gates, L),
    N1 is L - N,
    out(G,Out),
    (member(Out, Ts) -> Cnt = 1; Cnt = 0),
    format("Circuit No. ~w, test: ~w, split: ~w/~w, Optimal: ~w\n", [Src, Out, N, N1, Cnt]),
    writeln(select_test(Gates, N, G)),
    unload_file('bk.pl'),
    unload_file(SrcPath),!.

% test(Src, Cnt) :-
%     atomic_list_concat([Src, '/bk.pl'], SrcPath),
%     consult(SrcPath),
%     consult('bk.pl'),
%     opt_tests(Src, Ts),
%     findall(G, gate(G), Gates),
%     select_test(Gates, (N, N1)),
%     findall(G, (member(T, Ts), out(G, T)), Gs),
%     maplist(partition_sizes, Gs, Ps),
%     (member((N, N1), Ps) -> Cnt = 1; Cnt = 0),
%     format("Circuit No. ~w, split: ~w/~w, Optimal: ~w\n", [Src, N, N1, Cnt]),
%     writeln(select_test(Gates, (N, N1))),
%     unload_file('bk.pl'),
%     unload_file(SrcPath),!.

test_acc :-
    unload_file('all_bk.pl'),
    findall(Cnt, (opt_tests(Src, _), test(Src, Cnt)), Cnts),
    sum_list(Cnts, Sum),
    length(Cnts, N),
    Acc is Sum / N,
    format("Number of tests: ~d\nNumber of passed tests: ~d\nAccuracy: ~3f", [N, Sum, Acc]).