# 0-Search

下面是一些查找相关算法的术语：

- Agent

  Agent 是一个

# 1- Knowledge

## Knowledge

### Sentence

A sentence is an assertion about the world in a knowledge representation language. A sentence is how AI stores knowledge and uses it to infer new information.   请忽略我

## Propositional Logic

- Proposition is statements about the world that can be either true or false
- Propositional logic is based on propositions

### Propositional Symbols

Proposition symbols are most often letters that are used to represent a proposition

### Logical Connectives

Logical connectives are **logical symbols** that connect propositional symbols in order to reason in a more complex way about the world.

- Not ($\neg$)
- And ($\land$)
- Or ($\lor$)
- Implication ($\rightarrow$)
- Biconditional ($\leftrightarrow$)

### Model

The model is an assignment of a truth value to every proposition. To reiterate, propositions are statements about the world that can be either true or false. However, knowledge about the world is represented in the truth values of these propositions. 

The model is the truth-value assignment that provides infomation about the world.

For example, if P: “It is raining.” and Q: “It is Tuesday.”, a model could be the following truth-value assignment: {P = true, Q = False}. However, there are more possible models in this situation (for example, {P = True, Q = True}, where it is both raining an a Tuesday). **In fact, the number of possible models is 2 to the power of the number of propositions.** In this case, we had 2 propositions, so 2²=4 possible models.

### Knowledge Base(KB)

The knowledge base is a set of sentences known by a knowledge-based agent. This is knowledge that the AI is provided about the world in the form of propositional logic sentences that can be used to make additional inferences about the world.

### Entailment ($\vDash$)

if $\alpha \vDash \beta$ ($\alpha$ entails $\beta$), then in any world where $\alpha$ is true, $\beta$ is true, too.

 Entailment is different from implication. Implication is a **logical connective** between two propositions. Entailment, on the other hand, is a **relation** that means that if all the information in α is true, then all the information in β is true.

## Inference

Inference is the process of deriving new sentences from old ones.

There are multiple ways to infer new knowledge based on existing knowledge. First, we will consider the **Model Checking** algrithm.

- To determine if KB $\vDash \alpha$ (in other words, answering the question: “can we conclude that α is true based on our knowledge base” )  
  1. Enumerate all possible models
  2. If every model where KB is true, $\alpha$ is true as well, then KB entails α (KB ⊨ α).

Consider the following example:

> P: It is a Tuesday. 
>
> Q: It is raining. 
>
> R: Harry will go for a run. 
>
> KB: (P ∧ ¬Q) → R (in words, P and not Q imply R) P (P is true) ¬Q (Q is false) 
>
> Query: R (We want to know whether R is true or false; Does KB ⊨ R?)

To answer the query using the Model Checking algorithm, we enumerate all possible models.

| P     | Q     | R     | KB   |
| ----- | ----- | ----- | ---- |
| false | false | false |      |
| false | false | true  |      |
| false | true  | false |      |
| false | true  | true  |      |
| true  | false | false |      |
| true  | false | true  |      |
| true  | true  | false |      |
| true  | true  | true  |      |

>Rememer that we say there are $2^n$ models given n propositions. 

Then, we go through every model and check whether it is true given our Knowledge Base.

First, in our KB, we know that P is true. Thus, we can say that the KB is false in all models where P is not true.

Next, similarly, in our KB, we know that Q is false. Thus, we can say that the KB is false in all models where Q is true.

Finally, we are left with two models. In both, P is true and Q is false. In one model R is true and in the other R is false. Due to (P ∧ ¬Q) → R being in our KB, we know that in the case where P is true and Q is false, R must be true. Thus, we say that our KB is false for the model where R is false, and true for the model where R is true.

then, we get:

| P     | Q     | R     | KB    |
| ----- | ----- | ----- | ----- |
| false | false | false | false |
| false | false | true  | false |
| false | true  | false | false |
| false | true  | true  | false |
| true  | false | false | false |
| true  | false | true  | true  |
| true  | true  | false | false |
| true  | true  | true  | false |

Looking at this table, there is only one model where our knowledge base is true. In this model, we see that R is also true. By our definition of entailment, if R is true in all models where the KB is true, then KB ⊨ R.

Next, we look at how knowledge and logic can be represented as code.

```python
from logic import *

# Create new classes, each having a name, or a symbol, representing each proposition.
rain = Symbol("rain")  # It is raining.
hagrid = Symbol("hagrid")  # Harry visited Hagrid
dumbledore = Symbol("dumbledore")  # Harry visited Dumbledore

# Save sentences into the KB
knowledge = And(  # Starting from the "And" logical connective, becasue each proposition represents knowledge that we know to be true.

    Implication(Not(rain), hagrid),  # ¬(It is raining) → (Harry visited Hagrid)

    Or(hagrid, dumbledore),  # (Harry visited Hagrid) ∨ (Harry visited Dumbledore).

    Not(And(hagrid, dumbledore)),  # ¬(Harry visited Hagrid ∧ Harry visited Dumbledore) i.e. Harry did not visit both Hagrid and Dumbledore.

    dumbledore  # Harry visited Dumbledore. Note that while previous propositions contained multiple symbols with connectors, this is a proposition consisting of one symbol. This means that we take as a fact that, in this KB, Harry visited Dumbledore.
    )
```

To run the Model Checking algorithm, the following information is needed:

- Knowledge Base, which will be used to draw inferences
- A query, or the proposition that we are interested in whether it is entailed by KB
- Symbols, a list of all the symbols (or atomic propositions) used (in our case, these are `rain`, `hagrid`, and `dumbledore`)
- Model, an assignment of truth and false values to symbols

The model checking algorithm looks as follows:

```python
def check_all(knowledge, query, symbols, model):

    # If model has an assignment for each symbol
    # (The logic below might be a little confusing: we start with a list of symbols. The function is recursive, and every time it calls itself it pops one symbol from the symbols list and generates models from it. Thus, when the symbols list is empty, we know that we finished generating models with every possible truth assignment of symbols.)
    if not symbols:

        # If knowledge base is true in model, then query must also be true
        if knowledge.evaluate(model):
            return query.evaluate(model)
        return True
    else:

        # Choose one of the remaining unused symbols
        remaining = symbols.copy()
        p = remaining.pop()

        # Create a model where the symbol is true
        model_true = model.copy()
        model_true[p] = True

        # Create a model where the symbol is false
        model_false = model.copy()
        model_false[p] = False

        # Ensure entailment holds in both models
        return(check_all(knowledge, query, remaining, model_true) and check_all(knowledge, query, remaining, model_false))
```

Note that we are interested only in the models where the KB is true. If the KB is false, then the conditions that we know to be true are not occurring in these models, making them irrelevant to our case.

## Knowledge Engineering

Knowledge engineering is the process of figuring out how to represent propositions and logic by AI.

## Inference Rules

Model Checking is not an efficient algorithm because it has to consider every possible model  before giving the answer (a reminder: a query is true if under all the models (truth assignments) where the KB is true, R is true as well). Inference rules allow us to generate new information based on existing knowledge without considering every possible model.

Inference rules are usually represented using a horizontal bar that seperates the top part, the premise, from the bottom part, the conclusion. The premise is whatever knowledge we have, and the conclusion is what knowledge can be generated based on the premise.

![image-20230328084702929](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328084702929.png)

Now we shall introduce some fancy inference rules.

### Modus Ponens

![image-20230328084811873](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328084811873.png)

### And Elimination

If an And proposition is true, then any one atomic proposition within it is true as well.

![image-20230328084847526](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328084847526.png)

### Double Negation Elimination

![image-20230328084919609](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328084919609.png)

### Implication Elimination

An implication is equivalent to an Or relation between the negated antecedent and the consequent. 

![image-20230328085047481](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328085047481.png)

### Biconditional Elimination

A biconditional proposition is equivalent to an implication and its inverse with an And connective. 

![image-20230328085211276](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328085211276.png)

### De Morgan’s Law

![image-20230328085434355](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328085434355.png)

### Distributive Property

![image-20230328085510044](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328085510044.png)

![image-20230328085520247](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328085520247.png)

### Knowledge and Search Problems

Inference can be viewed as a **search problem** with the following properties.

- Initial state: starting knowledge base
- Actions: inference rules
- Transition model: new knowledge base after inference
- Goal  test: checking whether the statement that we are trying to prove is in the KB
- Path cost function: the number of steps in the proof

## Resolution

Resolution is a powerful inference rule that states that if one of two atomic propositions in an Or proposition is false, the other has to be true.

![image-20230328090642435](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328090642435.png)

Resolution can be further generalized. Suppose that in addition to the proposition “Ron is in the Great Hall” Or “Hermione is in the library”, we also know that “Ron is not in the Great Hall” Or “Harry is sleeping.” We can infer from this, using resolution, that “Hermione is in the library” Or “Harry is sleeping.” To put it in formal terms:

![image-20230328090719543](C:\Users\ming\AppData\Roaming\Typora\typora-user-images\image-20230328090719543.png)

Complementary literals allow us to generate new sentences through inferences by resolution. Thus, inference algorithms locate complementary literals to generate new knowledge.



A **Clause** is a disjunction of literals (a propositional symbol or a negation of a propositional symbol, such as P, ¬P). A **disjunction** consists of propositions that are connected with an Or logical connective (P ∨ Q ∨ R). A **conjunction**, on the other hand, consists of propositions that are connected with an And logical connective (P ∧ Q ∧ R). Clauses allow us to convert any logical statement into a **Conjunctive Normal Form** (CNF), which is a conjunction of clauses, for example: (A ∨ B ∨ C) ∧ (D ∨ ¬E) ∧ (F ∨ G).

### Steps in Conversion of Proposition to Conjunctive Normal Form

- Eliminate biconditionals
  - Turn (α $\leftrightarrow$ β) into (α → β) ∧ (β → α).
- Eliminate implications
  - Turn (α → β) into ¬α ∨ β.
- Move negation inwards until only literals are being negated (and not clauses), using De Morgan’s Laws.
  - 
    Turn ¬(α ∧ β) into ¬α ∨ ¬β

Here’s an example of converting (P ∨ Q) → R to Conjunctive Normal Form:

- 
  (P ∨ Q) → R
- ¬(P ∨ Q) ∨ R /Eliminate implication
- (¬P ∧ ¬Q) ∨ R /De Morgan’s Law
- (¬P ∨ R) ∧ (¬Q ∨ R) /Distributive Law

At this point, we can run an inference algorithm on the conjunctive normal form. Occasionally, through the process of inference by resolution, we might end up in cases where a clause contains the same literal twice. In these cases, a process called **factoring** is used, where the duplicate literal is removed. For example, (P ∨ Q ∨ S) ∧ (¬P ∨ R ∨ S) allow us to infer by resolution that (Q ∨ S ∨ R ∨ S). The duplicate S can be removed to give us (Q ∨ R ∨ S).

Resolving a literal and its negation, i.e. ¬P and P, gives the **empty clause** (). The empty clause is always false, and this makes sense because it is impossible that both P and ¬P are true. This fact is used by the resolution algorithm.

- To determine if KB ⊨ α:
  - Check: is (KB ∧ ¬α) a contradiction?
    - 
      If so, then KB ⊨ α.
    - Otherwise, no entailment.

Proof by contradiction is a tool used often in computer science. If our knowledge base is true, and it contradicts ¬α, it means that ¬α is false, and, therefore, α must be true. More technically, the algorithm would perform the following actions:

- To determine if KB ⊨ α:
  - Convert (KB ∧ ¬α) to Conjunctive Normal Form.
  - Keep checking to see if we can use resolution to produce a new clause.
  - If we ever produce the empty clause (equivalent to False), congratulations! We have arrived at a contradiction, thus proving that KB ⊨ α.
  - However, if contradiction is not achieved and no more clauses can be inferred, there is no entailment.



# 2-Uncertainty

[This](https://cs50.harvard.edu/ai/2020/notes/3/) is the notes for uncertainty, it’s really nice and comprehensive.



















































