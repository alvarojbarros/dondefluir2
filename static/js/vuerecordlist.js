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
  components: {
    // <my-component> will only be available in parent's template
    'record-row': RecordRow,
  }

})

var RecordRow = {
  props: ['record','text','class_name','user_type','_Skip2'],
  template: '<a href="#" v-on:click="call_onclick">{{text}}</a>',
  methods: {
    call_onclick: function () {
        if (this.class_name=='Event') {showEvent(this.record.id);}
        if (this.class_name=='Service') {showService(this.record.id);}
        if (this.class_name=='UserService') {showUserService(this.record.id);}
        if (this.class_name=='User') {showUser(this.record.id);}
        if (this.class_name=='Activity') {showActivity(this.record.id);}
        if (this.class_name=='Company') {
            if (this.user_type==3){
                showCompanyProfile(this.record.id,this.record.Name);
            }else{
                showCompany(this.record.id);
            }
        }
        if (this.class_name=='Notification') {
            if (this.record.Status.substring(0, 1)=='N'){showNotification(this.record.id,true)}
            else if (this.record.Status.substring(0, 1)=='L'){showNotification(this.record.id)}
        }

    }
  },
}

