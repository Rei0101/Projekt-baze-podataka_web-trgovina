import time
from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "sysadmin"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

queries = {
    "Q1_Zaposlenik_Detalji": """
        MATCH (z:Zaposlenik {id_zaposlenik: 1})
              -[:ZIVI_U]->(g:Grad),
              (z)-[:RADI_U]->(s:Skladiste),
              (z)-[:IMA_ULOGU]->(f:Funkcija)
        RETURN z.ime, z.prezime,
               g.naziv_grada,
               s.adresa_skladista,
               f.naziv_funkcije
    """,

    "Q2_Korisnik_Racuni": """
        MATCH (k:Korisnik {id_korisnik: 1})
              -[:IZVRSIO_KUPNJU]->(r:Racun)
        RETURN k.ime,
               k.prezime,
               r.id_racuni,
               r.datum_kupnje
    """,

    "Q3_Stavke_Racuna": """
        MATCH (r:Racun {id_racuni: 1})
              -[:SADRZI_STAVKU]->(p:Proizvod)
        RETURN r.id_racuni,
               p.naziv_proizvoda,
               p.id_proizvod
    """,

    "Q4_Top_Proizvodi": """
        MATCH (:Racun)-[s:SADRZI_STAVKU]->(p:Proizvod)
        RETURN p.naziv_proizvoda AS proizvod,
               count(s) AS ukupno_prodano
        ORDER BY ukupno_prodano DESC
        LIMIT 5
    """,

    "Q5_Zaposlenik_KPI": """
        MATCH (p:Proizvod {id_proizvod: 1})<-[:SADRZI_STAVKU]-(r:Racun)-[:SADRZI_STAVKU]->(p2:Proizvod)
        WHERE p <> p2
        RETURN p2.naziv_proizvoda AS proizvod,
            count(*) AS broj_zajednickih_kupnji
        ORDER BY broj_zajednickih_kupnji DESC
        LIMIT 5
    """
}

results = []

with driver.session(database="web-trgovina") as session:

    for name, query in queries.items():

        start = time.perf_counter()

        result = session.run(query)

        # forsira dohvat svih rezultata
        list(result)

        end = time.perf_counter()

        duration_ms = (end - start) * 1000

        results.append(
            (name, round(duration_ms, 3))
        )

print("\n=== NEO4J PERFORMANCE RESULTS ===")
print("{:<25} {:>10}".format("QUERY", "TIME (ms)"))
print("-" * 40)

for r in results:
    print("{:<25} {:>10}".format(r[0], r[1]))

driver.close()