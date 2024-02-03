from pathlib import Path
from unittest import TestCase, main

from tests.integration_tests.utils import URL, WS_URL, get_random_series
from surrealist.utils import get_uuid
from surrealist import Surreal


class TestSurreal(TestCase):
    def test_health(self):
        surreal = Surreal(URL)
        self.assertEqual("OK", surreal.health())

    def test_status(self):
        surreal = Surreal(URL)
        self.assertEqual("OK", surreal.status())

    def test_is_ready(self):
        surreal = Surreal(URL)
        self.assertEqual(True, surreal.is_ready())

    def test_version(self):
        surreal = Surreal(URL)
        result = surreal.version()
        self.assertTrue("surrealdb-1." in result, result)

    def test_health_ws(self):
        surreal = Surreal(WS_URL)
        self.assertEqual("OK", surreal.health())

    def test_status_ws(self):
        surreal = Surreal(WS_URL)
        self.assertEqual("OK", surreal.status())

    def test_is_ready_ws(self):
        surreal = Surreal(WS_URL)
        self.assertEqual(True, surreal.is_ready())

    def test_version_ws(self):
        surreal = Surreal(WS_URL)
        result = surreal.version()
        self.assertTrue("surrealdb-1." in result, result)


class TestHttpConnection(TestCase):

    def test_is_ready_empty(self):
        db = Surreal(URL, use_http=True, timeout=1)
        with db.connect() as connection:
            self.assertTrue(connection._is_ready())

    def test_is_ready_full(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        self.assertTrue(connection._is_ready())

    def test_select_one(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"id": "exists", "author": uid, "title": uid, "text": uid})
        res = connection.select("article", "exists")
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], "article:exists", res)

    def test_select_all(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
        res = connection.select("article")
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")

    def test_select_one_non_existent(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.select("article", "not_exists")
        self.assertTrue(res.result == [])
        self.assertEqual(res.status, "OK")

    def test_select_one_non_existent_table(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.select("not_exists", "not_exists")
        self.assertTrue(res.result == [])
        self.assertEqual(res.status, "OK")

    def test_create_one(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        res = connection.create("article", {"id": uid, "author": uid, "title": uid, "text": uid})
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        res = connection.select("article", uid)
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)

    def test_create_one_with_id(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        res = connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        res = connection.select("article", uid)
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)

    def test_create_one_no_id(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        res = connection.create("article", {"author": uid, "title": uid, "text": uid})
        self.assertTrue(res.result != [])
        self.assertEqual(res.status, "OK")
        self.assertTrue(res.result[0]["id"] != f"article:⟨{uid}⟩", res)

    def test_update_one(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.update("article", {"author": "inserted"}, record_id=uid)
        self.assertTrue(len(res.result) == 1)
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        self.assertEqual(res.result[0]["author"], "inserted", res)
        res = connection.select("article", uid)
        self.assertEqual(res.status, "OK")
        self.assertEqual(len(res.result[0]), 2, res)
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        self.assertEqual(res.result[0]["author"], "inserted", res)

    def test_update_z_all(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.update("article", {"author": "inserted_all", "title": uid, "text": uid})
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")
        self.assertTrue(all(e["author"] == "inserted_all" for e in res.result))

    def test_merge_one(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.merge("article", {"new_field": "merge"}, record_id=uid)
        self.assertTrue(len(res.result) == 1)
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        self.assertEqual(res.result[0]["new_field"], "merge", res)
        res = connection.select("article", uid)
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        self.assertEqual(res.result[0]["new_field"], "merge", res)

    def test_merge_z_all(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.merge("article", {"all_field": "merge"})
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")
        self.assertTrue(all(e["all_field"] == "merge" for e in res.result))

    def test_query_success(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.query("INFO FOR ROOT;")
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")

    def test_query_success_with_vars(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.query("INFO FOR ROOT;", variables={})
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")

    def test_delete_one(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.delete("article", record_id=uid)
        self.assertTrue(len(res.result) == 1)
        self.assertEqual(res.status, "OK")
        self.assertEqual(res.result[0]["id"], f"article:⟨{uid}⟩", res)
        res = connection.select("article", uid)
        self.assertEqual(res.status, "OK")
        self.assertTrue(len(res.result) == 0)

    def test_z_delete_all(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        uid = get_uuid()
        connection.create("article", {"author": uid, "title": uid, "text": uid}, record_id=uid)
        res = connection.delete("article")
        self.assertTrue(len(res.result) > 1)
        self.assertEqual(res.status, "OK")
        res = connection.select("article")
        self.assertEqual(res.status, "OK")
        self.assertTrue(len(res.result) == 0)

    def test_export(self):
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.export()
        # with open("import.surql", "wt", encoding="UTF-8") as file:
        #     file.write(res)
        self.assertTrue("article" in res)
        self.assertTrue("user_db" in res)
        # self.assertTrue("user_ns" in res)
        self.assertTrue("user_scope" in res)
        self.assertTrue("OPTION IMPORT;" in res)

    def test_import(self):
        file_path = Path(__file__).parent / "import.surql"
        db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        connection = db.connect()
        res = connection.import_data(file_path)
        self.assertEqual(res.result, None)
        self.assertEqual(res.status, "OK")

    def test_signin(self):
        params = (
            'root', 'user_db', 'user_ns'
        )
        for type_ in params:
            with self.subTest(f"sign_in as {type_}"):
                db = Surreal(URL, use_http=True)
                connection = db.connect()
                res = connection.signin(type_, type_, namespace='test', database='test')
                self.assertEqual(res.code, 200)
                self.assertEqual(res.result, "Authentication succeeded")

    def test_signup(self):
        db = Surreal(URL, 'test', 'test', use_http=True)
        connection = db.connect()
        res = connection.signup(namespace='test', database='test', scope='user_scope',
                                params={'user': 'john:doe', 'pass': '123456'})
        self.assertEqual(res.code, 200)
        self.assertEqual(res.result, "Authentication succeeded")

    # TODO test for let and unset when fix bug https://github.com/surrealdb/surrealdb/issues/3418
    # def test_let(self):
    #     db = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True, log_level="DEBUG")
    #     connection = db.connect()
    #     res = connection.let("name", "LEX")
    #     self.assertEqual(res.result, None)
    #     self.assertEqual(res.status, "OK")

    def test_use(self):
        db = Surreal(URL, credentials=("root", "root"), use_http=True)
        with db.connect() as connection:
            res = connection.use(namespace='test', database='test')
            self.assertFalse(res.is_error())
            res = connection.select("article", "any")
            self.assertFalse(res.is_error())

    def test_insert_one(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'), use_http=True)
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
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'), use_http=True)
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


if __name__ == '__main__':
    main()
