import utils
from ontolutils import Thing


class TestValidation(utils.ClassTest):

    def test_validation(self):
        shacl_has_label = """@prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix ex: <http://example.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        
        ex:ThingShape a sh:NodeShape ;
            sh:targetClass owl:Thing ;
            sh:property [
                sh:path rdfs:label ;
                sh:datatype xsd:string ;
                sh:minCount 1 ;
            ] .
        """
        thing = Thing(
            id="http://example.org/thing1",
            label="A test thing",
            comment="This is a test thing for validation."
        )
        res = thing.validate(shacl_data=shacl_has_label)
        self.assertTrue(res)

        thing_no_label = Thing(
            id="http://example.org/thing2",
            comment="This is a test thing without a label."
        )
        res_no_label = thing_no_label.validate(shacl_data=shacl_has_label, raise_on_error=False)
        self.assertFalse(res_no_label)
