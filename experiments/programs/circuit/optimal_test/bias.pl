% Predicate declarations
head_pred(optimal_test,2). 
body_pred(optimal_partition_sizes,2). 
body_pred(partition_sizes,2). 
body_pred(gate,1).
body_pred(test_point_label,2).

% Types
type(optimal_test,(list,element)). 
type(optimal_partition_sizes,(list,list)). 
type(partition_sizes,(element,list)). 
type(gate,(element,)).
type(test_point_label,(element,element)).

% Input-output signatures
direction(optimal_test,(in,out)). 
direction(optimal_partition_sizes,(in,out)). 
direction(partition_sizes,(in,out)). 
direction(gate,(out,)).
direction(test_point_label,(in,out)).

% Turn off invented predicates in HO
:- invented_ho_used(_,_).