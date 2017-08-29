Vue.config.devtools = true;


Vue.component('activity-payment',{
  props: ['paid','id','cust','company'],
  template: '' +
            '<div v-if="paid" id="form-activity">' +
            '  <p style="color: green"><b><i>NO has pagado por este curso</i></b></p>' +
            '  <form ref="form-activity">' +
            '  </form>' +
            '</div>' +
            '<div v-else>' +
            '  <p style="color: green"><b><i>Ya has realizado tu pago</i></b></p>' +
            '</div>',

  mounted: function () {
    console.log(1)
    $.getJSON($SCRIPT_ROOT + '/_get_payment', {'activityId': this.id, 'userId': this.cust,'companyId': this.company}
        , function(data) {
        console.log(    data)
        Vue.set(this,'paid',data.result.res)
        if (!data.result.res){
            Vue.set(vue_activity,'KeyPayco',data.result.KeyPayco)
        }
    });
   }

})

