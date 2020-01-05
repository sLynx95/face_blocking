import numpy as np


def get_faces_embedding(faces, model):
    # convert each face to an embedding
    embeddings = []
    for face in faces:
        embedding = get_face_embedding(face, model)
        embeddings.append(embedding)
    return np.asarray(embeddings)


def get_face_embedding(face, model):
    # scale pixel values
    face = face.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face.mean(), face.std()
    face = (face - mean) / std
    # transform face into one sample
    samples = np.expand_dims(face, axis=0)
    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]
