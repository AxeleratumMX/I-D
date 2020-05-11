import re
import spacy
from neo4j import GraphDatabase, ServiceUnavailable


class Graph(object):

    def __init__(self, app=None):
        uri = "bolt://ec2-54-159-200-80.compute-1.amazonaws.com:7687"
        user = "neo4j"
        password = "i-017122e55d72b1a4c"
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

        if (app):
            self.logger = app.logger.info
        else:
            self.logger = print
        self.logger('======= Open connection for neo4j =====')

    def close(self):
        self._driver.close()
        self.logger('======= Closing connection for neo4j =====')

    def exec_query(self, query_method, params=None):
        try:
            with self._driver.session() as session:
                return session.write_transaction(query_method, params)
        except ServiceUnavailable:
            return "Service unavailable - Network or database problem"

    def count_words(self):
        def count_words_query(tx, params):
            result = tx.run("MATCH (n:Word) RETURN count(*)")
            return str(result.single()[0])

        return self.exec_query(count_words_query)

    def get_document(self, doc_id):
        def get_text_query(tx, doc_id, logger=self.logger):
            r = tx.run(""" 
                MATCH (doc:Doc)-[:STARTS]->(begin:T)
                MATCH (begin)-[:NEXT_DOC*]->(end:T)
                WHERE ID(doc)=$doc_id AND NOT (end)-[:NEXT_DOC]->()

                MATCH path=(begin)-[:NEXT_DOC*]->(end) 
                WITH nodes(path) AS NODES

                UNWIND NODES as t
                MATCH (t)-[:FOR]->(w:Word)
                RETURN w.name""", doc_id=doc_id)

            words = [record['w.name'] for record in r]
            return " ".join(words)

        return self.exec_query(get_text_query, doc_id)

    def create_document(self, text):
        def create_doc_query(tx, text):
            text = text.replace('“', '"')
            text = text.replace('”', '"')
            text = text.replace('...', '…')

            for r in re.findall(r"\n+", text):
                text = text.replace(r, '\n')

            text = text.lower()
            text = '->'.join(re.findall(r"\w+|[^\w\s]|\n", text, re.UNICODE))

            r = tx.run(""" 
                CREATE (d:Doc {name:"unnamed_doc"}) WITH ID(d) as doc_id, d
                SET d.name = "document " + doc_id
                
                MERGE (d)-[r:STARTS]->(t:T {document:id(d), seq:1}) WITH id(d) AS idDoc
                    
                WITH split($text, "->") AS text, idDoc
                UNWIND range(0, size(text) - 1) AS i
                
                MERGE (w1:Word {name: text[i]}) 
                    ON CREATE SET w1.count = 1 
                    ON MATCH SET w1.count = w1.count + 1
                
                // if (i < size(text) - 1):  
                FOREACH (ignoreMe in CASE WHEN i < size(text) - 1 THEN [1] ELSE [] END | 
                    MERGE (w2:Word {name: text[i + 1]}) 
                        ON CREATE SET w2.count = 1 
                        
                    MERGE (t1:T {document:idDoc, seq:i + 1})	
                    MERGE (t2:T {document:idDoc, seq:i + 2})
                        
                    MERGE (w1)-[r1:NEXT]->(w2)
                        ON CREATE SET r1.count = 1
                        ON MATCH SET r1.count = r1.count + 1
                    
                    MERGE (t1)-[r2:NEXT_DOC]->(t2)
                    
                    MERGE (t1)-[r3:FOR]->(w1)
                    
                    MERGE (t2)-[r4:FOR]->(w2)
                )
                
                WITH DISTINCT idDoc 
                RETURN idDoc""", text=text)

            doc_id = r.single()[0]

            return doc_id

        return self.exec_query(create_doc_query, text)

    def delete_document(self, doc_id):
        def delete_document_query(tx, doc_id, logger=self.logger):
            ## delete references
            r = tx.run(""" 
                MATCH (doc:Doc)-[:STARTS]->(:T)-[:NEXT_DOC*]->(:T)-[:END_R]->(ref:Reference)
                WHERE ID(doc)=$doc_id
                DETACH DELETE ref""", doc_id=doc_id)

            ## delete opinion
            r = tx.run("""
                MATCH (doc:Doc)-[:STARTS]->(:T)-[:NEXT_DOC*]->(:T)-[:END_O]->(opinion:Opinion)
                WHERE ID(doc)=$doc_id
                DETACH DELETE opinion""", doc_id=doc_id)

            ## decrement word.count - 1
            r = tx.run("""
                MATCH (doc:Doc)-[:STARTS]->(begin:T)
                MATCH (begin)-[:NEXT_DOC*]->(end:T)
                WHERE ID(doc)=$doc_id AND NOT (end)-[:NEXT_DOC]->()
                
                MATCH path=(begin)-[:NEXT_DOC*]->(end) 
                WITH nodes(path) AS NODES
                
                UNWIND NODES as t
                MATCH (t)-[:FOR]->(w:Word)
                SET w.count = w.count - 1
                """, doc_id=doc_id)

            ## delete :NEXT connection between words
            r = tx.run("""
                MATCH (doc:Doc)-[:STARTS]->(begin:T)
                MATCH (begin)-[:NEXT_DOC*]->(end:T)
                WHERE ID(doc)=$doc_id AND NOT (end)-[:NEXT_DOC]->()
                
                MATCH path=(begin)-[:NEXT_DOC*]->(end) 
                WITH nodes(path) AS NODES
                
                UNWIND NODES as t
                MATCH (t)-[:FOR]->(w:Word)
                MATCH (t)-[:NEXT_DOC]->(:T)-[:FOR]->(w2:Word)
                MATCH (w)-[next:NEXT]->(w2)
                SET next.count = next.count - 1
                
                FOREACH (ignoreMe in CASE WHEN next.count = 0 THEN [1] ELSE [] END |
                    DELETE next
                )""", doc_id=doc_id)

            ## delete T's
            r = tx.run("""
                MATCH (doc:Doc)-[:STARTS]->(begin:T)-[:FOR]->(beginW:Word)
                MATCH (begin)-[:NEXT_DOC*]->(end:T)-[:FOR]->(endW:Word)
                WHERE ID(doc)=$doc_id AND NOT (end)-[:NEXT_DOC]->()
                
                MATCH path=(begin)-[:NEXT_DOC*]->(end) 
                WITH nodes(path) AS NODES
                UNWIND NODES as t
                DETACH DELETE t""", doc_id=doc_id)

            #delete document
            r = tx.run("""
                MATCH (doc:Doc)
                WHERE ID(doc)=$doc_id
                DELETE doc""", doc_id=doc_id)

            return "Document {0} successfully deleted".format(doc_id)

        return self.exec_query(delete_document_query, doc_id)


### unit tests ### (There must be a better way to automatize these ...)

## document schema:
conn = Graph()
doc_id = conn.create_document("En respuesta a las preguntas de los legisladores...")
print(doc_id)
print(conn.get_document(doc_id))
msg = conn.delete_document(doc_id)
print(msg)
conn.close()


#print(conn.count_words())
# nlp = spacy.load('es')
# doc = nlp('JC y yo fuimos su parque! jejeje')
# for token in doc:
#     print ((token.text, token.pos_, token.dep_))
