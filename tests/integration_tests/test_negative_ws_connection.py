from unittest import TestCase, main

from py_surreal.errors import SurrealConnectionError, WebSocketConnectionError
from py_surreal.surreal import Surreal
from tests.integration_tests.utils import URL


class TestNegativeWebSocketConnection(TestCase):
    def test_connect_failed_on_invalid_url(self):
        surreal = Surreal("http://127.0.0.1:8001", namespace="test", database="test", credentials=('root', 'root'))
        with self.assertRaises(SurrealConnectionError):
            surreal.connect()

    def test_connect_failed_on_wrong_creds(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('wrong', 'wrong'))
        with self.assertRaises(WebSocketConnectionError):
            surreal.connect()

    def test_connect_failed_no_db(self):
        surreal = Surreal(URL, namespace="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.info()
            self.assertTrue(res.is_error(), res)
            self.assertTrue("Specify a database to use" in res.error["message"])

    def test_info_failed_no_ns(self):
        surreal = Surreal(URL, credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.info()
            self.assertTrue(res.is_error(), res)
            self.assertTrue("Specify a namespace to use" in res.error["message"])

    def test_authenticate_failed_wrong_token(self):
        surreal = Surreal(URL, namespace="test", database="test")
        with surreal.connect() as connection:
            res = connection.authenticate("wrong")
            self.assertTrue(res.is_error(), res)
            self.assertEqual(res.error['message'], 'There was a problem with authentication')
            self.assertEqual(res.error['code'], -32000)

    def test_signin_failed_root(self):
        surreal = Surreal(URL, namespace="test", database="test")
        with surreal.connect() as connection:
            res = connection.signin('wrong', 'wrong')
            self.assertTrue(res.is_error(), res)
            self.assertEqual(res.error['message'], 'There was a problem with authentication')
            self.assertEqual(res.error['code'], -32000)

    def test_kill(self):
        surreal = Surreal(URL, namespace="test", database="test", credentials=('root', 'root'))
        with surreal.connect() as connection:
            res = connection.kill("wrong")
            self.assertTrue(res.is_error(), res)
            self.assertEqual(res.error['message'],
                             "There was a problem with the database: Can not execute KILL statement using id '$id'")
            self.assertEqual(res.error['code'], -32000)




if __name__ == '__main__':
    main()
