# Teaching humans transferable strategy by inducing and explaining logic programs

Repository for "Teaching humans transferable strategy by inducing and explaining logic programs."

## Description

We propose a hybrid neuro-symbolic framework to generate human-interpretable explanations for improving human generalisation on unseen tasks. Our framework combines curriculum-trained ILP and LLMs. This is a concrete demonstration of Ultra-Strong Machine Learning, where the AI system teaches knowledge to humans, thereby enabling better human performance than without the AI teacher.

## Getting Started

### Dependencies

See environment.yml for details.

### Learning how to partition a circuit

We use [Hopper](hopper), a popper variant that can use second-order programs. Hopper is supplied with both first-order programs (is_connected/1, size/2, pair/3, equal/2, etc) and second-order programs (find_all/3, all/3, fold/4, map/3). 

Hopper uses language bias to declare body and head predicates, types and input-output directions. Hopper requires very few training examples (uses only 1 circuit example per task).

```
python hopper/popper.py --kbpath isolated_behind --max-ho 3 --max-rules 3
python hopper/popper.py --kbpath partition --max-ho 3 --max-rules 3
python hopper/popper.py --kbpath partition_sizes --max-rules 3
python hopper/popper.py --kbpath optimal_partition_sizes --max-ho 3 --max-rules 3
```

### Explaining the learned programs with large language models

We used open-source instruction-tuned coder models to sample explanations of code components and their overall function. We follow an instruction prompt template for Qwen2.5-coder-instruct and StarCoderv2-15b-instruct to generate responses. 

We prompt larger reasoning models (DeepSeek R1 and Claude-3.7-sonnet) to summarise explanation samples into one coherent descriptions.

## Contact
lun.ai.public@gmail.com