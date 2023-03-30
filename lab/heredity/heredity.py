import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    #print(joint_probability(people, {}, {"Lily", "James", "Harry"}, {"Harry", "James"}))
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    def findGene(parent):
        if parent in one_gene:
            rt = 1
        elif parent in two_genes:
            rt = 2
        else:
            rt = 0
        return rt
    
    def fromParents(fatherGene, motherGene, expectGene):
        prob_mutation = PROBS["mutation"]
        def fromAgetB(fromA, getB):
            if fromA == 0:
                if getB == 0:
                    rt = 1 - prob_mutation
                elif getB == 1:
                    rt = prob_mutation
            elif fromA == 1:
                if getB == 0:
                    rt = 1/2
                elif getB == 1:
                    rt = 1/2
            elif fromA == 2:
                if getB == 0:
                    rt = prob_mutation
                elif getB == 1:
                    rt = 1 - prob_mutation
            return rt
        if expectGene == 0:
            rt = fromAgetB(fatherGene, 0) * fromAgetB(motherGene, 0)
        elif expectGene == 1:
            rt = fromAgetB(fatherGene, 1) * fromAgetB(motherGene, 0) + fromAgetB(fatherGene, 0) * fromAgetB(motherGene, 1)
        elif expectGene == 2:
            rt = fromAgetB(fatherGene, 1) * fromAgetB(motherGene, 1)
        return rt
    
    names = people.keys()
    #unknown_trait = have_trait.copy()
    unknown_trait = have_trait
    # for p in have_trait:
    #     if people[p]["trait"] == False:
    #         return 0
    #     if people[p]["trait"] == True:
    #         unknown_trait.remove(p)
    unknown_untrait = names - have_trait 
    # for p in names - have_trait:
    #     if people[p]["trait"] == True:
    #         return 0
    #     if people[p]["trait"] == False:
    #         unknown_untrait.remove(p)

    joint_prob = 1
    
    for p in one_gene:
        if people[p]["mother"] is None:
            joint_prob *= PROBS["gene"][1]
            # print(f"1:{joint_prob}")
        else:
            fatherGene = findGene(people[p]["father"])
            motherGene = findGene(people[p]["mother"])
            joint_prob *= fromParents(fatherGene, motherGene, 1)
            # print(f"2:{joint_prob}")
    for p in two_genes:
        if people[p]["mother"] is None:
            joint_prob *= PROBS["gene"][2]
            # print(f"3:{joint_prob}")
        else:
            fatherGene = findGene(people[p]["father"])
            motherGene = findGene(people[p]["mother"])
            joint_prob *= fromParents(fatherGene, motherGene, 2)
            # print(f"4:{joint_prob}")
    for p in names - one_gene - two_genes:
        if people[p]["mother"] is None:
            joint_prob *= PROBS["gene"][0]
            # print(f"5:{joint_prob}")
        else:
            fatherGene = findGene(people[p]["father"])
            motherGene = findGene(people[p]["mother"])
            joint_prob *= fromParents(fatherGene, motherGene, 0)
            # print(f"6:{joint_prob}")
    for p in unknown_trait:
        if p in one_gene:
            joint_prob *= PROBS["trait"][1][True]
            # print(f"7:{joint_prob}")
        elif p in two_genes:
            joint_prob *= PROBS["trait"][2][True]
            # print(f"8:{joint_prob}")
        else:
            joint_prob *= PROBS["trait"][0][True]
            # print(f"9:{joint_prob}")
        
    for p in unknown_untrait:
        if p in one_gene:
            joint_prob *= PROBS["trait"][1][False]
            # print(f"10:{joint_prob}")
        elif p in two_genes:
            joint_prob *= PROBS["trait"][2][False]
            # print(f"11:{joint_prob}")
        else:
            joint_prob *= PROBS["trait"][0][False]
            # print(f"12:{joint_prob}")
        
    return joint_prob   
        

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.

    """
    names = probabilities.keys()
    for p_ in have_trait:
        probabilities[p_]["trait"][True] += p
    for p_ in names - have_trait:
        probabilities[p_]["trait"][False] += p
    for p_ in one_gene:
        probabilities[p_]["gene"][1] += p
    for p_ in two_genes:
        probabilities[p_]["gene"][2] += p
    for p_ in names - one_gene - two_genes:
        probabilities[p_]["gene"][0] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).

    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    """
    for p in probabilities:
        _sum = 0
        for g in probabilities[p]["gene"]:
            _sum += probabilities[p]["gene"][g]
        alpha = 1/_sum
        for g in probabilities[p]["gene"]:
            probabilities[p]["gene"][g] *= alpha
        
        _sum = 0
        for t in probabilities[p]["trait"]:
            _sum += probabilities[p]["trait"][t]
        alpha = 1/_sum
        for t in probabilities[p]["trait"]:
            probabilities[p]["trait"][t] *= alpha
        

if __name__ == "__main__":
    main()
