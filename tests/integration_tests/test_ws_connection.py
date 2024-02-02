from unittest import TestCase, main

from py_surreal.surreal import Surreal
from py_surreal.utils import get_uuid
from tests.integration_tests.utils import URL, get_random_series


class TestWebSocketConnection(TestCase):
    def test_connect(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            self.assertTrue(connection.is_connected())
            self.assertEqual("ws://127.0.0.1:8000/rpc", connection._base_url)

    def test_use(self):
        surreal = Surreal(URL, credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.use('test', 'test')
            self.assertFalse(res.is_error(), res)
            self.assertEqual(None, res.result)

    def test_info(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.info()
            self.assertFalse(res.is_error(), res)
            self.assertEqual(None, res.result)

    def test_signup(self):
        surreal = Surreal(URL, namespace="test", database="test")
        with surreal.connect() as connection:
            res = connection.signup(namespace='test', database='test', scope='user_scope',
                                    params={'user': 'john:doe', 'pass': '123456'})
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_signin_root(self):
        surreal = Surreal(URL, namespace="test", database="test")
        with surreal.connect() as connection:
            res = connection.signin('root', 'root')
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_authenticate(self):
        surreal = Surreal(URL, namespace="test", database="test")
        with surreal.connect() as connection:
            res = connection.signup(namespace='test', database='test', scope='user_scope',
                                    params={'user': 'john:doe', 'pass': '123456'})
            token = res.result
        with surreal.connect() as connection:
            connection.authenticate(token)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_invalidate(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.invalidate()
            self.assertFalse(res.is_error(), res)
            self.assertIsNone(res.result)
            res = connection.info()
            self.assertTrue(res.is_error(), res)

# TODO uncomment when bug fix
    # def test_let(self):
    #     surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
    #     with surreal.connect() as connection:
    #         res = connection.let("value151", "42")
    #         self.assertFalse(res.is_error(), res)
    #         self.assertIsNone(res.result)

    def test_unset(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.unset("value151")
            self.assertFalse(res.is_error(), res)
            self.assertIsNone(res.result)

    def test_query(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.query("SELECT * FROM type::table($tb);", {"tb": "article"})
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_query_simple(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.query("SELECT * FROM article;")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_select(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.select("article")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_select_with_id(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.select("author", "john")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_select_with_uuid_id(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_uuid()
            data = {"author": "Вася Ëлкин", "title": "øºRusr", "text": "text"}
            res = connection.create("article", {"id": uid, **data})
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            self.assertFalse(res.result == [])
            res = connection.select(f"article:⟨{uid}⟩")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, {"id": f"article:⟨{uid}⟩", **data})

    def test_create_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(22)
            res = connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            self.assertFalse(res.result == [])
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_create_one_with_id(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(25)
            res = connection.create("article", {"author": uid, "title": uid, "text": uid}, uid)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            self.assertFalse(res.result == [])
            res = connection.select("article", uid)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_insert_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(27)
            res = connection.insert("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            self.assertFalse(res.result == [])
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_insert_bulk(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(21)
            uid2 = get_random_series(33)
            res = connection.insert("article", [{"id": uid, "author": uid, "title": uid, "text": uid},
                                                {"id": uid2, "author": uid2, "title": uid2, "text": uid2}])
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            self.assertTrue(len(res.result) == 2)
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            res = connection.select(f"article:{uid2}")
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)

    def test_update_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(16)
            connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            res = connection.update("article", {"author": "new", "title": "new", "text": "new"}, uid)
            self.assertFalse(res.is_error(), res)
            self.assertFalse(len(res.result) == 1)
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result['author'], "new")

    def test_merge_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(19)
            connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            res = connection.merge("article", {"active": True}, uid)
            self.assertFalse(res.is_error(), res)
            self.assertFalse(len(res.result) == 1)
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result['author'], uid)
            self.assertEqual(res.result['active'], True)

    def test_patch_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(24)
            connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            res = connection.patch("article", [{"op": "replace", "path": "/active", "value": True}], uid)
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, {"id": f"article:{uid}", "author": uid, "title": uid, "text": uid,
                                          "active": True})
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result['author'], uid)
            self.assertEqual(res.result['active'], True)

    def test_patch_with_diff(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(24)
            connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid, "active": False})
            res = connection.patch("article", [{"op": "replace", "path": "/active", "value": True}], uid, True)
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, [{'op': 'replace', 'path': '/active', 'value': True}])
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result['author'], uid)
            self.assertEqual(res.result['active'], True)

    def test_delete_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(31)
            connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
            res = connection.delete("article", uid)
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, {"id": f"article:{uid}", "author": uid, "title": uid, "text": uid})
            res = connection.select(f"article:{uid}")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, None)

    def test_delete_all(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            uid = get_random_series(23)
            uid2 = get_random_series(33)
            connection.create("ws_article", {"id": uid, "author": uid, "title": uid, "text": uid})
            connection.create("ws_article", {"id": uid2, "author": uid2, "title": uid2, "text": uid2})
            res = connection.delete("ws_article")
            self.assertFalse(res.is_error(), res)
            res = connection.select(f"ws_article")
            self.assertFalse(res.is_error(), res)
            self.assertEqual(res.result, [])

    def test_live(self):
        a_list = []
        function = lambda mess: a_list.append(mess)
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.live("ws_article", callback=function)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            uid = get_random_series(27)
            opts = {"id": uid, "author": uid, "title": uid, "text": uid}
            connection.create("ws_article", opts)
            self.assertEqual(a_list[0]['result']['action'], 'CREATE')
            self.assertEqual(a_list[0]['result']['result'], {**opts, "id": f"ws_article:{uid}"})

    def test_live_and_kill(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.live("ws_article", callback=lambda x: None)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            token = res.result
            res = connection.kill(token)
            self.assertFalse(res.is_error(), res)
            self.assertIsNone(res.result)

    def test_live_with_diff(self):
        a_list = []
        function = lambda mess: a_list.append(mess)
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.live("ws_article", callback=function, return_diff=True)
            self.assertFalse(res.is_error(), res)
            self.assertIsNotNone(res.result)
            uid = get_random_series(14)
            opts = {"id": uid, "author": uid, "title": uid, "text": uid}
            connection.create("ws_article", opts)
            a_dict = {**opts, "id": f"ws_article:{uid}"}
            self.assertEqual(a_list[0]['result']['action'], 'CREATE')
            self.assertEqual(a_list[0]['result']['result'], [{'op': 'replace', 'path': '/', 'value': a_dict}])

    def test_live_two_queries(self):
        a_list = []
        function = lambda mess: a_list.append(mess)
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            connection.live("ws_article", callback=function)
            connection.live("ws_article2", callback=function)
            uid = get_random_series(27)
            opts = {"id": uid, "author": uid, "title": uid, "text": uid}
            connection.create("ws_article", opts)
            connection.create("ws_article2", opts)
            self.assertEqual(a_list[0]['result']['action'], 'CREATE')
            self.assertEqual(a_list[1]['result']['action'], 'CREATE')
            self.assertEqual(a_list[0]['result']['result'], {**opts, "id": f"ws_article:{uid}"})
            self.assertEqual(a_list[1]['result']['result'], {**opts, "id": f"ws_article2:{uid}"})


# TODO uncomment after bugfix
# def test_nesting_1000(self):
#     num = 0
#     prev = {"name":"first", "age":num, "inner":[]}
#     for _ in range(12):
#         num+=1
#         prev = {"name":get_random_series(10), "level":num, "inner":[prev]}
#
#     print(prev)
#     surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
#     with surreal.connect() as connection:
#         res = connection.create("ws_article", prev)
#         self.assertFalse(res.is_error())


if __name__ == '__main__':
    main()
