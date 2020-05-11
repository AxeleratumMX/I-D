import spacy
import nltk
import numpy as np
import scipy
from spacy import displacy
from pathlib import Path

class Node:

    def __init__(self, id=-1, tokens=None, is_leave=False, parent=None, children=None, dependency=None):
        self.id = id
        self.tokens = tokens if tokens else []
        self.is_leave = is_leave
        self.parent = parent
        self.children = children if children else []
        self.dependency = dependency
        self.can_squeeze = False

    def __str__(self):
        return 'Node[id:%d, tokens:%s, is_leave:%s, parent:%d, children:%s, dependency=%s, can_squeeze=%s]' % (self.id, self.tokens, self.is_leave, self.parent.id if self.parent else -1, [child.id for child in self.children], self.dependency, self.can_squeeze)

    __repr__ = __str__

class IdeasExtractor:

    SPLIT = ['conj', 'nsubj']
    JOIN = ['nsubj']
    IDEA_SEPARATOR = ['conj']
    
    def __init__(self, processor=None, min_length=3):

        self.processor = processor
        self.min_length = min_length
        if self.processor is None:
            self.processor = spacy.load('es_core_news_md')

    def extract(self, document):

        tokens = self.processor(document)
        ideas = self.__extract_ideas(tokens)
        ideas = [[ word.text for word in idea ] for idea in ideas if len(idea) > self.min_length ]
        sent = [' '.join(phrase).strip() for phrase in ideas]
        return sent

    def __parse_node(self, node, edge_sep):

        result = []
        edges = []

        for child in node.tokens.children:
            if child.dep_ in edge_sep:
                edges.append(Node(tokens=child))
            else:
                result_, edges_ = self.__parse_node(Node(tokens=child), edge_sep)
                result += result_
                edges += edges_ 

        result = [node] + result

        return result, edges

    def __generate_subtree(self, tokens):

        roots = [Node(tokens=token, parent=None) for token in tokens if token.dep_ == 'ROOT']

        results = []
        
        for root in roots:
            result, edges = self.__parse_node(root, edge_sep=self.SPLIT)
                  
            pos = len(results)

            node = Node()
            node.tokens = [res.tokens for res in result]
            node.id = pos
            node.is_leave = True
            node.parent = root.parent
            node.dependency = root.tokens.dep_

            if node.parent:
                node.parent.is_leave = False
                node.parent.children.append(node)
                
            for edge in edges:
                edge.parent = node

            results.append(node)

            roots += edges

        return results

    def __mark_squeezable(self, nodes, start_nodes):

        for node in nodes:
            node.visited = False

        leaves = start_nodes.copy()
        reduced_nodes = 0
        for leave in leaves:

            if nodes[leave].dependency not in self.JOIN:
                nodes[leave].can_squeeze = False
            else: 
                nodes[leave].can_squeeze = True

            if nodes[leave].can_squeeze:
                child_squeeze = True
                for child in nodes[leave].children:
                    if child.dependency not in self.JOIN:
                        child_squeeze = child_squeeze and False
                    else:
                        child_squeeze = child_squeeze and True

                nodes[leave].can_squeeze = nodes[leave].can_squeeze and child_squeeze

            if nodes[leave].can_squeeze:
                reduced_nodes += 1

            if nodes[leave].parent:
                leaves.append(nodes[leave].parent.id)
        
        return reduced_nodes

    def __squeeze(self, nodes):
        
        leaves = [node.id for node in nodes if node.is_leave]
        reduced_nodes = self.__mark_squeezable(nodes, leaves)
        non_squeezed_nodes = [node.id for node in nodes]
        new_nodes = [node for node in nodes]
        
        if reduced_nodes > 0:
            for leave in leaves:
                if new_nodes[leave].can_squeeze and new_nodes[leave].parent and new_nodes[leave].parent.can_squeeze:
                    new_nodes[leave].parent.tokens += new_nodes[leave].tokens
                    non_squeezed_nodes.remove(new_nodes[leave].id)

                if new_nodes[leave].parent and new_nodes[leave].parent.id not in leaves:
                    leaves.append(new_nodes[leave].parent.id)

            new_nodes = [node for node in new_nodes if node.id in non_squeezed_nodes]

            for node in new_nodes:
                node.children = [cnode for cnode in node.children if cnode.id in non_squeezed_nodes]
                if len(node.children) <= 0:
                    node.is_leave = True
        
        return new_nodes

    def __join_nodes(self, node):

        if node.is_leave:
            return [node.tokens]

        conjunctions = [node.tokens]
        complements = []

        for child in node.children:
            if child.dependency in self.IDEA_SEPARATOR:
                conjunctions += self.__join_nodes(child)
            else:
                complements += self.__join_nodes(child)

        sentences = []
        for conjunction in conjunctions:
            if len(complements) > 0:
                for complement in complements:
                    sentences.append(conjunction + complement)
            else:
                sentences.append(conjunction)

        return sentences

    def __generate_norm_sentences(self, nodes):
        
        roots = [node for node in nodes if node.dependency == 'ROOT'] 
        result = []
        for root in roots:
            result += self.__join_nodes(root)
            
        return result

    def __extract_ideas(self, tokens):
        
        token_idx = { token: idx for idx, token in enumerate(tokens) }
        
        nodes = self.__generate_subtree(tokens)
        print(nodes)
        squeezed_nodes = self.__squeeze(nodes)
        print(squeezed_nodes)
        sentences = self.__generate_norm_sentences(squeezed_nodes)
        print(sentences)

        sentences = [ sorted(sentence, key=token_idx.get) for sentence in sentences ]

        return sentences




nlp = spacy.load('es_core_news_md')
ideas_extractor = IdeasExtractor(processor=nlp, min_length=0)
ideas_extractor.SPLIT = ['conj', 'nsubj']
ideas_extractor.KEEP_SPLIT = ['conj']

document = '''
La digitalización y la caída de márgenes por los tipos negativos son las razones que esgrimen los bancos para seguir reduciendo plantilla.
'''

document = '''
La comisión activó un plan de contingencia y restringió la circulación de vehículos de con hologramas de verificación 2 y 1, así como con engomado de color rojo, terminación de placa de circulación 3 y 4, entre otras medidas.
'''

document = '''
En conferencia de prensa, la mandataria capitalina destacó que el anunció se dará en el reporte de las 15:00 horas, con la finalidad de que la medida ayude a la disminución de partículas contaminantes.
'''

document = 'El presidente y los ciudadanos creen que no es suficiente labor'

document = 'Son bonitos y amigables el perro y el gato'

#document = 'El perro es bonito y el gato también'

#document = 'El perro es bueno y el gato es malo'
document = 'El perro y el gato son bonitos y cariñosos'

result = ideas_extractor.extract(document)

for sentence in result:
    print('*', sentence)
 
 

svg = displacy.render(nlp(document)) 
with open('C:\\Users\\Uriel Corona\\Downloads\\render.svg', 'w', encoding='utf-8') as f:
    f.write(svg)