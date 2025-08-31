world_check(X,A):-
    nonvar(A),
    member(X,A),!.
world_replace(X,Y,A,B):-
    nonvar(A),
    nonvar(B),!,
    append(Prefix,[X|Suffix],A),
    append(Prefix,[Y|Suffix],B),!.
world_replace(X,Y,A,B):-
    nonvar(A),
    append(Prefix,[X|Suffix],A),
    append(Prefix,[Y|Suffix],B),!.

order_leq(A,B):-A=<B.
order_gt(A,B):-A>B.

lexi_order([0,1,2,3,4,5,6,7,8,9,
            10,11,12,13,14,15,16,17,18,19,
            20,21,22,23,24,25,26,27,28,29,
            30,31,32,33,34,35,36,37,38,39,
            40,41,42,43,44,45,46,47,48,49,
            50,51,52,53,54,55,56,57,58,59,
            60,61,62,63,64,65,66,67,68,69,
            70,71,72,73,74,75,76,77,78,79,
            80,81,82,83,84,85,86,87,88,89,
            90,91,92,93,94,95,96,97,98,99,
            100,101,102,103,104,105,106,107,108,109,
            110]).
compute_spearman(State,C):-
    world_check(left_bag(L),State),
    L \= [],!,
    world_check(right_bag(R),State),
    world_check(memory([H|T]),State),
    world_check(expr(Exprs),State),
    append([H|L],R,Values),
    create_exprs(Values,[Expr],"<"),
    reverse([Expr|T],M),
    append(M,Exprs,Exprs1),
    compute_spearman(Exprs1,C).
compute_spearman(State,C):-
    world_check(right_bag(R),State),
    R \= [],!,
    world_check(left_bag(L),State),
    world_check(memory([H|T]),State),
    world_check(expr(Exprs),State),
    append([H|L],R,Values),
    create_exprs(Values,[Expr],"<"),
    reverse([Expr|T],M),
    append(M,Exprs,Exprs1),
    compute_spearman(Exprs1,C).
compute_spearman(State,C):-
    world_check(memory([]),State),!,
    world_check(expr(Exprs),State),
    compute_spearman(Exprs,C).
compute_spearman(State,C):-
    world_check(memory([H|T]),State),
    world_check(expr(Exprs),State),
    reverse([H|T],M),
    append(M,Exprs,Exprs1),!,
    compute_spearman(Exprs1,C).
compute_spearman(Exprs,C):-
    lexi_order(Order),
    exprs_to_ints(Exprs,Ints),
    findall(Num,(member(Num,Order),member(Num,Ints)),LocalOrder),
    spearman_rank(Ints,LocalOrder,1,SumXY,SumX,SumY,_,_,Length),
    C is Length*SumXY-SumX*SumY.

spearman_rank([],_,_,0,0,0,0,0,0).
spearman_rank([H|T],L,Rank,SumXY,SumX,SumY,SumXSq,SumYSq,Size):-
    nth1(R,L,H),!,
    square(R,RS),
    square(Rank,RankS),
    Rank1 is Rank+1,
    spearman_rank(T,L,Rank1,SumXY1,SumX1,SumY1,SumXSq1,SumYSq1,Size1),
    SumX is SumX1+Rank,
    SumXSq is SumXSq1+RankS,
    SumY is SumY1+R,
    SumYSq is SumYSq1+RS,
    SumXY is Rank*R+SumXY1,
    Size is Size1+1.

square(X,Y):-
    Y is X*X.

term_order(spearman,A,B):-
    compute_spearman(A,C1),
    compute_spearman(B,C2),
    C1 =< C2.

increment_energy(A,B,Amount):-
    world_check(energy(E1),A),
    E2 is E1+Amount,
    world_replace(energy(E1),energy(E2),A,B).

record_energy(A,Amount):-
    world_check(energy(Amount),A).

extend_expr("",Expr,Expr):-!.
extend_expr(Expr,Expr1,Expr2):-
    atomics_to_string([Expr,Expr1],"<",Expr2).

compare_nums(A,B):-
    world_check(left_bag([H1|T1]),A),
    world_check(right_bag([H2|_]),A),
    world_check(memory([Seq|Seqs]),A),
    string_2_int(H1,V1),
    string_2_int(H2,V2),
    order_leq(V1,V2),
    extend_expr(Seq,H1,Seq1),
    world_replace(left_bag(_),left_bag(T1),A,C),
    world_replace(memory(_),memory([Seq1|Seqs]),C,D),
    increment_energy(D,B,1).
compare_nums(A,B):-
    world_check(left_bag([H1|_]),A),
    world_check(right_bag([H2|T2]),A),
    world_check(memory([Seq|Seqs]),A),
    string_2_int(H1,V1),
    string_2_int(H2,V2),
    order_gt(V1,V2),
    extend_expr(Seq,H2,Seq1),
    world_replace(right_bag(_),right_bag(T2),A,C),
    world_replace(memory(_),memory([Seq1|Seqs]),C,D),
    increment_energy(D,B,1).

drop_bag_remaining(A,B):-
    world_check(left_bag([]),A),!,
    world_check(right_bag(R),A),
    world_check(memory([Seq|Seqs]),A),
    atomics_to_string([Seq|R],"<",Seq1),
    world_replace(right_bag(_),right_bag([]),A,C),
    world_replace(memory(_),memory([Seq1|Seqs]),C,B).
drop_bag_remaining(A,B):-
    world_check(right_bag([]),A),!,
    world_check(left_bag(L),A),
    world_check(memory([Seq|Seqs]),A),
    atomics_to_string([Seq|L],"<",Seq1),
    world_replace(left_bag(_),left_bag([]),A,C),
    world_replace(memory(_),memory([Seq1|Seqs]),C,B).

parse_exprs(A,B):-
    world_check(left_bag([]),A),
    world_check(right_bag([]),A),
    world_check(memory(M),A),
    world_check(expr([Expr1,Expr2|Exprs]),A),
    world_replace(expr(_),expr(Exprs),A,C),
    split_string(Expr1,"<","",Values1),
    split_string(Expr2,"<","",Values2),
    world_replace(left_bag(_),left_bag(Values1),C,D),
    world_replace(right_bag(_),right_bag(Values2),D,E),
    world_replace(memory(_),memory([""|M]),E,B).

recycle_memory(A,B):-
    world_check(expr(Exprs),A),
    Exprs \= [_,_|_],
    world_check(memory(M),A),
    M \= [],
    reverse(M,M1),
    append(M1,Exprs,Exprs1),
    world_replace(memory(_),memory([]),A,C),
    world_replace(expr(_),expr(Exprs1),C,B).

single_expr(A,A):-
    world_check(expr([_]),A),
    world_check(memory([]),A),
    world_check(left_bag([]),A),
    world_check(right_bag([]),A).