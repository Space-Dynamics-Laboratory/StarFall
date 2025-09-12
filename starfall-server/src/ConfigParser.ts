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

import fs from 'fs';
import { Parser } from 'jison';
import Lexer from 'lex';

type config = { [key: string]: string; } | Record<string, never>; 

const lexer = new Lexer;
lexer
  .addRule(/^/g, function(this: typeof lexer) { this.yylineno = 0; })
  .addRule(/\r?\n/g, function(this: typeof lexer) {
    ++this.yylineno;
    return;
  })
  .addRule(/\s+/, function() { return; })
  .addRule(/#.*/, function() { return; })
  .addRule(/\[/, function() { return '['; })
  .addRule(/\]/, function() { return ']'; })
  .addRule(/[a-zA-Z]\w*/, function(this: typeof lexer, lexeme: string) {
    this.yytext = lexeme;
    return 'SIMPLE_WORD';
  })
  .addRule(/[\w:\\/.-]+/, function(this: typeof lexer, lexeme: string) {
    this.yytext = lexeme;
    return 'WORD';
  })
  .addRule(/"[^"\n]*"/, function(this: typeof lexer, lexeme: string) {
    this.yytext = lexeme.slice(1, -1);
    return 'QUOTED_WORD';
  })
  .addRule(/$/, function() {
    return 'EOF';
  });

const grammar = {
  bnf: {
    'config': [
      ['key_value_list EOF', 'return $1']
    ],
    'key_value_list': [
      ['key value key_value_list', '$$ = {[$1]: $2, ...$3}'],
      ['key value', '$$ = {[$1]: $2}']
    ],
    'key': [
      ['SIMPLE_WORD', '$$ = $1']
    ],
    'value': [
      ['SIMPLE_WORD', '$$ = $1'],
      ['WORD', '$$ = $1'],
      ['QUOTED_WORD', '$$ = $1'],
      ['array', '$$ = $1']
    ],
    'array': [
      ['[ key_value_list ]', '$$ = $2'],
      ['[ ]', '$$ = { }']
    ]
  }
};

export const doParse = function(input: string): config {
  const parser = new Parser(grammar);
  parser.lexer = lexer;
  return parser.parse(input);
};

export const parse = function(configFilePath: string): config {
  const input = fs.readFileSync(configFilePath).toString();
  return doParse(input);
};