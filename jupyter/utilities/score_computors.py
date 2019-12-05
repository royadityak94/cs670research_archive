
def jaccard_similarity(sent1, sent2):
    union = min(len(sent1), len(sent2))
    if union == 0:
        return 0
    intersection = len(list(set(sent1).intersection(set(sent2))))
    return (intersection / union)

def are_sentences_alike(sent1, sent2, cutoff=.25):
    score = jaccard_similarity(sent1, sent2)
    return True if score > cutoff else False

