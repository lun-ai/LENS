:- ['optimal_partition_sizes/target.pl'].
:- use_module(library(csv)).

% Id for each circuit example
ex_ids([1,2,3,4,5,6,7,8,9,10,11,12,13,14]).

% Optimal tests for each circuit example
opt_tests(ex_intro_0, ['c','d']).
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

opt_gates(ex_intro_0,[3,4]).
opt_gates(ex_1,[104]).
opt_gates(ex_2,[203,204]).
opt_gates(ex_3,[303]).
opt_gates(ex_4,[405,406,407]).
opt_gates(ex_5,[503]).
opt_gates(ex_6,[608]).
opt_gates(ex_7,[710]).
opt_gates(ex_8,[801,802]).
opt_gates(ex_9,[902]).
opt_gates(ex_10,[1004,1005]).
opt_gates(ex_11,[1104]).
opt_gates(ex_12,[1203,1204]).
opt_gates(ex_13,[1304,1305]).
opt_gates(ex_14,[1406]).


% Combine all circuit BK into one
combine_bk :-
    ex_ids(Ids),
    tell('ex_bk.pl'),
    forall(member(N, Ids), combine_bk_1(N)),
    forall(member(N, Ids), combine_bk_2(N)),
    told,
    forall(member(N, Ids), print_opt_test_gates(N)).


% Convert ex_i/bk.pl to ex_bk.pl
% New gate numbers in ex_bk.pl = i * 100 + original gate number in ex_i/bk.pl
combine_bk_1(N) :-
    atomic_list_concat(['ex_', N, '/bk.pl'], SrcPath),
    consult(SrcPath),
    forall(gate(G), (NewG is N * 100 + G, write(gate(NewG)), writeln('.'))),
    unload_file(SrcPath).
combine_bk_2(N) :-
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
    format("~w.\n", [opt_gates(Src,Gs)]),
    unload_file(SrcPath).


% Create pos and neg examples of local optimal partition sizes
write_test_ex :-
    ex_ids(Ids),
    tell('test/exs.pl'),
    forall(member(CircuitNum, Ids), 
            (atomic_list_concat(['ex_', CircuitNum], Src),
            write_test_pos(CircuitNum, Src))),
    forall(member(CircuitNum, Ids), 
            (atomic_list_concat(['ex_', CircuitNum], Src),
            write_test_neg(CircuitNum, Src))),
    told.
write_test_pos(CircuitNum, Src) :-
    findall(G, (gate(G), CircuitNum is G // 100), Gates),
    opt_gates(Src, OptGates),
    maplist(partition_sizes, OptGates, OptPs),
    sort(OptPs,OptPsSorted),
    forall(member(Pos, OptPsSorted), format("pos(optimal_partition_sizes(~w,~w)).\n", [Gates, Pos])).
write_test_neg(CircuitNum, Src) :-
    findall(G, (gate(G), CircuitNum is G // 100), Gates),
    maplist(partition_sizes, Gates, Ps),
    sort(Ps,PsSorted),
    opt_gates(Src, OptGates),
    maplist(partition_sizes, OptGates, OptPs),
    subtract(PsSorted, OptPs, Diffs),
    forall(member(Neg, Diffs), format("neg(optimal_partition_sizes(~w,~w)).\n", [Gates, Neg])).


% Check the partition selected by the learned program
test(CircuitNum, Src, Cnt) :- 
    opt_gates(Src, Gs),
    findall(G, (gate(G), CircuitNum is G // 100), Gates),
    optimal_partition_sizes(Gates, [N, N1]),
    maplist(partition_sizes, Gs, Ps),
    (member([N, N1], Ps) -> Cnt = 1; Cnt = 0),
    format("Circuit No. ~w, split: ~w/~w, Optimal: ~w\n", [Src, N, N1, Cnt]),
    format("\tResult: ~w\n", [optimal_partition_sizes(Gates, (N, N1))]),!.
test_selection :-
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


% Compute the log base and compute the entropy
log_base(Base,N,Log) :-
        Log is log(N) / log(Base).
entropy([0,_], 0) :- !.
entropy([_,0], 0) :- !.
entropy([A,B], Entropy) :-
    Prob is A / (A + B),
    log_base(2, Prob, LogProb),
    log_base(2, 1 - Prob, Log1Prob),
    Entropy is -Prob * LogProb - (1 - Prob) * Log1Prob.
compute_entropy_(CircuitNum, Ents) :-
    findall(G, (gate(G), CircuitNum is G // 100), Gates),
    maplist(partition_sizes, Gates, Ps),
    maplist(entropy, Ps, Ents).


% Compute the entropy of the partitions for each circuit and write to a csv file
compute_entropy :-
    ex_ids(Ids),
    tell('data/partition_to_entropy.csv'),
    print_list([a,b,c,d,e,f,g,h,i,j]),nl,
    forall(member(CircuitNum,Ids),
                (
                atomic_list_concat(['ex_',CircuitNum], Src),
                write(Src),
                compute_entropy_(CircuitNum, Ents),
                print_list(Ents),
                nl
                )),
    told.


% Print the list elements
print_list([]).
print_list([H|T]) :-
    format(",~w", [H]),
    print_list(T).

test_ex(A) :-
    call(A).


% Test the accuracy of the learned program on test examples
:-
    unload_file('ex_1/bk.pl'),
    consult('circuit_bk.pl'),
    consult('data/exs.pl'),
    % consult('ex_5/bk.pl'),
    % consult('isolated/exs.pl'),
    findall(A, (pos(A); neg(A)), Es),
    findall(A, (pos(A), test_ex(A)), Ps_),
    findall(A, (neg(A), not(test_ex(A))), Ns_),
    findall(A, (pos(A), not(test_ex(A))), FN_),
    findall(A, (neg(A), test_ex(A)), FP_),
    sort(Ps_, Ps),
    sort(Ns_, Ns),
    length(Es, EN),
    length(Ps, PN),
    length(Ns, NN),
    sort(FP_,FP),
    sort(FN_,FN),
    Acc is (PN + NN) / EN,
    format("Number of tests: ~d\nNumber of passed pos/neg tests: ~d/~d\nAccuracy: ~3f\nFP: ~w\nFN: ~w", [EN, PN, NN, Acc, FP, FN]).