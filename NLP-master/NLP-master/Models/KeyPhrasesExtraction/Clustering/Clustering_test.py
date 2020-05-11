import numpy as np
from numpy.linalg import norm

from SentenceEmbedding import Model
#from AroraSentenceEmbedding import Model
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, AffinityPropagation
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import CustomJS, Div
from bokeh import events
from bokeh.models import HoverTool, ResetTool, BoxSelectTool
from bokeh.layouts import column, row
from bokeh.palettes import Category10
from bokeh.models.widgets import TextInput, TextAreaInput


def main():
    """ Generate sample data and apply DBSCAN clustering """

    #embedding:

    model = Model()
    # sentences = [
    #     "Minatitlán.",
    #     "Al entrar hoy en operaciones la primera coordinación de la Guardia Nacional en este municipio veracruzano, elementos del Ejército y de la Policía Federal, portando la insignia de la nueva corporación, montaron operativos de revisión en diversas calles, además de realizar patrullajes.",
    #     "Aún con sus uniformes castrenses y policiacos, en cada caso, efectúan revisiones en vehículos y verifican documentos de choferes.",
    #     "Sobre la avenida Benito Juárez, colonia Cerro Alto, sobre todo en camionetas y taxis.",
    #     "En su conferencia mañanera, el Presidente Andrés Manuel López Obrador anunció el arranque de la Guardia Nacional en este municipio, con la primera coordinación, de 266 que habrá en el país.",
    #     "Luego se hará lo propio en Salina Cruz y Coatzacoalcos, en el sur de la entidad, así como en Cancún, Quintana Roo, puntos en los que se requiere con más urgencia a la corporación, dijo.",
    #     "Antes de viajar a ese municipio, en el inicio de una gira por la región del Istmo de Tehuantepec, dijo que aunque todavía no hay leyes secundarias, la reforma constitucional permite al gobierno iniciar con la instalación de bases para la guardia.",
    #     "Entonces, la primera que se establece ya con el número de elementos suficientes con mando único va a ser la de Minatitlán, el día de hoy, señaló en la conferencia de prensa matutina en la que estuvo acompañado por el secretario de la Defensa Nacional, Luis Cresencio Sandoval, y el titular de la Secretaría de Comunicaciones y Transportes, entre otros.",
    #     "Agradeció en ese punto a los legisladores que convocarán a un periodo extraordinario de sesiones para la aprobación de las leyes secundarias para la Guardia Nacional.",
    #     "Pero sí, en efecto, hoy se va a dar a conocer la estrategia de seguridad en Mitatitlán, que es la primera coordinación.",
    #     "Y también en Minatitlán vamos a dar respuesta a la demanda de seguridad.",
    #     "Me va a acompañar el gabinete de seguridad y se va a presentar un plan para proteger a la población en el marco del funcionamiento de la Guardia Nacional",
    #     "Señaló que la visita de hoy al sur de Veracruz ya estaba programada desde antes de los sucesos lamentables en Minatitlán (el viernes 19 de abril un grupo armado mató a 13 personas que se hallaban en una fiesta).",
    #     "El encuentro de hoy, comentó, es con todo el pueblo, en la plaza pública y desde luego vamos a expresar nuestro más sentido pésame, ya lo hemos hecho, a los familiares de las víctimas.",
    #     "Y vamos a eso, a que se investigue, se castigue a los responsables y haya justicia.",
    #     "Por eso, agregó, la reunión que tenía como propósito original los programas de Bienestar se amplía y ahora se va a tratar también el tema de la violencia y lo que se está haciendo al respecto.",
    #     "El mandatario irá el sábado a Coatzacoalcos, Veracruz y Salina Cruz, así como Matías Romero y Juchitán, Oaxaca, para revisar las obras del Tren Transítsmico, así como todo el proyecto social en la región.",
    # ]
    # sentences = [
    #     'Madrid. ',
    #     'El presidente venezolano, Nicolás Maduro, encabezó este jueves una marcha junto a miles de miembros de la Fuerza Armada Nacional Bolivariana (FANB), con la que ha querido poner de manifiesto el respaldo del que goza en el estamento militar tras el intento de alzamiento al que convocó el líder opositor Juan Guaidó.',
    #     'El mandatario apela a la FANB, a la cohesión y la unión en torno a la Constitución, la paz y la democracia venezolanas.',
    #     '"Ante el mundo esta FANB tiene que dar una lección histórica en este momento, de que en Venezuela hay una Fuerza Armada consecuente, legal, cohesionada, unida como nunca antes, derrotando intentonas golpistas de traidores que se venden a los dólares de Washington", sostuvo.',
    #     'La marcha partió del Fuerte Tiuna, en Caracas, y, según la agencia oficial AVN, junto a Maduro y el ministro de Defensa, Vladimir Padrino, participan más de cuatro mil 500 efectivos de la FANB.',
    #     'El objetivo de la misma es, según AVN, ratificar la lealtad de la FANB a la patria, a la Constitución, a la democracia y a la defensa de la paz, así como su reconocimiento de Maduro como presidente del país y comandante en jefe de la misma.',
    #     'Esta demostración de fuerza se produce después de que el martes Guaidó asegurara que contaba con el respaldo de buena parte del estamento militar tras anunciar el inicio de la llamada Operación Libertad para acabar con la "usurpación" del poder por parte de Maduro.',
    #
    # ]
    # sentences = [
    #     'Con la intención de avalar lo más pronto posible la reforma educativa, el presidente de la Comisión Permanente del Congreso, Martí Batres (Morena), informó que la primera sesión de ésta, será el próximo lunes 6 de mayo, y no el 8, como se había planteado en un inició con la intención de resolver que el periodo extraordinario arranque esa semana y no a partir de 14 mayo, como se había acordado.',
    #     'En conferencia de prensa, Batres Guadarrama indicó que en una reunión donde estuvo presente diputados y senadores de las diversas fracciones, acordaron convocar con anticipación, por lo que a las 12 horas del próximo lunes 6 de mayo, se reunirá la Mesa Directiva, y a las 13 horas, comenzará la sesión.',
    #     '“Analizamos la fecha para la que convocamos a la primera sesión de la Comisión Permanente, que fue el 8 de mayo, y resolvimos convocar con anticipación para el día lunes 6 de mayo.',
    #     'El único punto a tratar el lunes en la Permanente, será la convocatoria al periodo extraordinario.',
    #     'Esa es la resolución que ha tomado la Mesa Directiva el día de hoy”, externó.',
    #     'Batres indicó que no se puede afirmar que el extraordinario sea el 8 de mayo, pues falta que lo resuelvan los coordinadores, además de que para que ello suceda, se debe aprobar en el pleno por las dos terceras partes de los legisladores presentes.',
    #     '“Esto aún no es un acuerdo, es una posibilidad y, en su caso, tendría que ser resuelto por la Comisión Permanente.',
    #     'La convocatoria al extraordinario tiene que ser resuelta por dos terceras partes de los votos en la Comisión Permanente.',
    #     'Por lo tanto, esto ameritará acuerdos y acercamientos entre los grupos parlamentarios, que se están dando en estos momentos, a fin de lograr el primer extraordinario”, detalló.',
    # ]
    sentences=["Con la intención de avalar lo más pronto posible la reforma educativa el presidente de la Comisión Permanente del Congreso Martí Batres ( Morena ) informó la primera sesión de ésta será el próximo lunes 6 de mayo ",
"En conferencia de prensa Batres Guadarrama indicó en una reunión donde estuvo presente diputados acordaron convocar con anticipación por lo que a las 12 horas del próximo lunes 6 de mayo se reunirá la Mesa Directiva ",
"Analizamos la fecha para la que convocamos a la primera sesión de la Comisión Permanente que fue el 8 de mayo ",
"El único punto a tratar el lunes en la Permanente será la convocatoria al periodo extraordinario ",
"Esa es la resolución que ha tomado la Mesa Directiva el día de hoy ” externó ",
"Batres indicó no se puede afirmar el extraordinario sea el 8 de mayo falta lo resuelvan los coordinadores además de para ello suceda se debe aprobar en el pleno por las dos terceras partes de los legisladores presentes ",
"Esto aún no es un acuerdo es una posibilidad ",
"Por lo tanto esto ameritará acuerdos entre los grupos parlamentarios que se están dando en estos momentos a fin de lograr el primer extraordinario detalló",
"no el 8 se había planteado en un inició con la intención de resolver el periodo extraordinario arranque esa semana",
"senadores de las diversas fracciones",
"a las 13 horas comenzará la sesión",
"resolvimos convocar con anticipación para el día lunes 6 de mayo",
"en su caso tendría",
"La convocatoria al extraordinario ser resuelta por dos terceras partes de los votos en la Comisión Permanente",]
    vecs = model.sentence_to_vector(sentences)
    X = np.array([x["feature_vector"] for x in vecs])

    cluster = clustering(X)
    draw_bokeh(X, cluster, sentences)


def clustering(X, normalize=False):

    X_cluster = X

    if normalize:
        X_cluster = StandardScaler().fit_transform(X)

    af = AffinityPropagation().fit(X_cluster)

    #cluster_centers_indices = af.cluster_centers_indices_
    #cluster_centers_ = af.cluster_centers_
    #labels = af.labels_
    #n_clusters_ = len(cluster_centers_indices)
    #print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, metric='sqeuclidean'))

    return af


def draw_bokeh(X, cluster, sentences):
    """Dimension reduction with PCA and plotting with bokeh """

    X_reduced = PCA(n_components=2).fit_transform(X)

    colors = [Category10[10][i % 10] for i in cluster.labels_]
    sizes = np.ones(len(X)) * 10
    sizes[cluster.cluster_centers_indices_] = 20

    source = ColumnDataSource(
        data=dict(
            eigenv1=[x[0] for x in X_reduced],
            eigenv2=[x[1] for x in X_reduced],
            s=sentences,
            c=colors,
            size=sizes,
        )
    )

    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "@eigenv1, @eigenv2)"),
            ("s", "@s")
        ]
    )

    p = figure(title="reforma_educativa", tools=[hover, ResetTool(), BoxSelectTool()])
    p.toolbar.logo = None
    p.xaxis.axis_label = '1st eigenv'
    p.yaxis.axis_label = '2nd eigenv'
    p.scatter('eigenv1', 'eigenv2', size='size', fill_color='c',  fill_alpha=1, line_color='c',
              nonselection_fill_color="c",
              nonselection_fill_alpha=0.5, source=source)

    div = Div(width=600)

    text_input = TextAreaInput(title="Text: ", rows=50, max_length=2000)

    layout = row(p, div, text_input)


    source.callback = CustomJS(args=dict(source=source, div=div, sentences=sentences, colors=colors), code="""
            var inds = source.selected.indices
            div.text = ""
            for (var i = 0; i < sentences.length; i++) {
                if (inds.includes(i)) {
                    div.text += '<p style="background-color:' + colors[i] + ';">' + sentences[i] + "</p>"
                }
                else {
                    r = parseInt(colors[i].substring(1, 3), 16)
                    g = parseInt(colors[i].substring(3, 5), 16)
                    b = parseInt(colors[i].substring(5, 7), 16)
                    a = 0.3
                    rgba = r  + "," + g + "," + b + "," + a
                    div.text += '<p style="background-color:rgba(' + rgba + ');">' + sentences[i] + "</p>"
                }   
            }
        """)

    output_file("reforma_educativa.html", title="Sentence embedding example")

    show(layout)



if __name__ == '__main__':
    main()
