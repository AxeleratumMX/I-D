from w2v_mimick import load_w2v_mimicking_model, vectorize
# import tensorflow as tf
import numpy as np
import time

text = '''LinkedIn, la red social que conecta profesionales, lanzó su nueva sección de noticias o “temas más comentados” con el objetivo de mantener informados a los ejecutivos de los acontecimientos o tendencias del día.
Esta herramienta, lanzada en Estados Unidos en 2017, llega a México en forma de un feed de noticias sobre los temas más comentados del día. Otra de sus metas es que los usuarios conozcan diferentes perspectivas de los temas nacionales.
Con esta innovación la plataforma se une a la tendencia de Twitter, Google y Facebook quienes poseen una sección de noticias para mantener y atraer de manera distinta a sus usuarios.'''

text2 = '''Jesusa Rodríguez (Ciudad de México, 1955) compara el Senado mexicano con un teatro, un espacio que conoció bien durante más de 40 años de carrera como directora, actriz, artista de performance y cabaretera. “Este es un teatro político con actores, escenografía, textos y toda la puesta en escena está pensada”, dice la legisladora, quien llegó a la Cámara alta en diciembre cuando la titular del escaño, Olga Sánchez Cordero, fue designada secretaria de Gobernación (Interior) en la Administración de Andrés Manuel López Obrador. 
Rodríguez, quien acostumbra vestir con trajes de algodón decorados con bordados indígenas, es uno de los perfiles progresistas del plural Movimiento de Regeneración Nacional (Morena). Es vegana, ecologista, feminista y defensora de los derechos de la comunidad LGBT. “Es el siglo de la liberación animal”, asegura durante la entrevista. Un mensaje suyo publicado en las redes sociales el 15 de marzo provocó polémica al recordar la conquista que impuso la religión católica “a sangre y fuego por fanáticos que venían a depredar el territorio y la cultura”. Conocedora del mundo del espectáculo, aguzó su video diciendo que comer tacos de carnitas de cerdo, uno de los platos típicos de México, era celebrar la caída de Tenochtitlan, la gran ciudad azteca que capituló en agosto de 1521. El comentario fue antesala de la polémica causada por el presidente mexicano, quien pidió a la Corona española reconocer los agravios de la conquista para conmemorar cinco siglos de la fecha.'''


print('Loading model...')
start_time = time.time()
model = load_w2v_mimicking_model(
    wordvectors_file_vec = 'Mimicking/wiki.es.vec',
    w2v_limit=100,
    best_epoch=200)
    
end_time = time.time()
print('0. Model loaded in %s sec' % (end_time - start_time))

print('Embedding text of %d characters...' % len(text))
start_time = time.time()
paragraphs = vectorize(model, text)
end_time = time.time()
print('1. Text embedding in %s secs' % (end_time - start_time))

# for paragraph in paragraphs:
#     print(paragraph.shape)


print('Embedding text of %d characters...' % len(text2))
start_time = time.time()
paragraphs = vectorize(model, text2)
end_time = time.time()
print('2. Text embedding in %s secs' % (end_time - start_time))

# for paragraph in paragraphs:
#     print(paragraph.shape)
