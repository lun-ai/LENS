:- ['bk.pl'].

optimal_partition_sizes(A,B):- empty_partition_sizes(C),map(partition_sizes,A,D),fold(larger_min_size,C,D,B).