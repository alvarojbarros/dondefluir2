Vue.config.devtools = true;

var vue_report = new Vue({
  el: '#filters',
  data: {
    filters: [],
    htmlView: [],
  },

})

var vue_report_result = new Vue({
  el: '#result',
  data: {
    Columns: [],
    Rows: [],
  },

})
