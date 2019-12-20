
def jaccard_similarity(sent1, sent2):
    union = min(len(sent1), len(sent2))
    if union == 0:
        return 0
    intersection = len(list(set(sent1).intersection(set(sent2))))
    return (intersection / union)

def are_sentences_alike(sent1, sent2, cutoff=.25):
    score = jaccard_similarity(sent1, sent2)
    return True if score > cutoff else False

def cosineValue(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/np.sqrt(sumxx*sumyy)

def get_sentence_vector(sentence, std_embeddings_index = std_embeddings_index ):
    sent_vector = 0
    for word in sentence.lower().split():
        if word not in std_embeddings_index :
            word_vector = np.array(np.random.uniform(-1.0, 1.0, 300))
            std_embeddings_index[word] = word_vector
        else:
            word_vector = std_embeddings_index[word]
        sent_vector = sent_vector + word_vector
    return sent_vector

def cosine_sim(sent1, sent2):
    global std_embeddings_index
    std_embeddings_index = {}
    with io.open("datasets/cached_embeddings.txt", "r", encoding="utf-8") as my_file:
        for line in my_file:
            values = line.split(' ')
            word = values[0]
            embedding = np.asarray(values[1:], dtype='float32')
            std_embeddings_index[word] = embedding
            
    return cosineValue(get_sentence_vector(sent1), get_sentence_vector(sent2))