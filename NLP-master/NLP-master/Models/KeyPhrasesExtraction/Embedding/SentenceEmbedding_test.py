from SentenceEmbedding import Model
#from AroraSentenceEmbedding import Model
from sklearn.decomposition import PCA
import numpy as np
import os
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import CustomJS, Div
from bokeh import events
from bokeh.models import HoverTool, ResetTool, BoxSelectTool
from bokeh.layouts import column, row
import os


def main():
    """run an example of how to use sentence-to-vector model"""

    #os.chdir("C:\\Users\Hugo\Desktop\SourceCloudGit\\Natural_Language_Processing\Models\KeyPhrasesExtraction\Embedding")

    model = Model()
    sentences = [
        "Minatitlán.",
        "Al entrar hoy en operaciones la primera coordinación de la Guardia Nacional en este municipio veracruzano, elementos del Ejército y de la Policía Federal, portando la insignia de la nueva corporación, montaron operativos de revisión en diversas calles, además de realizar patrullajes.",
        "Aún con sus uniformes castrenses y policiacos, en cada caso, efectúan revisiones en vehículos y verifican documentos de choferes.",
        "Sobre la avenida Benito Juárez, colonia Cerro Alto, sobre todo en camionetas y taxis.",
        "En su conferencia mañanera, el Presidente Andrés Manuel López Obrador anunció el arranque de la Guardia Nacional en este municipio, con la primera coordinación, de 266 que habrá en el país.",
        "Luego se hará lo propio en Salina Cruz y Coatzacoalcos, en el sur de la entidad, así como en Cancún, Quintana Roo, puntos en los que se requiere con más urgencia a la corporación, dijo.",
        "Antes de viajar a ese municipio, en el inicio de una gira por la región del Istmo de Tehuantepec, dijo que aunque todavía no hay leyes secundarias, la reforma constitucional permite al gobierno iniciar con la instalación de bases para la guardia.",
        "Entonces, la primera que se establece ya con el número de elementos suficientes con mando único va a ser la de Minatitlán, el día de hoy, señaló en la conferencia de prensa matutina en la que estuvo acompañado por el secretario de la Defensa Nacional, Luis Cresencio Sandoval, y el titular de la Secretaría de Comunicaciones y Transportes, entre otros.",
        "Agradeció en ese punto a los legisladores que convocarán a un periodo extraordinario de sesiones para la aprobación de las leyes secundarias para la Guardia Nacional.",
        "Pero sí, en efecto, hoy se va a dar a conocer la estrategia de seguridad en Mitatitlán, que es la primera coordinación.",
        "Y también en Minatitlán vamos a dar respuesta a la demanda de seguridad.",
        "Me va a acompañar el gabinete de seguridad y se va a presentar un plan para proteger a la población en el marco del funcionamiento de la Guardia Nacional",
        "Señaló que la visita de hoy al sur de Veracruz ya estaba programada desde antes de los sucesos lamentables en Minatitlán (el viernes 19 de abril un grupo armado mató a 13 personas que se hallaban en una fiesta).",
        "El encuentro de hoy, comentó, es con todo el pueblo, en la plaza pública y desde luego vamos a expresar nuestro más sentido pésame, ya lo hemos hecho, a los familiares de las víctimas.",
        "Y vamos a eso, a que se investigue, se castigue a los responsables y haya justicia.",
        "Por eso, agregó, la reunión que tenía como propósito original los programas de Bienestar se amplía y ahora se va a tratar también el tema de la violencia y lo que se está haciendo al respecto.",
        "El mandatario irá el sábado a Coatzacoalcos, Veracruz y Salina Cruz, así como Matías Romero y Juchitán, Oaxaca, para revisar las obras del Tren Transítsmico, así como todo el proyecto social en la región.",
    ]
    vecs = model.sentence_to_vector(sentences)

    draw_bokeh(vecs, sentences)


def draw_bokeh(vecs, sentences):
    """ Dimension reduction with PCA and plotting with bokeh """

    X = np.array([x["feature_vector"] for x in vecs])
    X_reduced = PCA(n_components=2).fit_transform(X)

    source = ColumnDataSource(
        data=dict(
            eigenv1=[x[0] for x in X_reduced],
            eigenv2=[x[1] for x in X_reduced],
            s=sentences,
        )
    )

    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "@eigenv1, @eigenv2)"),
            ("s", "@s")
        ]
    )

    p = figure(title="Guardia nacional", tools=[hover, ResetTool(), BoxSelectTool()])
    p.xaxis.axis_label = '1st eigenv'
    p.yaxis.axis_label = '2nd eigenv'
    p.circle('eigenv1', 'eigenv2', size=10, fill_alpha=1, nonselection_fill_alpha=0.5, source=source)

    div = Div(width=400)
    layout = row(p, div)

    source.callback = CustomJS(args=dict(source=source, div=div, sentences=sentences), code="""
        var inds = source.selected.indices
        div.text = ""
        for (var i = 0; i < sentences.length; i++) {
            if (inds.includes(i)) {
                div.text += '<p style="background-color:powderblue;">' + sentences[i] + "</p>"
            }
            else {
                div.text += "<p>" + sentences[i] + "</p>"
            }   
        }
    """)

    output_file("news.html", title="Sentence embedding example")

    show(layout)


if __name__ == '__main__':
    main()










