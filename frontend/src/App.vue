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

.loading {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: gray;
    opacity: 0.8;
    display: flex;
    justify-content: center;
    align-items: center;
}

.loading-svg {
    position: absolute;
    left: 50%;
    top: 45%;
}

.circle-path {
  transform: translate(15px,15px);
/*   transform-origin: center; */
  animation: rotate_arrow 2s infinite;
}

@keyframes rotate_arrow {
  from {
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
    }
    99.999% {
        -webkit-transform: rotate(359deg);
        transform: rotate(359deg);
    }
    to {
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
    }
}


</style>
