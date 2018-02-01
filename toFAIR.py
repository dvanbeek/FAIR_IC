import sys
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDFS, RDF, DC, FOAF
import urllib
from hashlib import md5
import sys

repocontents = open(sys.argv[1] + "/DACRespositorycontents.txt", 'r')
studies = open(sys.argv[1] + "/DACStudies.txt", 'r')
ICdir = sys.argv[1] + "/"

repoGraph = Graph()
repoGraph.bind("dcterms", DCTERMS)
repoGraph.bind("wikidata_prop", URIRef("http://www.wikidata.org/prop/direct/"))
wikidataprop = Namespace("http://www.wikidata.org/prop/direct")
repoGraph.bind("semsc", URIRef("http://semanticscience.org/resource/"))
semscience = Namespace("http://semanticscience.org/resource/")
repoGraph.bind("AEO", URIRef("http://www.geneontology.org/formats/oboInOwl#"))
anenon = Namespace("http://www.geneontology.org/formats/oboInOwl#")
repoGraph.bind("OBO", URIRef("http://purl.obolibrary.org/obo/"))
obo = Namespace("http://purl.obolibrary.org/obo/")
repoGraph.bind("ENM", URIRef("http://purl.org/dc/terms/"))
enm = Namespace("http://purl.org/dc/terms/")
repoGraph.bind("OBA", URIRef("http://purl.obolibrary.org/obo/oba/patterns/entity_attribute/"))
oba = Namespace("http://purl.obolibrary.org/obo/oba/patterns/entity_attribute/")
repoGraph.bind("SWO", URIRef("http://usefulinc.com/ns/doap#"))
swo = Namespace("http://usefulinc.com/ns/doap#")

fairic_uri = "http://datasteward.nl/fair_IC"

header = True
headerRepo = []
for line in repocontents:
    line = line.rstrip().split("\t")
    if header:
        header = False
        headerRepo = line
        continue
    dataset = md5(line[headerRepo.index("Dataset ID")].encode()).hexdigest()
    filename = md5(("File" + line[headerRepo.index("Dataset ID")]).encode()).hexdigest()
    dataset_uri = URIRef(fairic_uri + "/rdf/dataset/" + dataset)
    file_uri = URIRef(fairic_uri + "/rdf/file/" + filename)
    repoGraph.add((dataset_uri, RDF.type, URIRef(semscience.SIO_000089)))
    repoGraph.add((dataset_uri, anenon.id, Literal(line[headerRepo.index("Dataset ID")])))
    repoGraph.add((dataset_uri, obo.OMIABIS_0000048, Literal(line[headerRepo.index("DAC number")])))
    repoGraph.add((dataset_uri, semscience.SIO_000028, file_uri))
    repoGraph.add((file_uri, RDF.type, URIRef(semscience.SIO_000396)))
    try:
        #Add support for multiple ICs per file (parents + kids situation for example)
        ic = md5(("IC" + line[headerRepo.index("Informed consent")]).encode()).hexdigest()
        ic_uri = URIRef(fairic_uri + "/rdf/ic/" + ic)
        repoGraph.add((file_uri, obo.ERO_0000460, ic_uri))
        repoGraph.add((ic_uri, RDF.type, URIRef(obo.ICO_0000001)))
        repoGraph.add((ic_uri, oba.location, Literal("N52°05'10.7 E5°10'48.0")))
        try:
            ic_file = open(ICdir + line[headerRepo.index("Informed consent")] + ".txt", 'r')
            for line in ic_file:
                line = line.rstrip()
                if line.startswith("Versie: "):
                    repoGraph.add((ic_uri, swo.version, Literal(line[len("Versie: "):])))
                elif line.startswith("Onderzoek: "):
                    repoGraph.add((ic_uri, enm.title, Literal(line[len("Onderzoek: "):])))
                else:
                    repoGraph.add((ic_uri, obo.RO_0002180, Literal(line)))
            ic_file.close()
        except IOError:
            print("Cannot find file")
    except IndexError:
        pass

header = True
headerStudy = []
for line in studies:
    line = line.rstrip().split("\t")
    if header:
        header = False
        headerStudy = line
        continue
    study = md5(line[headerStudy.index("Study ID")].encode()).hexdigest()
    study_uri = URIRef(fairic_uri + "/rdf/study/" + study)
    dataset = md5(line[headerStudy.index("Dataset ID")].encode()).hexdigest()
    dataset_uri = URIRef(fairic_uri + "/rdf/dataset/" + dataset)
    repoGraph.add((study_uri, RDF.type, URIRef(semscience.SIO_001066)))
    repoGraph.add((study_uri, anenon.id, Literal(line[headerStudy.index("Study ID")])))
    repoGraph.add((study_uri, enm.title, Literal(line[headerStudy.index("Study Title")])))
    repoGraph.add((study_uri, semscience.SIO_001277, dataset_uri))

repoGraph.serialize(destination=sys.argv[1] + '/FAIR_IC.ttl', format='turtle')

repocontents.close()
studies.close()
