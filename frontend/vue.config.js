const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: "http://localhost:8000/",
        changeOrigin: true,
        // ws: false,
        pathRewrite:{
          '^api': ''
        },
      }
    },
    host: '0.0.0.0',
    port: 11111,
    client: {
      webSocketURL: 'ws://0.0.0.0:11111/ws',
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  }
})
