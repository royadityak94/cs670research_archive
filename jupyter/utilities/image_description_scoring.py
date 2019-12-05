from nltk.corpus import wordnet

def extract_synonyms(item, max_recursion=4):
    synonyms = list(set([(lemma.name().lower()) for synset in wordnet.synsets(item) for lemma in synset.lemmas()]))
    
    for i in range(max_recursion):
        new_list = []
        for synonym in synonyms:
            new_list.extend([(lemma.name().lower()) for synset in wordnet.synsets(synonym) for lemma in synset.lemmas()])
        
        synonyms.extend(new_list)
        synonyms = list(set(synonyms))
    return synonyms

def get_all_synonyms(item_list, max_recursion=4):
    synonyms = [item for item in item_list]
    for item in item_list:
        synonyms.extend(extract_synonyms(item, max_recursion))
    return synonyms

def matching_label_score(detected, actual, max_depth=4):
    total_cnt = 0
    actual_synonyms = get_all_synonyms(actual, max_depth)
    for item in detected: 
        if item in actual_synonyms:
            total_cnt += 1
            continue
        else:
            all_synonyms = get_all_synonyms([item], max_depth)
            for synonym in all_synonyms:
                if synonym in actual_synonyms:
                    total_cnt += 1
                    break
    return min(1, total_cnt/len(actual))