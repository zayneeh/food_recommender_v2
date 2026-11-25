import unittest
from recipes import load_recipes, recommend, parse_ingredients

class RecipeTests(unittest.TestCase):
    def test_corpus(self):
        self.assertEqual(len(load_recipes()),84)
    def test_white_rice_complete(self):
        r = next(x for x in recommend('rice, salt',limit=84) if x['id']==75)
        self.assertTrue(r['can_make'])
    def test_no_water_assumption(self):
        r = next(x for x in recommend('rice, salt',assume_water=False,limit=84) if x['id']==75)
        self.assertIn('water',r['missing_ingredients'])
    def test_garri_is_not_abacha(self):
        self.assertEqual(recommend('garri, water'),[])
    def test_palm_oil_is_not_vegetable_oil(self):
        r = next(x for x in recommend('rice, palm oil, onion',limit=84) if x['id']==59)
        self.assertIn('vegetable oil',r['missing_ingredients'])
    def test_tomato_is_not_paste(self):
        r = next(x for x in recommend('rice, tomato, onion',limit=84) if x['id']==59)
        self.assertIn('tomato paste',r['missing_ingredients'])
    def test_optional(self):
        r = next(x for x in recommend('plantain',limit=84) if x['id']==43)
        self.assertTrue(r['can_make'])
        self.assertIn('pepper',r['optional_missing'])
    def test_alternative(self):
        r = next(x for x in recommend('maize flour',limit=84) if x['id']==36)
        self.assertTrue(r['can_make'])
    def test_normalize(self):
        self.assertEqual(parse_ingredients('tomatoes, rodo, maggi, tomato'),{'tomato','hot pepper','seasoning cube'})
    def test_threshold(self):
        self.assertTrue(all(x['can_make'] for x in recommend('rice, salt',min_match=1,limit=84)))
    def test_salt_only(self):
        self.assertEqual(recommend('salt, water'),[])

if __name__=='__main__': unittest.main()
