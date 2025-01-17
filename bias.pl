% Learn a divide and conquer strategy to partition each input graph

max_body(4).

head_pred(select_test,2). 
body_pred(empty_partitions,1).
body_pred(partition_sizes,2).
body_pred(max_min_size,3).
body_pred(map,3,ho).
body_pred(fold,4,ho).

type(select_test,(list,list)). 
type(empty_partitions,(list,)).
type(partition_sizes,(element,list)).
type(max_min_size,(list,list,list)).
type(map,((element,list),list,list)).
type(fold,((list,list,list),list,list,list)).

direction(select_test,(in,out)). 
direction(empty_partitions,(out,)).
direction(partition_sizes,(in,out)).
direction(max_min_size,(in,in,out)).
direction(map,((in,out),in,out)).
direction(fold,((in,in,out),in,in,out)).