Vue.config.devtools = true;

var vue_recordlist = new Vue({
  el: '#record_list',
  data: {
    values: [],
    filters: [],
    filtersNames: [],
    table: '',
    user_id: '',
    user_type: '',
    columns: null,
    table: [],
  },
})
