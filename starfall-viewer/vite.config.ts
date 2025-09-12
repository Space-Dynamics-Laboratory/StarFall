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

import { fileURLToPath, URL } from 'node:url'

import { execSync } from 'node:child_process'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'

process.env.VITE_COMMIT_REF = execSync('git rev-parse --short HEAD || echo "[commit SHA not set]"').toString()
process.env.VITE_COMMIT_BRANCH = execSync('git rev-parse --abbrev-ref HEAD || echo "[git branch not set]"').toString()
process.env.VITE_BUILD_TIME = new Date().toISOString()
process.env.VITE_NEAREST_TAG = execSync('git describe --abbrev=0 || echo "[git tag not found]"').toString()

const cesiumSource = '../node_modules/cesium/Build/Cesium'
const cesiumBaseUrl = 'cesiumStatic'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    viteStaticCopy({
      targets: [
        { src: `${cesiumSource}/Workers`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/ThirdParty`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/Assets`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/Widgets`, dest: cesiumBaseUrl },
      ]
    }),
  ],
  define: {
    CESIUM_BASE_URL: JSON.stringify(`/${cesiumBaseUrl}`)
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
      }
    }
  },
  server: {
    port: 8080,
    proxy: {
      '^/api': {
        target: 'http://localhost:8443'
      },
      '^/socket.io': {
        target: 'http://localhost:8443',
        ws: true
      }
    }
  }
})
