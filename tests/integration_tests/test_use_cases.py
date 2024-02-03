import threading
from unittest import TestCase, main

from py_surreal.connections import Connection
from py_surreal.errors import OperationOnClosedConnectionError
from py_surreal.surreal import Surreal
from tests.integration_tests.utils import URL, get_random_series


class TestUseCases(TestCase):
    connections = []

    @classmethod
    def setUpClass(cls) -> None:
        surreal_ws = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=False)
        surreal_http = Surreal(URL, 'test', 'test', ('root', 'root'), use_http=True)
        con_ws = surreal_ws.connect()
        con_ws.close()
        con_http = surreal_http.connect()
        con_http.close()
        TestUseCases.connections.append(con_ws)
        TestUseCases.connections.append(con_http)

    def test_raise_after_close(self):
        """
        We check here is_connected id False after close, and using method after it raise error
        """
        params = (
            (True, "signin", ["root", "root"]),
            (True, "signup", ["ns", "db", "scope"]),
            (True, "select", ["some"]),
            (True, "create", ["some", {}]),
            (True, "update", ["some", {}]),
            (True, "delete", ["some"]),
            (True, "merge", ["some", {}]),
            (True, "query", ["some"]),
            (True, "import_data", ["some"]),
            (True, "export", []),
            (True, "ml_import", ["some"]),
            (True, "ml_export", ["some", "some"]),
            (True, "let", ["some", "some"]),
            (True, "unset", ["some"]),
            (True, "use", ["some", "some"]),
            (False, "signin", ["root", "root"]),
            (False, "signup", ["ns", "db", "scope"]),
            (False, "select", ["some"]),
            (False, "create", ["some", {}]),
            (False, "update", ["some", {}]),
            (False, "delete", ["some"]),
            (False, "merge", ["some", {}]),
            (False, "query", ["some"]),
            (False, "let", ["some", "some"]),
            (False, "unset", ["some"]),
            (False, "use", ["some", "some"]),
            (False, "patch", ["some", {}]),
            (False, "insert", ["some", {}]),
            (False, "info", []),
            (False, "invalidate", []),
            (False, "authenticate", ["token"]),
            (False, "live", ["token", print]),
            (False, "kill", ["token"]),
        )
        for use_http, method_name, args in params:
            with self.subTest(f"use method {method_name} on connection use_http {use_http}"):
                connection: Connection = TestUseCases.connections[use_http]
                self.assertFalse(connection.is_connected())
                with self.assertRaises(OperationOnClosedConnectionError):
                    getattr(connection, method_name)(*args)

    def test_live_with_two_connections(self):
        """
        We test here live query is linked to one connection only

        """
        a_list = []
        function = lambda mess: a_list.append(mess)
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            with surreal.connect() as connection2:
                res = connection.live("ws_article", callback=function)
                self.assertFalse(res.is_error(), res)
                uid = get_random_series(27)
                opts = {"id": uid, "author": uid, "title": uid, "text": uid}
                connection.create("ws_article", opts)
                self.assertEqual(a_list[0]['result']['action'], 'CREATE')
                self.assertEqual(connection2._client._messages, {})
                self.assertEqual(connection2._client._callbacks, {})

    def test_select_in_threads(self):
        """
        We test here using one connection by two threads
        :return:
        """
        first = []
        second = []
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            thread1 = threading.Thread(target=lambda: first.append(connection.select("user")), daemon=True)
            thread2 = threading.Thread(target=lambda: second.append(connection.select("article")), daemon=True)
            thread1.start()
            thread2.start()
            thread1.join(3)
            thread2.join(3)
        self.assertNotEqual(first, [])
        self.assertNotEqual(second, [])
        self.assertFalse(first[0].is_error())
        self.assertFalse(second[0].is_error())
        self.assertNotEqual(first, second)


if __name__ == '__main__':
    main()
