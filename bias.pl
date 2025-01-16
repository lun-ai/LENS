% Learn a divide and conquer strategy to partition each input graph based on test-outcome pairs

% enable_recursion.

max_body(4).
max_clause(1).

head_pred(select_test,2). 
body_pred(empty_partitions,1).
body_pred(partition_sizes,2).
body_pred(max_min_size,3).
body_pred(maplist,3,ho).
body_pred(foldl,4,ho).

type(select_test,(list,list)). 
type(empty_partitions,(list,)).
type(partition_sizes,(element,list)).
type(max_min_size,(list,list,list)).
type(maplist,((element,list),list,list)).
type(foldl,((list,list,list),list,list,list)).

direction(select_test,(in,out)). 
direction(empty_partitions,(in,)).
direction(partition_sizes,(in,out)).
direction(max_min_size,(in,in,out)).
direction(maplist,((in,out),in,out)).
direction(foldl,((in,in,out),in,in,out)).

only_once(empty_partitions).
only_once(partition_sizes).
only_once(max_min_size).
only_once(maplist).
only_once(foldl).

:-
    only_once(P),
    clause(C),
    #count{Vars : body_literal(C,P,A,Vars)} > 1.