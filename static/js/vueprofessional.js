Vue.config.devtools = true;

var vue_record = new Vue({
  el: '#recordFields',
  data: {
    values: '',
    favorite: false,
  },

})

var vue_tabs = new Vue({
  el: '#vue_tabs',
  data: {
    user_type: 0,
  },

})
