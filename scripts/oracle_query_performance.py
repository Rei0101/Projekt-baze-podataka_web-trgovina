import time
import cx_Oracle

conn = cx_Oracle.connect(
    "WEB_TRGOVINA/admin@localhost:1521/XE"
)
cur = conn.cursor()

queries = {
    "Q1_Zaposlenik_Detalji": """
        SELECT Z.IME, Z.PREZIME, G.NAZIV_GRADA, S.ADRESA_SKLADISTA, F.NAZIV_FUNKCIJE
        FROM ZAPOSLENICI Z
        INNER JOIN GRADOVI G ON Z.GRADOVI_ID_GRAD = G.ID_GRAD
        INNER JOIN SKLADISTA S ON Z.SKLADISTA_ID_SKLADISTE = S.ID_SKLADISTE
        INNER JOIN FUNKCIJE_ZAPOSLENIKA F ON Z.FUNKCIJE_ZAPOSLENIKA_ID2 = F.ID_FUNKCIJA_ZAPOSLENIKA
        WHERE Z.ID_ZAPOSLENIK = 1
    """,

    "Q2_Korisnik_Racuni": """
        SELECT K.IME, K.PREZIME, R.ID_RACUNI, R.DATUM_KUPNJE
        FROM KORISNICI K
        INNER JOIN RACUNI R ON K.ID_KORISNIK = R.KORISNICI_ID_KORISNIK
        WHERE K.ID_KORISNIK = 1
    """,

    "Q3_Stavke_Racuna": """
        SELECT R.ID_RACUNI, P.NAZIV_PROIZVODA, RP.KOLICINA
        FROM RACUNI R
        INNER JOIN RACUNI_PROIZVODI RP ON R.ID_RACUNI = RP.RACUNI_ID_RACUNI
        INNER JOIN PROIZVODI P ON RP.PROIZVODI_ID_PROIZVOD = P.ID_PROIZVOD
        WHERE R.ID_RACUNI = 1
    """,

    "Q4_Top_Proizvodi": """
        SELECT *
        FROM (
            SELECT P.NAZIV_PROIZVODA,
                   SUM(RP.KOLICINA) AS UKUPNO_PRODANO
            FROM PROIZVODI P
            INNER JOIN RACUNI_PROIZVODI RP ON P.ID_PROIZVOD = RP.PROIZVODI_ID_PROIZVOD
            GROUP BY P.NAZIV_PROIZVODA
            ORDER BY SUM(RP.KOLICINA) DESC
        )
        WHERE ROWNUM <= 5
    """,

    "Q5_Zaposlenik_KPI": """
        SELECT *
        FROM (
            SELECT 
                P2.NAZIV_PROIZVODA,
                COUNT(*) AS BROJ_ZAJEDNICKIH_KUPNJI
            FROM RACUNI R1
            INNER JOIN RACUNI_PROIZVODI RP1 ON R1.ID_RACUNI = RP1.RACUNI_ID_RACUNI
            INNER JOIN RACUNI_PROIZVODI RP2 ON RP1.RACUNI_ID_RACUNI = RP2.RACUNI_ID_RACUNI
            INNER JOIN PROIZVODI P2 ON RP2.PROIZVODI_ID_PROIZVOD = P2.ID_PROIZVOD
            WHERE RP1.PROIZVODI_ID_PROIZVOD = 1
            AND RP2.PROIZVODI_ID_PROIZVOD <> 1
            GROUP BY P2.NAZIV_PROIZVODA
            ORDER BY COUNT(*) DESC
        )
        WHERE ROWNUM <= 5
    """
}

results = []

for name, query in queries.items():
    start = time.perf_counter()
    
    cur.execute(query)
    cur.fetchall()
    
    end = time.perf_counter()
    
    duration_ms = (end - start) * 1000
    
    results.append((name, round(duration_ms, 3)))


print("\n=== ORACLE PERFORMANCE RESULTS ===")
print("{:<25} {:>10}".format("QUERY", "TIME (ms)"))
print("-" * 40)

for r in results:
    print("{:<25} {:>10}".format(r[0], r[1]))

cur.close()
conn.close()
