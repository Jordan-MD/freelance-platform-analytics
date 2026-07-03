import unicodedata

def generer_graine_groupe(nom_complet: str) -> int:
    chaine_normalisee = unicodedata.normalize('NFKD', nom_complet)
    S = "".join(c for c in chaine_normalisee if not unicodedata.combining(c))
    S = S.upper().replace(" ", "")

    n = len(S)
    p = 31
    m = 2**31 - 1
    graine = 0

    for i in range(n):
        valeur_ascii = ord(S[i])
        graine = (graine * p + valeur_ascii) % m

    return graine
