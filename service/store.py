
from collections.abc import MutableMapping
from datetime import datetime, timedelta
from attr import validate
from neo4j import GraphDatabase
from pydantic import validate_arguments
from typing import Literal, Any
from enum import Enum

import json
import os
import urllib.parse

import pprint

from tapisservice.config import conf
from tapisservice.logs import get_logger
logger = get_logger(__name__)


class StoreMutexException(Exception):
    pass

class AbstractStore(MutableMapping):
    """A persitent dictionary."""

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        """Iterator for the keys."""
        pass

    def __len__(self):
        """Size of db."""
        pass

    def set_with_expiry(self, key, obj):
        """Set `key` to `obj` with automatic expiration of the configured seconds."""
        pass

    def update(self, key, field, value):
        "Atomic ``self[key][field] = value``."""
        pass

    def pop_field(self, key, field):
        "Atomic pop ``self[key][field]``."""
        pass

    def update_subfield(self, key, field1, field2, value):
        "Atomic ``self[key][field1][field2] = value``."""
        pass

    def getset(self, key, value):
        "Atomically: ``self[key] = value`` and return previous ``self[key]``."
        pass

    def mutex_acquire(self, key):
        """Try to use key as a mutex.
        Raise StoreMutexException if not available.
        """

        busy = self.getset(key, True)
        if busy:
            raise StoreMutexException(f'{key} is busy')

    def mutex_release(self, key):
        self[key] = False


class NeoStore(AbstractStore):
    """
    Note: pop_fromlist, append_tolist, and within_transaction were removed from the Redis
    store functions as they weren't necessary, don't work, or don't work in Mongo.
    Creates an abaco `store` which maps to a single mongo
    collection within some database.
    :param host: the IP address of the mongo server.
    :param port: port of the mongo server.
    :param database: the mongo database to use for abaco.
    :param db: an integer mapping to a mongo collection within the
    :param auth_db: For sites. This is where we should check auth. Should be abaco_{site}. 
        Default is usually admin, but Mongo will take care of that for us.
    mongo database.

    :return:
    """

    # Most of this described here: neo4j.com/docs/api/python-driver/current/api.html#driver
    @validate_arguments
    def __init__(self,
                 scheme: Literal['neo4j', 'bolt'] = 'neo4j',
                 host: str | None = None,
                 port: int | None = None,
                 user: str | None = None,
                 passw: str | None = None,
                 config: dict[str, str] = {}):
        
        logger.info(f"Top of NeoStore __init__().")

        if user and passw:
            logger.info(f"Using user {user} and pass: ***")
            auth = (urllib.parse.quote_plus(user), urllib.parse.quote_plus(passw))
        elif user or passw:
            logger.info("Got user or pass. Using no auth with neo.")
            auth = None
        else:
            logger.info("Did not get user or pass. Using no auth with neo")
            auth = None

        neo_uri = f'{scheme}://{host}:{port}'
        logger.info(f"Using neo_uri: {neo_uri}, with config: {config}")

        self.neo = GraphDatabase.driver(neo_uri, auth=auth, **config)

    class resultFns(Enum):
        keys = "keys"
        consume = "consume"
        single = "single"
        peek = "peek"
        graph = "graph"
        value = "value"
        values = "values"
        data = "data"

    @validate_arguments
    def run(self,
            query: str,
            parameters: dict[str, Any] | None = None,
            res_fn: resultFns = "data",
            res_key: str | int | list | None = None,
            kwparameters: dict[str, str] = {}
            ) -> dict[str, str] | str:

        logger.info("Top of NeoStore run().")
        logger.debug(f"NeoStore.run() using res_fn: {res_fn}")

        if res_key is not None:
            res_fns_with_keys = ["value", "values", "data"]
            if res_fn not in res_fns_with_keys:
                msg = (f"NeoStore: res_key: {res_key}; result_fn: {res_fn}; res_key only used by {res_fns_with_keys}")
                logger.warning(msg)
                raise ValueError(msg)
            if isinstance(res_key, list) and res_fn in "value":
                msg = (f"NeoStore: type(res_key) = list. res_fn, value, accepts str or int only")
                logger.warning(msg)
                raise ValueError(msg)
            if res_fn in ["values", "data"]:
                # Put single ints and strs into a list so later code gets the expected list.
                if not isinstance(res_key, list):
                    res_key = [res_key]
        elif res_fn in ["values", "data"]:
            res_key = []
                
        # Now run the actual session and get the result
        with self.neo.session() as session:
            result = session.run(query, parameters, **kwparameters)

            if res_fn == 'single':
                return result.single()

            if res_fn == 'keys':
                return result.keys()

            if res_fn == 'consume':
                return result.consume()

            if res_fn == 'peek':
                return result.peek()

            if res_fn == 'graph':
                return result.graph()

            if res_fn == 'value':
                return result.value(key=res_key)

            if res_fn == 'values':
                return result.values(*res_key)

            if res_fn == 'data':
                return result.data(*res_key)

        raise KeyError("Something has gone very bad.")
            
    # def __getitem__(self, fields):
    #     """
    #     Simple match
    #     Gets and returns 'self[key]' or 'self[key][field1][field2][...]' as a dictionary
    #     """
        
    #     query = "match (n: $field) return n"
    #     parameters = {'field': fields}

    #     try:
    #         self.run(query, parameters)
    #     except Exception as e:
    #         print(e)
        



        
    #     key, _, subscripts = self._process_inputs(fields)
    #     result = self._db.find_one(
    #         {'_id': key},
    #         projection={'_id': False})
    #     if result == None:
    #         raise KeyError(f"'_id' of '{key}' not found")
    #     try:
    #         return eval('result' + subscripts)
    #     except KeyError:
    #         raise KeyError(f"Subscript of {subscripts} does not exists in document of '_id' {key}")


    # def __setitem__(self, fields, value):
    #     """
    #     Atomically does either:
    #     Sets 'self[key] = value' or sets 'self[key][field1][field2][...] = value'
    #     """
    #     key, dots, _ = self._process_inputs(fields)
    #     try:
    #         if isinstance(fields, str) and isinstance(value, dict):
    #             result = self._db.update_one(
    #                 filter={'_id': key},
    #                 update={'$set': value},
    #                 upsert=True)
    #         else:
    #             result = self._db.update_one(
    #                 filter={'_id': key},
    #                 update={'$set': {dots: value}},
    #                 upsert=True)
    #     except WriteError:
    #         raise WriteError(
    #             "Likely due to trying to set a subfield of a field that does not exists." +
    #             "\n Try setting a dict rather than a value. Ex. store['id_key', 'key', 'field'] = {'subfield': 'value'}")
    #     if result.raw_result['nModified'] == 0:
    #         if not 'upserted' in result.raw_result:
    #             logger.debug(f'Field not modified, old value likely the same as new. Key: {key}, Fields: {dots}, Value: {value}')

    # def __delitem__(self, fields):
    #     """
    #     Atomically does either:
    #     Deletes 'self[key]'
    #     Unsets 'self[key][field1][field2][...]'
    #     """
    #     key, dots, subscripts = self._process_inputs(fields)
    #     if not subscripts:
    #         result = self._db.delete_one({'_id': key})
    #         if result.raw_result['n'] == 0:
    #             logger.debug(f"No document with '_id' found. Key:{key}, Fields:{dots}")
    #     else:
    #         result = self._db.update_one(
    #             filter={'_id': key},
    #             update={'$unset': {f'{dots}': ''}})
    #         if result.raw_result['nModified'] == 0:
    #             logger.debug(f"Doc with specified fields not found. Key:{key}, Fields:{dots}")

    # def __iter__(self):
    #     for cursor in self._db.find():
    #         yield cursor['_id']
    #     # return self._db.scan_iter()

    # def __len__(self):
    #     """
    #     Returns the estimated document count of a store to give length
    #     We don't use '.count_documents()' as it's O(N) versus O(1) of estimated
    #     Length for a document or subdocument comes from len(store['key']['field1'][...]) using dict len()
    #     """
    #     return self._db.estimated_document_count()

    # def __repr__(self):
    #     """
    #     Returns a pretty string of the entire store with '_id' visible for developer use
    #     """
    #     return pprint.pformat(list(self._db.find()))

    # def _process_inputs(self, fields):
    #     """
    #     Takes in fields and returns the key corresponding with '_id', dot notation
    #     for getting to a specific field in a Mongo query/filter (ex. 'field1.field2.field3.field4')
    #     and the subscript notation for returning a specified field from a result dictionary
    #     (ex. `['field1']['field2']['field3']['field4']`)
    #     """
    #     if isinstance(fields, str):
    #         key = dots = fields
    #         subscripts = ''
    #     elif isinstance(fields, list) and len(fields) == 1:
    #         key = dots = fields[0]
    #         subscripts = ''
    #     else:
    #         key = fields[0]
    #         dots = '.'.join(fields[1:])
    #         subscripts = "['" + "']['".join(fields[1:]) + "']"
    #     return key, dots, subscripts

    # def _prepset(self, value):
    #     if type(value) is bytes:
    #         return value.decode('utf-8')
    #     return value

    # def pop_field(self, fields):
    #     """
    #     Atomically pops 'self[key] = value' or 'self[key][field1][field2][...] = value'
    #     """
    #     key, dots, subscripts = self._process_inputs(fields)
    #     if not subscripts:
    #         result = self._db.find_one(
    #             {'_id': key},
    #             projection={'_id': False})
    #         if result == None:
    #             raise KeyError(f"'_id' of '{key}' not found")
    #         del_result = self._db.delete_one({'_id': key})
    #         if del_result.raw_result['n'] == 0:
    #             raise KeyError(f"No document deleted")
    #         return result
    #     else:
    #         result = self._db.find_one_and_update(
    #             filter={'_id': key},
    #             update={'$unset': {dots: ''}})
    #         try:
    #             return eval('result' + subscripts)
    #         except KeyError:
    #             raise KeyError(f"Subscript of {subscripts} does not exist in document of '_id' {key}")

    # def set_with_expiry(self, fields, value, log_ex):
    #     """
    #     Atomically:
    #     Sets 'self[key] = value' or 'self[key][field1][field2][...] = value'
    #     Creates 'exp' subdocument in document root with current time for use with MongoDB TTL expiration index
    #     Note: MongoDB TTL checks every 60 secs to delete files
    #     """
    #     key, dots, _ = self._process_inputs(fields)
    #     time_to_expire = datetime.utcnow() + timedelta(seconds=log_ex)
    #     logger.debug(f"Set with expiry setting time to expire to : {time_to_expire} ")
    #     if len(fields) == 1 and isinstance(value, dict):
    #         result = self._db.update_one(
    #             filter={'_id': key},
    #             update={'$set': {'exp': time_to_expire},
    #                     '$set': value},
    #             upsert=True)
    #     else:
    #         result = self._db.update_one(
    #             filter={'_id': key},
    #             update={'$set': {'exp': time_to_expire, dots: self._prepset(value)}},
    #             upsert=True)

    # def full_update(self, key, value, upsert=False):
    #     result = self._db.update_one(key, value, upsert)
    #     return result

    # def getset(self, fields, value):
    #     """
    #     Atomically does either:
    #     Sets 'self[key] = value' and returns previous 'self[key]'
    #     Sets 'self[key][field1][field2][...] = value' and returns previous 'self[key][field1][field2][...]'
    #     """
    #     key, dots, subscripts = self._process_inputs(fields)
    #     result = self._db.find_one_and_update(
    #         filter={'_id': key, dots: {'$exists': True}},
    #         update={'$set': {dots: value}})
    #     if result == None:
    #         raise KeyError(f"Subscript of {subscripts} does not exist in document of '_id' {key}")   
    #     try:
    #         if len(fields) == 1:
    #             return eval(f"result['{key}']")
    #         else:
    #             return eval('result' + subscripts)
    #     except KeyError:
    #         raise KeyError(f"Subscript of {subscripts} does not exist in document of '_id' {key}")

    # def items(self, filter_inp=None, proj_inp={'_id': False}):
    #     " Either returns all with no inputs, or filters when given filters"
    #     return list(self._db.find(
    #         filter=filter_inp,
    #         projection=proj_inp))

    # def add_if_empty(self, fields, value):
    #     """
    #     Atomically:
    #     Sets 'self[key] = value' or 'self[key][field1][field2][...] = value'
    #     Only if the specified key/field(s) combo does not exist or is empty
    #     Returns the value if it was added; otherwise, returns None
    #     Note: Will not override a field set to a value in order to create a subfield
    #     """
    #     key, dots, _ = self._process_inputs(fields)
    #     try:
    #         if len(fields) == 1 and isinstance(value, dict):
    #             result = self._db.update_one(
    #                 filter={'_id': key},
    #                 update={'$setOnInsert': value},
    #                 upsert=True)
    #             if result.upserted_id:
    #                 return key
    #         elif len(fields) == 1:
    #             result = self._db.update_one(
    #                 filter={'_id': key},
    #                 update={'$setOnInsert': {dots: value}},
    #                 upsert=True)
    #             if result.upserted_id:
    #                 return key
    #         else:
    #             try:
    #                 result = self._db.update_one(
    #                     filter={'_id': key},
    #                     update={'$setOnInsert': {dots: value}},
    #                     upsert=True)
    #                 if result.upserted_id:
    #                     return fields
    #             except WriteError:
    #                 print("Likely due to trying to set a subfield of a field that is already set to one value")
    #                 pass
    #         return None
    #     except DuplicateKeyError:
    #         return None
    
    # def aggregate(self, pipeline, options = None):
    #     return self._db.aggregate(pipeline, options)

    # def create_index(self, index_list):
    #     return self._db.create_index(index_list)