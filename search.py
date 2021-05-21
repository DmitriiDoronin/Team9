import numpy as np
def cosine_similarity(vec1, vec2):
    '''
        This function returns the cosine similarity of 2 vectors.
    :param vec1: np.array
        The first vector.
    :param vec2: np.array
        The second vector.
    :return: float
        The cosine similarity of the 2 vectors.
    '''
    # Getting the dot product of the 2 values.
    dot_product = np.dot(vec1, vec2.T)
    print(vec1)

    # Getting the norm of every vector.
    norm1 = np.linalg.norm(vec1, ord=2)
    norm2 = np.linalg.norm(vec2, ord=2)

    # Computing and returning the cosine similarity.
    return dot_product / (norm1 * norm2)

def find_top_n(vec, matrix, n=5):
    '''
        This function returns the indexes of the most similar resumes.
    :param vec: np.array
        The vector representation of the query.
    :param matrix: sparse matrix
        The sparse matrix of the vectorised resumes.
    :param n: int
        The number results to return.
    :return: np.array
        The top n indexes with the most similar resumes.
    '''
    # Creating an empty list to store the cosine similarities.
    cos_sim = []
    print('vec')
    print(vec)

    print('metrix')
    print(matrix)
    # Computing the cosine similarity of every resume with the vector representation of the query.
    for i in range(len(matrix.toarray())):
        cos_sim.append(cosine_similarity(vec, matrix[i].toarray())[0])
    # Returning the n most similar indexes.
    return np.argsort(cos_sim)[-n:]
