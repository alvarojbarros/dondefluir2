Vue.config.devtools = true;

var vue_dashboard = new Vue({
  el: '#dashboard',
  data: {
    currentdate:  '',
    user_type: '',
  },

})

var vue_dashboard_ntf = new Vue({
  el: '#notifications',
  data: {
    news: 'No hay nuevas notificaciones',
    values: '',
    cnt: 0,
  },

})
