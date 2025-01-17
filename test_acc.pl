:- ['select_test.pl'].

ex_ids([1,2,3,4,5,6,7,8,9,10,11,12,13,14]).

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

opt_gate_split(ex_1,[104]).
opt_gate_split(ex_2,[203,204]).
opt_gate_split(ex_3,[303]).
opt_gate_split(ex_4,[405,406,407]).
opt_gate_split(ex_5,[503]).
opt_gate_split(ex_6,[608]).
opt_gate_split(ex_7,[710]).
opt_gate_split(ex_8,[801,802]).
opt_gate_split(ex_9,[902]).
opt_gate_split(ex_10,[1004,1005]).
opt_gate_split(ex_11,[1104]).
opt_gate_split(ex_12,[1203,1204]).
opt_gate_split(ex_13,[1304,1305]).
opt_gate_split(ex_14,[1406]).

concat_bk :-
    ex_ids(Ids),
    tell('ex_bk.pl'),
    forall(member(N, Ids), concat_bk_1(N)),
    forall(member(N, Ids), concat_bk_2(N)),
    told,
    forall(member(N, Ids), print_opt_test_gates(N)).

% Convert ex_i/bk.pl to ex_bk.pl
% New gate numbers in ex_bk.pl = i * 100 + original gate number in ex_i/bk.pl
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
print_opt_test_gates(N) :-
    atomic_list_concat(['ex_', N], Src),
    atomic_list_concat([Src, '/bk.pl'], SrcPath),
    consult(SrcPath),
    opt_tests(Src, OptTests),
    findall(G1,(member(T,OptTests),out(G, T), G1 is 100 * N + G),Gs),
    format("~w.\n", [opt_gate_split(Src,Gs)]),
    unload_file(SrcPath).

test(CircuitNum, Src, Cnt) :- 
    opt_gate_split(Src, Gs),
    findall(G, (gate(G), CircuitNum is G // 100), Gates),
    select_test(Gates, [N, N1]),
    maplist(partition_sizes, Gs, Ps),
    (member([N, N1], Ps) -> Cnt = 1; Cnt = 0),
    format("Circuit No. ~w, split: ~w/~w, Optimal: ~w\n", [Src, N, N1, Cnt]),
    format("\tResult: ~w\n", [select_test(Gates, (N, N1))]),!.

test_acc :-
    ex_ids(Ids),
    findall(Cnt,    
                (member(CircuitNum,Ids),
                atomic_list_concat(['ex_',CircuitNum], Src),
                test(CircuitNum, Src, Cnt)
                ), 
            Cnts),
    sum_list(Cnts, Sum),
    length(Cnts, N),
    Acc is Sum / N,
    format("Number of tests: ~d\nNumber of passed tests: ~d\nAccuracy: ~3f", [N, Sum, Acc]).