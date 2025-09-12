/*************************************************************************************************
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements.  See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership.  The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied.  See the License for the
* specific language governing permissions and limitations
* under the License.
**************************************************************************************************/

import assert from 'assert';
import 'mocha';
import { doParse } from '../src/ConfigParser';

describe('ConfigParser', () => {
  describe('#doParse', () => {
    it('should return a parsed config', () => {
      const config = `
        key0       3000
        key1       "local host"
        key2       "a \\/.-_ 0"
        
        # comment
        key3       tcp://127.0.0.1:5555
        key4       172.31.25.184
        key5       starfall_database
        key6       password
        key7       /var/log/starfall-server.log
        key8       C:\\var\\log\\dott13-server.log
            key9         value       
        key10 1value
                   # this still a comment
        key11   value # comment
        key12 value#comment comment
        key13 [ key value]
        key14 [
           key value key2 value2
          # comment in a list
         key3 "value with spaces" ]
         key15 []
         key16 [
           
         ]
        key17 value17 key18 value18
      `;
      const expected = {
        key0: '3000',
        key1: 'local host',
        key2: 'a \\/.-_ 0',
        key3: 'tcp://127.0.0.1:5555',
        key4: '172.31.25.184',
        key5: 'starfall_database',
        key6: 'password',
        key7: '/var/log/starfall-server.log',
        key8: 'C:\\var\\log\\dott13-server.log',
        key9: 'value',
        key10: '1value',
        key11: 'value',
        key12: 'value',
        key13: { key: 'value'},
        key14: { key: 'value', key2: 'value2', key3: 'value with spaces' },
        key15: { },
        key16: { },
        key17: 'value17',
        key18: 'value18',
      };
      const result = doParse(config);
      assert.deepStrictEqual(result, expected);
    });
    it('should fail to parse a key with no value', () => {
      const config = 'appPort';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
    it('should fail to parse a key or value with spaces', () => {
      const config = 'key space value';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
    it('should fail to parse a quoted key spaces', () => {
      const config = '"key space" value';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
    it('should fail to parse a key that starts with a number', () => {
      const config = '0key value';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
    it('should fail to parse a key with the # symbol', () => {
      const config = 'key# #value#';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
    it('should fail to parse an array with just a key', () => {
      const config = 'key [ key ]';
      try {
        doParse(config);
        assert.fail();
      } catch {
        assert.ok(true);
      }
    });
  });
});
