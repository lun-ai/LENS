:- ['bk.pl'].

optimal_partition_sizes(A,B):- empty_partition_sizes(D),map(partition_sizes,A,C),fold(larger_min_size,D,C,B).