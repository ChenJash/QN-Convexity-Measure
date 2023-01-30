<template>
  <div id="app">
    <QuestionNaire />
  </div>
</template>

<script>
import QuestionNaire from './components/Questionnaire.vue'

export default {
  name: 'App',
  components: {
    QuestionNaire
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
