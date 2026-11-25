import unittest
from app import run
class Limite(unittest.TestCase):
    def test_limitar(self):
        data={"tema":"fé","data_sermao":"2026-10-01","intervalo_dias":30,"limite_sugestoes":1,"ilustracoes":[dict(titulo=t,resumo="Resumo",origem="Fonte",temas=["Fé"]) for t in ["B","A"]]}
        result=run(data)
        self.assertEqual(result["sugeridas"][0]["titulo"],"A")
        self.assertEqual(result["total_sugeridas"],2)
        self.assertEqual(result["sugeridas_omitidas"],1)
        data["limite_sugestoes"]=0
        with self.assertRaises(ValueError): run(data)
