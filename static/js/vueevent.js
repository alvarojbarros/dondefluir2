Vue.config.devtools = true;

var vue_event = new Vue({
  el: '#event_record',
  data: {
    events: '',
    ProfName: '',
  },
  methods: {
    getScript: function(id,params) {
			return $(
				'<script src="https://s3-us-west-2.amazonaws.com/epayco/v1.0/checkoutEpayco.js" ' +
				'    class="epayco-button" ' +
				'    data-epayco-key="' + params.KeyPayco + '"' +
				'    data-epayco-amount="' + params.Price + '"' +
				'    data-epayco-name="Donde Fluir ' + params.Comment + '"' +
				'    data-epayco-description="' + params.Description + '"' +
				'    data-epayco-currency="cop" ' +
				'    data-epayco-country="co" ' +
				'    data-epayco-test="false" ' +
				'    data-epayco-response="'+ window.location.href.replace('#','') + 'epayco/' + id + '"' +
				'    data-epayco-confirmation="https://ejemplo.com/confirmacion" > <' + '/script>')
		}
	},

	mounted: function () {
		for (k in this.events){
			$(this.$refs['form' + k]).html(this.getScript(k,this.events[k][0]))
		}
	},
	updated: function () {
		for (k in this.events){
			$(this.$refs['form' + k]).html(this.getScript(k,this.events[k][0]))
		}
	}

})
