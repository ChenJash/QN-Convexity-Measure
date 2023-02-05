const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: "http://localhost:5000/",
        changeOrigin: true,
        ws: false,
        pathRewrite:{
          '^api': ''
        },
      }
    },
    host: '0.0.0.0',
    port: 8080,
    client: {
      webSocketURL: 'ws://127.0.0.1:8081/ws',
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  }
})
