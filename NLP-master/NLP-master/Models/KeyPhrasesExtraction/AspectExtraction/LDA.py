from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()


n_samples = 2000
n_features = 100
n_components = 10
n_top_words = 20


dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
data_samples = dataset.data[:n_samples]
data_samples = [
"Uno de mis cinepolis favoritos y uno de los mejores ubicados en mi opinión. Cuenta con sala VIP y una organización que me agrada bastante en cuanto al orden de los servicios como taquilla, dulcería y taquilla VIP. Tienen una limpieza sin igual y debido a su ubicación es bastante bueno para poder recorrer una considerable parte del centro comercial. En cuanto al servicio, el rápido y eficiente, no tengo quejas en cuanto a lo serviciales que pueden ser sus trabajadores y el empeño que ponen en su labor.",
"Como cualquier otro cine, pero no tiene acceso para personas discapasitadas",
"Sus salas muy limpias, es bastante cómodo",
"Lugar no tan concurrido, siempre encuentro buenos lugares.",
"Me encanto toda la gente en su lugar haciendo lo suyo atendiendo lo mas rápido posible la gente suficiente el lugar con luz apropiada las salas muy bien y en cuanto comienza la película se cierran las puertas y ay personal ayudando ala gente a encontrar sus lugar en lo personal muy grato",
"Porque queda en un lugar cercano a mi domicilio y está bonito",
"Las salas son pequeñas, se escuchan las peliculas de las otras salas.",
"Excelente",
"Demasiado atascado de gente, ninguna película que quería ver había cupo. Además como qie estaba de malas el de la taquilla. Pero en general bueno",
"Muy bien ubicada la plaza",
"Es muy cómodo y agradable, me gusta mucho el trato que brinda el personal de aquí c:",
"Muy cerca de metro barranca del muerto.... Complejo de cobepolis muy cómodo!",
"Tienen muy poca gente despachando en dulcería y si vas con poco tiempo de tolerancia Para tu película...eso te retrasa muchisimo",
"Buena atención",
"Mi estancia fue muy cómoda, el personal fue muy atento y amable. En lo que respecta a la dulcería la fila era larga pero avanzó muy rápido con lo cual no hay que esperar mucho tiempo. El espacio para estar antes de que comience tu función es amplio, ademas de que la plaza donde esta ubicado cuenta con muchos otros lugares en donde pasar un buen rato.",
"Buen cine, bien organizado y con buena atención. Nunca he ido a la sala general siempre he ido a la sala VIP que es bastante agradable y tienen una buena variedad de botanas y platillos para comer, además de las ya conocidas golosinas y palomitas. Si deseas puedes optar por un trago o café para esperar tu película o si quieres pues dentro de la sala ya viendo la misma. Muy recomendable.",
"Me encanto toda la gente en su lugar haciendo lo suyo atendiendo lo mas rápido posible la gente suficiente el lugar con luz apropiada las salas muy bien y en cuanto comienza la película se cierran las puertas y ay personal ayudando ala gente a encontrar sus lugar en lo personal muy grato",
"Buen cine, en un buen lugar en una muy buena ubicación. El precio es regular y quizás su único 'pero' es la manera en que distribuyen las películas; constantemente, tienen horarios demasiado diferidos para cintas de poco alcance.",
"Esta medio escondido llegar, pero es un buen cine. Todos son muy amables. Y también hay forma de comprar boletos sin necesidad de estar haciendo fila. Se puede hacer en las máquinas de autoservicio.",
"Pues que puedo decir si cada semana vamos 1 o 2 veces al cine me encanta",
"Es muy cómodo y agradable, me gusta mucho el trato que brinda el personal de aquí c:",
"Esta sucursal es algo pequeña por lo que se llena de gente fácilmente y tendrás que hacer fila para todo: para la taquilla, para la dulcería, para entrar a la sala y para el baño. En cuanto a todo lo demás ofrecen buen servicio como en cualquier otra sala de cine.",
"Muy buen establecimiento, los trabajadores son buenos y aclaran tus dudas y las salas son bastante grandes. ¡Muy bueno sin duda!",
"Buena actitud de servicio, salas limpias y de buen tamaño, excelente sonido. Altamente recomendable.",
"Uno de mis cinepolis favoritos y uno de los mejores ubicados en mi opinión. Cuenta con sala VIP y una organización que me agrada bastante en cuanto al orden de los servicios como taquilla, dulcería y taquilla VIP. Tienen una limpieza sin igual y debido a su ubicación es bastante bueno para poder recorrer una considerable parte del centro comercial. En cuanto al servicio, el rápido y eficiente, no tengo quejas en cuanto a lo serviciales que pueden ser sus trabajadores y el empeño que ponen en su labor.",
"Muestran muy buenas películas. El lugar siempre esta limpio y te atienden muy bien.",
"Muy comodo y muy buen servicio.",
"Muy concurrido pero sus salas son excelentes. Buen servicio del personal",
"El cine está bien, es un cine u casi todos son iguales. Lo que no está bien es la Plaza, para llegar al local del cine hay que caminar un montón y una persona co oxígeno debe caminar todo eso.... No hay atajos como.para llegar rápido, los elevadores quedan lejos del acceso y luego la sala tan grande también hay que subir muchos pisos para la butaca. Para no volver sólo por esa razón, mejor una plaza más cómoda",
"El cine super bien. La plaza no termina por convencerme, es demasiado extraña.",
"Este cine es muy cómodo y buena atención",
"Muy buen lugar buenas salas",
"Muy agradable y fácil de llegar.",
"Me encanta.... Es un complejo que al contar con sala junior y eso le da un alto valor para que lo visiten las familias",
"Este Cinépolis se me hace genial. Siempre voy al VIP y la atención es excelente",
"Demasiado atascado de gente, ninguna película que quería ver había cupo. Además como qie estaba de malas el de la taquilla. Pero en general bueno",
"Es muy cómodo y muy grande ..",
"El complejo es bueno en general, pero no se que tienen TODOS los cinepolis que el área de dulceria siempre está exageradamente llena de gente por que no hay coordinación para la atención. Deben de echarle ganas a eso. Sus productos en general son buenos.",
"Excelente lugar para llevar al cine a los niños, porfavor padre respeta los límites de edad para cada juego",
"Muy cerca de metro barranca del muerto.... Complejo de cobepolis muy cómodo!",
"Lugar agradable y la limpieza en todo es una característica. La atención del personal en el área de alimentos puede mejorar en amabilidad. Es una buena oportunidad de seguir creciendo.",
"Exelente lugar para sasar el rato buen contenido de peliculas, la dulceria tiene buena atencion las salas son amplias con acientos comodos",
"Buena plaza, limpia, hay opciones decentes para comprar y comer, cines, un estacionamiento grande. Generalmente es tranquila y con poca gente.",
"El personal es amable. Los precios son un poco más baratos que en otros Cinépolis, cono Perisur",
"Muy amplio y bien surtido, aunque no tenían Ice más que de limón, espero que no sea algo que pase seguido",
"Exelente lugar para divertirse cualquier dia de la semana",
"Un buen cine ala salida del metro barranca del muerto",
"Muy buen ubicación",
"Buen servicio del personal y la atención rápida en la dulcería a pesar de haber mucha gente los fines de semana",
"Todo excelente, muy recomendable.",
"Excelente y pequeño por eso casi siempre esta vacio!",
"Visitamos las salas junior y son excelentes para los más pequeños ya que poseen parque, y ofrecen dos recesos para que los niños disfruten y jueguen en esa área. El primer receso es antes de empezar la película y el segundo receso es a la mitad de la película donde paran la función para que puedan jugar los peques",
"Rápida atención en la dulcería, el apartado VIP estaba muy escondido... No lo ví hasta que entre a la sala.",
"Acogedor y con buenas salas, aunque reducido de espacio y por lo tanto se llena fácilmente",
"Tampoco se me hizo bueno el servicio y atención. Muy chiquito y poco interés de los q atienden",
"Buen servicio, aunque creo que la salida la conplican al tener que salir unicamente por los elevadores",
"El cine cuenta con un servicio rápido, tanto en taquillas como en dulceria.",
"Bonito y te atienden bien",
"El com0lejo esta super bien ubicado en una plaza nueva y muy función al . De no hay mucho que decir la firma se cono se y creo que es muy competitiva con sus oponentes . La ventaja que tiene este complejo es esta ubicada como ya dije en una plaza muy bonita y con muchos comercios padres . Visiten la no se arrepentirán. En lo personal lo que más me gusta es que se encuentra en el último piso y pasas por toda las tiendas y es como de 5 pisos el centro comercial",
"Buena sucursal, todos muy amables y todos limpio.",
"Cinépolis tiene la garantía de ser siempre un excelente lugar para ver películas ,sus salas son muy cómodas y las palomitas son las mejores, en esta sucursal ubicada en portal San angel las cosas no cambian, se mantiene el mismo estándar de calidad que caracteriza a Cinépolis",
"Las salas Muy bien",
"Muy buen sitio para pasar el rato con la novia, familia o amigos",
"es un cine muy bueno sobre todo por la salas no tradicionales. se disfruta mucho el 4dx",
"Un lugar muy limpio",
"Muy buen servicio, instalaciones muy limpias en las salas VIP, los sillones es.muy cómodos, vale la pena el pago ya que para películas largas es muy cómodo y si tienes antojo o hambre puedes comer sin problemas aunque para ser honesto, comer a oscuras no es la mejor experiencia, menos cuando estás viendo una película.",
"Bastante cómodo, las salas no son muy grandes, lo que hace que sea más cómoda la experiencia. Incluso con sala bastante concurrida",
"Amplio estacionamiento, fácil acceso, rapidez en taquilla y venta de dulces.",
"La salas son chiquitas y se ve cuando escoges los boletos pero cuando llegas a tu asiento te das cuenta de que esta más atrás de lo que se veía en la pantalla. Fuera de eso el servicio es bueno, los sanitarios son grandes y muy limpios",
"No tiene tanto tiempo de existencia, pero cumple con todo lo necesario para ser excelente.",
"Una buena opción para completar tu día, siempre una buena cartelera y en general, los felicito por la amabilidad con la que atienden en el mostrador",
"Cinépolis VIP Portal San Ángel está in-cre-í-ble! La atención es esmerada, en el lobby se disfrutan sus sillones y en caso de que haya que esperar un poco hay revistas para hojear y servicio de bar y platillos calientes. Ya en la sala los asientos son muy amplios, reclinables y limpios. Puedes ordenar a tu asiento lo que se te antoje. Me encantó la experiencia, te hacen sentir consentido. Sí se desquita lo que se paga.",
"Complejo de exhibición de cine, con instalaciones bastante cuidadas. Su mayor problema es que la mayoría de las películas que exhibe están dobladas al español y solo encontrarán películas de lo más comercial que hay en cartelera.",
"Super menos la policía gordita que se encuentra es super grocera y nada amable",
"Súper cómodo y está en una plaza muy bonita, me gusta mucho!",
"Las salas VIP necesitan mantenimiento. Me tocó un asiento chueco y deforme pero el servicio es bueno. Los baños no estaban tan limpios en la sección VIP. Necesitan mejorar.",
"Tiene muchas salas.",
"Servicio excelente, pero la comida a decaído muchísimo, órdenes incompletas y con mala presentación y calidad",
"La sala de bien, pero el servicio nefasto, los de la dulceria se equivocaron en lo que pedimos. Además después de ponerle limón a las palomitas no quisieron rellenar el envase, como si las vendieran tan baratas.",
"Son tan lentos en coffee tree, que aunque llegues con 30 min de anticipación, te hacen llegar tarde a tu función. En VIP siempre toman mal la orden, o se tardan más de 30 min en llevarte lo que pediste, frío, incompleto... con razón son el Cinépolis con más “áreas de oportunidad”.",
"Demasiado pequeño el lugar,en definitiva nunca volveria a ir a este cine",
]

# Use tf (raw term count) features for LDA.
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features,
                                stop_words=["en", "de", "que", "la", "el", "lo", "es", "las", "para", "muy", "los", "una", "se",
                                            "son", "no", "un", "con", "me", "pero", "me", "al", "si", "ya", "toda", "su", "más"])
tf = tf_vectorizer.fit_transform(data_samples)

lda = LatentDirichletAllocation(n_components=n_components, max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
lda.fit(tf)

print("\nTopics in LDA model:")
tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words)

