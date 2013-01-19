'''
This module uses topic models to make relevant-project suggestions.

from gensim import similarities
from tm.modeler import build_lda_topic_model, get_truonex_data
data, dictionary, model = build_lda_topic_model(no_below=10, no_above=0.25, keep_n=1000, num_topics=24)
td = get_truonex_data(data)
corpus = [dictionary.doc2bow(item['text']) for item in td.values()]
index = similarities.MatrixSimilarity(model[corpus])
project_id = 'ml-2593'

ps.make_project_suggestions(data, dictionary, model, index, project_id)
'''
from gensim import similarities

def make_suggestions(data, dictionary, model, num_suggestions=20, threshold=.75, handler=None):
    corpus = [dictionary.doc2bow(item['text']) for item in data.values()]
    index = similarities.MatrixSimilarity(model[corpus])
    for project_id in data.keys():
        make_project_suggestions(data, dictionary, model, index, project_id)
        
def make_project_suggestions(data, dictionary, model, index, project_id, num_suggestions=20, threshold=.7):
    print project_id
    doc = data[project_id]['text']
    bow = dictionary.doc2bow(doc)
    vec = model[bow]
    results = [item for item in enumerate(index[vec]) if item[1]>= threshold and not data.values()[item[0]]['id'] == project_id]
    results = sorted(results, key=lambda item: -item[1])[:num_suggestions]
    return [(data.values()[item[0]]['id'], item[1]) for item in results]
 